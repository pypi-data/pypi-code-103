import asyncio
import threading

from .._content_provider import ContentProviderLayer, emit_event
from .._content_provider_factory import get_api_config, get_base_url, get_url
from ...core.session import get_valid_session
from ...delivery.data.endpoint import RequestMethod
from ...errors import EndpointError
from ...tools import urljoin

DELAY_BEFORE_FIRST_GET_ASYNC_OPERATION = 0.3
DELAY_BETWEEN_TWO_GET_ASYNC_OPERATION = 5


class IPAContentProviderLayer(ContentProviderLayer):
    def __init__(self, content_type, **kwargs):
        super().__init__(content_type, **kwargs)
        self._lock_request = threading.Lock()
        self._async_url = None

    async def get_data_async(self, session=None, on_response=None, async_mode=None):
        session = get_valid_session(session)
        content_type = self._content_type
        config = session.config
        self._async_url = get_url(content_type, config, request_mode="async")

        if async_mode:
            if self._async_url:
                response = await self._get_data_with_async_mode(
                    session, config, content_type
                )
                on_response and emit_event(on_response, response, self, session)

            else:
                raise AttributeError(
                    f"Asynchronous endpoint is not available for this content provider"
                )

        else:
            response = await super().get_data_async(session, on_response)

        return response

    async def _get_data_with_async_mode(self, session, config, content_type):

        _base_url = get_base_url(content_type, config)
        api_config = get_api_config(content_type, config)

        _operation_url = urljoin(_base_url, api_config.get("endpoints.async-operation"))
        _resource_url = urljoin(_base_url, api_config.get("endpoints.async-resource"))

        _delay_before_first_get_operation = api_config.get(
            "delay-before-first-get-async-operation",
            DELAY_BEFORE_FIRST_GET_ASYNC_OPERATION,
        )
        _delay_between_two_get_operation = api_config.get(
            "delay-between-two-get-async-operation",
            DELAY_BETWEEN_TWO_GET_ASYNC_OPERATION,
        )

        if not self._async_url:
            raise AttributeError(
                f"Asynchronous endpoint is not available for this content provider"
            )

        initial_response = self._provider.get_data(
            session, self._async_url, **self._kwargs
        )

        # At this step, normal response should have 202 status code,
        # "Accepted" error message and location header
        status_code = initial_response.status.get("http_status_code")
        if status_code != 202:
            msg_error = initial_response.error_message
            msg_error = (
                f"Async IPA response "
                f"status code {status_code}|{msg_error} != 202|Accepted"
            )
            session.error(msg_error)
            initial_response.error_message = msg_error
            initial_response.is_success = False
            return initial_response

        location = initial_response.http_headers.get("location")
        if location:
            operation_id = location.rsplit("/", 1)[-1]
        else:
            msg_error_location = (
                "IPA Asynchronous request operation failed, "
                "response doesn't contain location."
            )
            session.error(msg_error_location)
            initial_response.error_message = msg_error_location
            initial_response.is_success = False
            return initial_response

        operation_result = None
        loop_retrieving = True
        while loop_retrieving:
            # wait before requesting operation status
            session.run_until_complete(asyncio.sleep(_delay_before_first_get_operation))
            # while request operation not succeeded or not failed, request operation

            operation_result = await self._request_async_ipa(
                session, "operation", _operation_url, operation_id
            )

            status_code = operation_result.status.get("http_status_code")

            if status_code != 200:
                # operation status should be 200, otherwise,
                # it failed, then return response as an error
                return operation_result

            status_text = operation_result.data.raw.get("status")
            if status_text in ["failed", "succeeded"]:
                # request succeeded or failed, in both cases,
                # stop to wait and retrieve result
                loop_retrieving = False
            else:
                # wait for 5 sec before next request
                session.run_until_complete(
                    asyncio.sleep(_delay_between_two_get_operation)
                )

        # request resource
        resource_location = operation_result.data.raw.get("resourceLocation")
        if resource_location:
            resource_id = resource_location.rsplit("/", 1)[-1]
            response = await self._request_async_ipa(
                session, "resource", _resource_url, resource_id
            )
            return response
        else:
            msg_error_resource = (
                "IPA Asynchronous request resource failed, "
                "operation response doesn't contain resource location."
            )
            session.error(msg_error_resource)
            raise EndpointError(-1, msg_error_resource)

    async def _request_async_ipa(self, session, ipa_endpoint_name, url, request_id):
        with self._lock_request:
            url_id = urljoin(url, request_id)
            session.log(10, f"Request {ipa_endpoint_name} :\n {url_id}")
            _result = await self._provider.get_data_async(
                session, url_id, method=RequestMethod.GET, **self._kwargs
            )
            return _result
