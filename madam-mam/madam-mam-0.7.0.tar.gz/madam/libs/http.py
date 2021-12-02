# Copyright 2021 Vincent Texier
#
# This file is part of MADAM.
#
# MADAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MADAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MADAM.  If not, see <https://www.gnu.org/licenses/>.

import copy
import json
import logging
from http.client import HTTPResponse
from typing import Any, Optional
from urllib import parse, request

# Response type constants
RESPONSE_JSON = "json"
RESPONSE_TEXT = "text"
RESPONSE_HTTP = "http"


class HTTPClient:
    def request(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[dict] = None,
        rtype: str = RESPONSE_JSON,
        json_data: Optional[dict] = None,
        **kwargs: Any,
    ) -> Any:
        """
        HTTP request

        :param url: the request url
        :param method: Http method  'GET' or 'POST' (optional, default='GET')
        :param headers: Http headers (optional, default=None)
        :param rtype: Response type (optional, default=RESPONSE_JSON, can be RESPONSE_TEXT, RESPONSE_HTTP)
        :param json_data: Json data as dict (optional, default=None)

        :return:
        """
        if headers is None:
            headers = {}

        logging.debug("Request: %s", url)
        request_ = request.Request(url, method=method)

        if kwargs:
            # urlencoded http form content as bytes
            request_.data = parse.urlencode(kwargs).encode("utf-8")
            logging.debug("%s : %s, data=%s", method, url, request_.data)

        if json_data:
            # json content as bytes
            request_.data = json.dumps(json_data).encode("utf-8")
            logging.debug("%s : %s, data=%s", method, url, request_.data)

            # http header to send json body
            headers["Content-Type"] = "application/json"

        if len(headers) > 0:
            request_.headers = headers

        with request.urlopen(request_, timeout=15) as response:  # type: HTTPResponse
            if response.status != 200:
                content = response.read().decode("utf-8")
                raise ValueError(f"status code != 200 => {response.status} ({content})")

            # get response content
            return_response = copy.copy(response)
            content = response.read().decode("utf-8")

        # return the chosen type
        result = return_response  # type: Any
        if rtype == RESPONSE_TEXT:
            result = content
        elif rtype == RESPONSE_JSON:
            result = json.loads(content)

        return result
