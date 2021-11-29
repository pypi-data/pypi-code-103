import logging.config

import requests

from .constants import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
LOGGER = logging.getLogger("root")


class APIHandler:
    REQUEST_TIMEOUT = 60

    # TODO: Define own variables as per requirement
    def __init__(
        self,
        host: str,
        headers: dict,
        logging: bool = True,
    ):
        self._host = host
        self._headers = headers
        self.__logging = logging

    @property
    def host(self):
        return self._host

    def send_request(
        self, method, url, payload=None, log_config: dict = None, headers: dict = None
    ):
        if not headers:
            headers = self._headers

        if self.__logging:
            LOGGER.info("Sending [%s] API call to [%s]", method, f"{self.host}{url}")

        log_entry = None

        # TODO: Define own variables as per requirement
        if log_config:
            if (
                "model" not in log_config
                or "user" not in log_config
                or "sba_number" not in log_config
                or "timezone" not in log_config
            ):
                raise Exception("Invalid log dict")

        try:
            # TODO: Understand what needs to be logged?
            if log_config:
                log_entry = log_config["model"](
                    sba_number=log_config["sba_number"],
                    requested_by=log_config["user"],
                    request_url=f"{method}: {url}",
                    request_headers=headers,
                    request_body=payload,
                    request_time=log_config["timezone"].now(),
                )

            response = requests.request(
                method,
                f"{self.host}{url}",
                headers=headers,
                timeout=self.REQUEST_TIMEOUT,
                data=payload,
            )

            if self.__logging:
                LOGGER.info(
                    "Received [%s] response for [%s: %s]",
                    response.status_code,
                    method,
                    f"{self.host}{url}",
                )

            if log_entry:
                log_entry.response_code = response.status_code
                log_entry.response_body = response.text
                log_entry.response_time = log_entry.request_time + response.elapsed
                log_entry.save()

            response.raise_for_status()

            response = response.text

            if self.__logging:
                LOGGER.info(
                    "WKFS Response for [%s: %s] -- [%s]",
                    method,
                    f"{self.host}{url}",
                    response,
                )

            # In case if the token expires, the response status code will be 401, the header will contain the error information.
            # The header property for 401 error is WWW-Authenticate.
            # Value for header property for 401 error is Bearer error="invalid_token", error_description="The token expired at '11/09/2021 14:58:41'"
            return response
        except requests.HTTPError as excp:
            if self.__logging:
                LOGGER.error(
                    "WKFS API Failed. Received [%s] response for [%s: %s]",
                    response.status_code,
                    method,
                    f"{self.host}{url}",
                )

            raise Exception(
                f"Failed to get success response from WKFS. Response: [{response.text}]"
            ) from excp
