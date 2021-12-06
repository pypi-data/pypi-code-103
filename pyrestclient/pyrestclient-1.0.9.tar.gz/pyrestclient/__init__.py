import base64
import json
import re
import socket
from http import HTTPStatus
from typing import Union
from urllib.parse import urljoin, urlencode

import requests
from urllib3 import disable_warnings, exceptions

from .logger import logger

disable_warnings(exceptions.InsecureRequestWarning)


def json_data(data):
    return json.dumps(data)


def get_header_default(user_agent='ide', content_type='application/json-patch+json', accept='application/json'):
    return {
        'User-Agent': user_agent,
        'Content-Type': content_type,
        'Accept': accept,
        # 'UserAgentInternal': 'webfrontend/1.0'
    }


def log_params(func):
    def inner(*args, **kwargs):
        # log_info = f'{locals()["kwargs"]}.'

        log_info = ' | '.join([f'{key}={value}' for key, value in locals()["kwargs"].items()])
        if len(args) > 1:
            log_info += f'UNKNOWN params: {args[1:]}'
        logger.info(log_info)
        return func(*args, **kwargs)

    return inner


class RESTAssertion:
    """Parse requests response to get status code."""

    @staticmethod
    def should_be_success_response_code(response):
        """200 <= status_code < 400"""
        assert response.ok, 'Response code is not success.'

    @staticmethod
    def should_be_ok_response_code(response):
        """OK, 200. Request fulfilled, document follows"""
        assert response.status_code == HTTPStatus.OK, 'Response code is not 200.'

    @staticmethod
    def should_be_not_found_response_code(response):
        """Nothing matches the given URI"""
        assert response.status_code == HTTPStatus.NOT_FOUND, 'Response code is not 404.'

    @staticmethod
    def should_be_bad_request(response):
        """Bad request syntax or unsupported method"""
        assert response.status_code == HTTPStatus.BAD_REQUEST, 'Response code is not 400.'


class RESTClient(RESTAssertion):
    """ Main class for RestAPI """

    def __init__(self,
                 protocol: str = '',
                 host: str = '',
                 port: int = 0,
                 username: str = None,
                 password: str = None,
                 header: dict = None,
                 auth_basic: bool = False,
                 auth_uri: str = '',
                 auth_payload: dict = None,
                 logger_enabled: bool = True,
                 encode_password: bool = False):

        # Enable/disable logger
        self.logger = logger
        logger.disabled = not logger_enabled

        # Credentials and settings for api url
        self.username = username
        self.password = password
        self.protocol = protocol  # HTTP or HTTPS
        self.host = host
        self.port = port
        self.auth_uri = auth_uri
        self.auth_payload = auth_payload
        self.auth_basic = auth_basic
        self.header = header or get_header_default()  # Default header

    def __str__(self):

        return f'Username: {self.username}\n' \
               f'Password: {self.password}\n' \
               f'Base URL: {self.base_url}\n'

    @property
    def base_url(self):
        """Create tested URL"""

        return f'{self.protocol}://{self.host}:{self.port}' if self.port else f'{self.protocol}://{self.host}'

    def requested_url(self, url):
        """ Return full URL if link specified contains 'http' """

        if 'http' in url:
            return url
        elif self._validate_url(self.base_url):
            return urljoin(self.base_url, url)
        raise SyntaxError(f'URL does not specified. Used: "{url}" only. Specify full URL or use constructor')

    @staticmethod
    def _validate_url(url):
        return re.match(r'http[s]?://[\w/.]+', url)

    def get_token(self) -> str:
        """Get auth (Bearer) token"""

        return AuthToken(self).token

    def get_auth_header(self, header: dict = None) -> dict:
        """Get auth header with a token

        :param header: custom header is needed
        :return:
        """

        self.header = header or get_header_default()

        try:
            self.token = self.get_token()
            self.header['Authorization'] = self.token
            return self.header
        except KeyError as err:
            logger.error(f'Cannot get token. {err}')

    def _auth_basic(self):
        """Enable basic auth if provided"""

        self.header = {}
        return self.username, self.password

    def send_request(self,
                     method: str,
                     url: str,
                     data: dict = None,
                     files=None,
                     query_params: dict = None,
                     verify: bool = False,
                     custom_header: dict = None,
                     cookies=None,
                     request_timeout: int = 60):

        """Send common REST request

        To upload file use:

        with open(files, 'rb') as f:
             files = {'licenseFile': (License.name, f)}

        :param cookies:
        :param method: GET, POST, DELETE
        :param url: unified identifier, self.url (BASE) + url
        :param query_params: = Query parameters in the url
        :param data: json data
        :param files: "files: {'licenseFile': (License.name, f)}"
        :param verify: Bool
        :param custom_header: Use specified header
        :param request_timeout: Time in sec.
        :return: requests.request('POST', url=url, headers=HEADER, files=files, verify=False)

        """

        # Set auth method
        if self.auth_payload is not None:
            self.header = self.get_auth_header(header=custom_header)
        elif self.auth_basic:
            self.auth_basic = self._auth_basic()
        elif custom_header:
            self.header = custom_header

        # Make full url to use in request
        link = self.requested_url(url)

        # Add params to requested link
        if query_params:
            link += '?' + urlencode(query_params)

        method = method.upper()

        assert method in ['GET', 'HEAD', 'DELETE', 'POST', 'PUT', 'PATCH', 'OPTIONS'], \
            'Specified methods is not compatible.'

        if data and files:
            logger.error('Data parameter cannot be used with files parameter simultaneously.')
            raise ValueError('Data parameter cannot be used with files parameter simultaneously.')

        # Extend header
        if 'Content-Type' not in self.header:
            self.header['Content-Type'] = 'application/json'

        response = 'Invalid requests. Check parameters'

        logger.info(f'[{method}] {link}')

        try:
            # For 'POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE'
            if method in ['POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE']:
                if data and not files:

                    logger.debug(f'Headers={self.header}, '
                                 f'Cookies={cookies}, '
                                 f'Timeout={request_timeout}')
                    logger.info('PAYLOAD:\n' + json.dumps(data, indent=4))

                    response = requests.request(method=method,
                                                url=link,
                                                auth=self.auth_basic,
                                                headers=self.header,
                                                json=data,
                                                cookies=cookies,
                                                verify=verify,
                                                timeout=request_timeout)

                elif files:
                    files_header = self.header.copy()
                    del files_header['Content-Type']

                    logger.debug(f'Headers={files_header}, '
                                 f'Cookies={cookies}, '
                                 f'Timeout={request_timeout}')
                    logger.info('PAYLOAD:\n' + json.dumps(data, indent=4))

                    response = requests.request(method=method,
                                                url=link,
                                                auth=self.auth_basic,
                                                headers=files_header,
                                                cookies=cookies,
                                                files=files,
                                                verify=verify,
                                                timeout=request_timeout)

                elif not files and not data:
                    logger.debug(f'Header={self.header}, '
                                 f'Cookies={cookies}, '
                                 f'Timeout={request_timeout}')

                    response = requests.request(method=method,
                                                url=link,
                                                auth=self.auth_basic,
                                                headers=self.header,
                                                cookies=cookies,
                                                verify=verify,
                                                timeout=request_timeout)

            # For 'GET', 'HEAD' request
            else:
                # For usual 'GET' without query params
                header = custom_header if custom_header else self.header

                logger.debug(f'Header={header}, '
                             f'Cookies={cookies}, '
                             f'Timeout={request_timeout}')

                response = requests.request(method=method,
                                            url=link,
                                            auth=self.auth_basic,
                                            cookies=cookies,
                                            headers=header,
                                            verify=verify,
                                            timeout=request_timeout)

        except BaseException as err:
            logger.exception('Something wend wrong.')
            raise err

        return response

    @property
    def is_service_available(self):
        """Check base url availability within 10 sec."""

        try:
            response = requests.get(self.base_url, timeout=10, verify=False)
            if response.status_code == 200:
                return True
            return False
        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ConnectionError:
            return False

    def download(self, url: str, dst: str):
        """Download file.

        :param url: Full url to file
        :param dst: path to store
        :return:
        """

        response = self.send_request('GET', url)
        try:
            if response.ok:
                with open(dst, 'wb') as f:
                    f.write(response.content)
                    return True
            else:
                return False
        except (ConnectionError, ConnectionRefusedError) as err:
            logger.error(f'Download failed. {err}')
            return err

    # noinspection PyPep8Naming
    def GET(self,
            url: str = '',
            query_params: dict = None,
            cookies=None,
            request_timeout: int = None,
            header: dict = None):

        return self.send_request(method='GET',
                                 url=url,
                                 query_params=query_params,
                                 cookies=cookies,
                                 request_timeout=request_timeout,
                                 custom_header=header)

    # noinspection PyPep8Naming
    def POST(self,
             url: str = '',
             data: dict = None,
             file=None,
             query_params: dict = None,
             cookies=None,
             request_timeout: int = None,
             header: dict = None):

        return self.send_request(method='POST',
                                 url=url,
                                 query_params=query_params,
                                 data=data,
                                 files=file,
                                 cookies=cookies,
                                 request_timeout=request_timeout,
                                 custom_header=header)

    # noinspection PyPep8Naming
    def PUT(self,
            url: str = '',
            data: dict = '',
            files='',
            query_params: dict = None,
            cookies=None,
            request_timeout: int = None,
            header: dict = None):

        header_original = self.header.copy()

        if files:  # FIXME
            del header_original['Content-Type']

        return self.send_request(method='PUT',
                                 url=url,
                                 data=data,
                                 files=files,
                                 query_params=query_params,
                                 cookies=cookies,
                                 request_timeout=request_timeout,
                                 custom_header=header)

    def DELETE(self,
               url: str = '',
               data: dict = '',
               query_params: dict = None,
               cookies=None,
               request_timeout: int = None,
               header: dict = None):

        return self.send_request(method='DELETE',
                                 url=url,
                                 query_params=query_params,
                                 data=data,
                                 cookies=cookies,
                                 request_timeout=request_timeout,
                                 custom_header=header)

    def is_host_available(self, port: int = 0, timeout: int = 5) -> bool:
        """Check remote host availability using socket and specified port"""

        port_ = port or self.port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((self.host, port_))
            return False if result else True

    def is_service_initialized(self, timeout: Union[int, float] = 20) -> bool:
        """Send GET to base URL https://{IP}:{PORT}

        :param timeout:
        :return:
        """

        try:
            response = requests.get(self.base_url, verify=False, timeout=timeout)
            return response.ok
        except requests.exceptions.ConnectionError:
            return False

    def wait_service_start(self, timeout: int = 30) -> bool:
        """Waiting for the service start.

        :param timeout: in sec.
        :return:
        """

        timer = 0
        status = self.is_service_initialized(1)

        while not status:
            status = self.is_service_initialized(1)
            timer += 1

            if timer > timeout - 2:
                raise TimeoutError(f'The service was not started within {timeout} seconds.')
        return status


class AuthToken:
    """Class to get auth token"""

    def __init__(self, client: RESTClient):
        self.client = client

    @property
    def auth_url(self):
        """Get full authorization URL"""
        return urljoin(self.client.base_url, self.client.auth_uri)

    @property
    def token(self):
        """Get token"""

        response_json = None

        try:
            response = requests.post(self.auth_url, json=self.client.auth_payload, verify=False, timeout=7)
            response_json = response.json()
            return response_json['token']
        except KeyError as err:
            logger.exception(f'Cannot get key (token) from json data. {response_json}')
            raise err
        except json.decoder.JSONDecodeError as err:
            logger.exception(f'Cannot get token property. URL: {self.auth_url} ({self.client.auth_payload})', err)
            raise err
        except TypeError as err:
            logger.exception('Endpoint is available but "token" key cannot be retrieved.', err)
            raise err
        except requests.exceptions.ConnectTimeout as err:
            logger.exception(f'Perhaps, URI ({self.auth_url}) or service is unreachable.')
            raise err
