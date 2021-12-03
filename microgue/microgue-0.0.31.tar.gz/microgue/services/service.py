import json
import logging
import requests
import traceback
from collections import OrderedDict
from ..constants.error_constants import ErrorConstants
from ..utils import mask_fields_in_data

logger = logging.getLogger('microgue')


class Service:
    class Response:
        def __init__(self, status_code=400, headers={}, cookies={}, data={}):
            self.status_code = status_code
            self.headers = headers
            self.cookies = cookies
            self.data = data

    def __init__(self, *args, **kwargs):
        self._request_base_url = ''
        self._request_url = ''
        self._request_parameters = {}
        self._request_method = 'GET'
        self._request_headers = {}
        self._request_cookies = {}
        self._request_data = {}
        self._request_files = {}
        self.convert_request_data_to_json = True
        self.mask_request_headers_fields = []
        self.mask_request_data_fields = []
        self.verify_ssl = True

    @property
    def request_base_url(self):
        return self._request_base_url

    @request_base_url.setter
    def request_base_url(self, value):
        self._request_base_url = value

    @property
    def request_url(self):
        return self._request_url

    @request_url.setter
    def request_url(self, value):
        self._request_url = self.request_base_url + value

    @property
    def request_parameters(self):
        return self._request_parameters

    @request_parameters.setter
    def request_parameters(self, value):
        if type(value) is str:
            self._request_parameters = json.loads(value)
        else:
            self._request_parameters = value

    @property
    def request_method(self):
        return self._request_method

    @request_method.setter
    def request_method(self, value):
        self._request_method = value

    @property
    def request_headers(self):
        return self._request_headers

    @request_headers.setter
    def request_headers(self, value):
        if type(value) is str:
            self._request_headers = json.loads(value)
        else:
            self._request_headers = value

    @property
    def request_cookies(self):
        return self._request_cookies

    @request_cookies.setter
    def request_cookies(self, value):
        if type(value) is str:
            self._request_cookies = json.loads(value)
        else:
            self._request_cookies = value

    @property
    def request_data(self):
        return self._request_data

    @request_data.setter
    def request_data(self, value):
        if type(value) is str:
            self._request_data = json.loads(value)
        else:
            self._request_data = value

    @property
    def request_files(self):
        return self._request_files

    @request_files.setter
    def request_files(self, value):
        self._request_files = value

    def request(self, url, method=None, headers=None, cookies=None, data=None):
        self.request_url = url

        if method is not None:
            self.request_method = method
        if headers is not None:
            self.request_headers = headers
        if cookies is not None:
            self.request_cookies = cookies
        if data is not None:
            self.request_data = data

        return self.invoke()

    def invoke(self):
        logger.debug("########## {} Invoke ##########".format(self.__class__.__name__))
        logger.debug("request url: {}".format(self.request_url))
        logger.debug("request method: {}".format(self.request_method))
        logger.debug("request headers: {}".format(mask_fields_in_data(self.request_headers, self.mask_request_headers_fields)))
        logger.debug("request cookies: {}".format(self.request_cookies))
        logger.debug("request data: {}".format(mask_fields_in_data(self.request_data, self.mask_request_data_fields)))

        request_data = json.dumps(self.request_data) if self.request_data and self.convert_request_data_to_json else self.request_data

        # open all files before sending them
        request_files = OrderedDict()
        for key, file in self.request_files.items():
            request_files[key] = open(file, 'rb')

        try:
            requests_response = requests.request(
                url=self.request_url,
                params=self.request_parameters,
                method=self.request_method,
                headers=self.request_headers,
                cookies=self.request_cookies,
                data=request_data,
                files=request_files,
                verify=self.verify_ssl
            )

            response_status_code = requests_response.status_code
            response_headers = dict(requests_response.headers)
            response_cookies = dict(requests_response.cookies)

            try:
                response_data = requests_response.json()
            except:
                response_data = requests_response.text

            logger.debug("########## {} Invoke Response".format(self.__class__.__name__))
            logger.debug("response status code: {}".format(response_status_code))
            logger.debug("response headers: {}".format(response_headers))
            logger.debug("response cookies: {}".format(response_cookies))
            logger.debug("response data: {}".format(response_data))

        except Exception as e:
            logger.error("########## {} Invoke Error".format(self.__class__.__name__))
            logger.error("{}: {}".format(e.__class__.__name__, str(e)))
            logger.error(traceback.format_exc())
            response_status_code = 500
            response_headers = {}
            response_cookies = {}
            response_data = {'error': ErrorConstants.App.INTERNAL_SERVER_ERROR}

        return self.Response(
            status_code=response_status_code,
            headers=response_headers,
            cookies=response_cookies,
            data=response_data
        )
