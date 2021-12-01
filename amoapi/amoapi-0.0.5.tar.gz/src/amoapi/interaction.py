import logging
import time
from typing import Tuple
from requests import Session
from requests import ConnectionError
from .exceptions import *
from .filters import Filter

logger = logging.getLogger(__name__)


class BaseInteraction:
    _default_headers = {
        "User-Agent": "amocrm-py/v2",
    }

    def __init__(self, token_manager, headers=_default_headers):

        self._token_manager = token_manager
        self._session = Session()
        self._default_headers = headers
        self.time_at_last_request = time.time()

    def get_headers(self):
        headers = {}
        headers.update(self._default_headers)
        headers.update(self._get_auth_headers())
        return headers

    def _get_auth_headers(self):
        return {"Authorization": "Bearer " + self._token_manager.get_access_token()}

    def _get_url(self, path):
        return "https://{subdomain}.amocrm.ru/api/{path}".format(subdomain=self._token_manager.subdomain, path=path)

    def _request(self, method, path, data=None, params=None, headers=None):

        headers = headers or {}
        headers.update(self.get_headers())
        #
        max_sending_tries = 3
        # make sure that the rate is not to high
        time_passed = time.time() - self.time_at_last_request
        logger.debug('time passed %s' % str(time_passed))
        # send the request,
        for send_request_tries in range(max_sending_tries):
            # wait 1/7 second (amocrm wants it this way)
            if time_passed < (1.0 / 7.0):
                logger.debug('have to wait %s' % str((1.0 / 7.0) - time_passed))
                time.sleep((1.0 / 7.0) - time_passed)

            # reset time
            self.time_at_last_request = time.time()
            try:
                url = self._get_url(path)
                response = self._session.request(method,
                                                 url=url,
                                                 json=data,
                                                 params=params,
                                                 headers=headers)
                logger.debug('sending amo-request')
            except ConnectionError as err:
                error = f"Got an exception while using method \"{method}\" on {url}. Error is:\n{str(err)}"
                logger.warning(error)
                logger.warning(f'current try: {send_request_tries}')
                if send_request_tries < 3:
                    send_request_tries += 1
                else:
                    raise AmoApiException(err.args[0].args[0])  # Sometimes Connection aborted.
            except Exception as err:
                error = f"Got an exception while using method \"{method}\" on {url}. Error is:\n{str(err)}"
                logger.error(error)
                raise
            else:
                if response.status_code == 200:
                    return response, 200
                elif response.status_code == 204:
                    return None, 204
                elif response.status_code < 300 or response.status_code == 400:
                    return response.json(), response.status_code
                else:
                    logger.error("There is a error with this request.")
                    logger.error("Status: {} ({})".format(response.status_code, response.text))
                if response.status_code == 401:
                    raise UnAuthorizedException()
                if response.status_code == 403:
                    raise PermissionsDenyException()
                if response.status_code == 402:
                    raise ValueError("Тариф не позволяет включать покупателей")
                raise AmoApiException("Wrong status {} ({})".format(response.status_code, response.text))

    def request(self, method, path, data=None, params=None, headers=None, include=None):
        params = params or {}
        if include:
            params["with"] = ",".join(include)
        return self._request(method, path, data=data, params=params, headers=headers)

    def _list(self, path, page, include=None, limit=250, query=None, filters: Tuple[Filter] = (), order=None):
        assert order is None or len(order) == 1
        assert limit <= 250
        params = {
            "page": page,
            "limit": limit,
            "query": query,
        }
        if order:
            field, value = list(order.items())[0]
            params["order[{}]".format(field)] = value
        for _filter in filters:
            params.update(_filter._as_params())
        return self.request("get", path, params=params, include=include)

    def _all(self, path, include=None, query=None, filters: Tuple[Filter] = (), order=None, limit=250):
        page = 1
        while True:
            response, _ = self._list(
                path, page, include=include, query=query, filters=filters, order=order, limit=limit
            )
            if response is None:
                return
            yield response["_embedded"]
            if "next" not in response["_links"]:
                return
            page += 1
