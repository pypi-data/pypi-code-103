import json
import logging
from requests import HTTPError

from ..services.exceptions import InterfaceResourceUnavailable

logger = logging.getLogger(__name__)


class ExternalService:
    @classmethod
    def _service_response_error(cls, err_msg: str):
        """
        Request function for handling errors requesting
        interface resources.
        """
        def _hook(response, *args,  **kwargs):
            try:
                response.raise_for_status()
            except HTTPError as e:
                error_data = None

                try:
                    error_data = response.json()
                except json.decoder.JSONDecodeError:
                    error_data = response.text

                logger.warning(
                    f'Error accessing external service {response.request}',
                    extra={
                        'response': response.status_code,
                        'error_data': error_data,
                        'url': response.request.url
                    }
                )

                raise InterfaceResourceUnavailable(
                    details=err_msg,
                    status=e.response.status_code
                ) from e

        return _hook

    @classmethod
    def _make_hook(cls, err_msg: str):
        return {
            'response': [cls._service_response_error(err_msg)]
        }