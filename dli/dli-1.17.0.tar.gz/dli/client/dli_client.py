#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import base64
import datetime
import os
import re
import sys
import time
import webbrowser
from json import JSONDecodeError
import uuid
import keyring
import jwt
import requests
import logging
import inspect
import socket
from http.cookiejar import CookiePolicy
from http import HTTPStatus
from urllib.parse import urljoin, urlparse, parse_qs
from collections import defaultdict

from dli import __version__, __product__
from dli.client import ModelDescriptor
from dli.cli.boto_authenticator import BotoAuthenticator

from dli.components.auto_reg_metadata import AutoRegMetadata
from dli.components.package import Package
from dli.components.dataset import Dataset
from dli.components.dictionary import Dictionary
from dli.components.datafile import Datafile

from dli.models.package_model import PackageModel
from dli.models.dataset_factory import DatasetFactory
from dli.models.structured_dataset_model import StructuredDatasetModel
from dli.models.unstructured_dataset_model import UnstructuredDatasetModel
from dli.models.dictionary_model import DictionaryModel
from dli.models.file_model import FileModel
from dli.models.instance_model import InstanceModel
from dli.models.instance_model_collection import InstanceModelCollection as InstancesCollection_
from dli.modules.package_module import PackageModule
from dli.modules.dataset_module import DatasetModule

from platform_services_lib.lib.authentication.auth import _sam_app_flow, decode_token as _decode_token
from platform_services_lib.lib.context.urls import identity_urls
from platform_services_lib.lib.context.environments import _Environment
from platform_services_lib.lib.adapters.pagination_adapters import Paginator
from platform_services_lib.lib.adapters.session_adapters import (
    DLIBearerAuthAdapter, DLIAccountsV1Adapter,
    DLIInterfaceV1Adapter, DLISamAdapter
)
from platform_services_lib.lib.handlers.analytics_handler import AnalyticsHandler, AnalyticsSender
from platform_services_lib.lib.services.exceptions import (
    DatalakeException, InsufficientPrivilegesException,
    InvalidPayloadException, UnAuthorisedAccessException,
    CatalogueEntityNotFoundException,
    DatalakeGatewayTimeout, DatalakeServiceUnavailable,
    DatalakePayloadTooLargeException, ConnectionException
)

trace_logger = logging.getLogger('trace_logger')


def _read_field_values(class_fields_to_include, wrapped_object):
    properties = {}
    for field in class_fields_to_include or []:
        property_name = field.split('.')[-1]
        property_value = wrapped_object
        for nested_field_name in field.split('.'):
            property_value = property_value.__dict__[nested_field_name]
        properties.update({property_name: property_value})
    return properties


class DliClient(AutoRegMetadata, Datafile, Dataset, Dictionary, Package):
    """
    Definition of a client. This client mixes in utility functions for
    manipulating packages, datasets and datafiles.
    """

    _Package = ModelDescriptor(PackageModel)
    _DatasetFactory = ModelDescriptor(DatasetFactory)
    _Structured = ModelDescriptor(StructuredDatasetModel)
    _Unstructured = ModelDescriptor(UnstructuredDatasetModel)

    _Instance = ModelDescriptor(InstanceModel)
    _InstancesCollection = ModelDescriptor(InstancesCollection_)
    _File = ModelDescriptor(FileModel)

    _Pagination = ModelDescriptor(Paginator)
    _DictionaryV2 = ModelDescriptor(DictionaryModel)

    _packages = ModelDescriptor(PackageModule)
    _datasets = ModelDescriptor(DatasetModule)

    _environment_class = _Environment

    def __init__(self, api_root, debug=None, strict=True,
                 access_id=None, secret_key=None, use_keyring=True, show_login_url=False):
        self._environment = self._environment_class(api_root)
        self.access_id = access_id
        self.secret_key = secret_key
        self.debug = debug
        self.strict = strict
        self.use_keyring = use_keyring
        self.logger = logging.getLogger(__name__)
        self.show_login_url = show_login_url

        self.logger.debug(
            'Starting SDK session',
            extra={
               'catalogue': self._environment.catalogue,
               'consumption': self._environment.consumption,
               'strict': strict,
               'version': __version__
            }
        )

        self._session = self._new_session()
        __config = {
            'version': __version__,
            'app_name': 'SDK',
            'consumption_env': self._environment.consumption,
            'strict': self.strict,
            'logger': self.logger,
        }
        __sender = AnalyticsSender(__config, session_func=self._session_func)
        self._analytics_handler = AnalyticsHandler(__sender)

        #: access to the :class:`~dli.modules.package_module.PackageModule` to get packages. This method is callable as well (e.g. client.packages() - see class for parameters)
        self.packages = self._packages()

        #: access to the :class:`~dli.modules.dataset_module.DatasetModule` to get datasets.  This method is callable as well (e.g. client.datasets()  - see class for parameters )
        self.datasets = self._datasets()

        self._boto_authenticator = None

    def _analytics_extract_metadata(
        self, wrapped_object, func, arguments,
        keyword_args, class_fields_to_include=None
    ):
        org_id = None
        if 'datalake' in self.session.decoded_token:
            org_id = self.session.decoded_token.get('datalake').get('organisation_id', None)

        subject = self.session.decoded_token.get('sub', 'UNKNOWN USER')
        argspec = inspect.getfullargspec(func)
        args_dict = dict(zip(argspec.args, [wrapped_object, *arguments]))
        properties = _read_field_values(class_fields_to_include, wrapped_object)

        return {
            'func': func,
            'subject': subject,
            'organisation_id': org_id,
            'arguments': args_dict,
            'kwargs': dict(keyword_args),
            'properties': properties
        }, self

    def _new_session(self) -> 'Session':
        session = Session(
            self.access_id,
            self.secret_key,
            self._environment,
            logger=self.logger,
            use_keyring=self.use_keyring,
            show_login_url=self.show_login_url,
        )
        return session

    @property
    def session(self) -> 'Session':
        """
        Access to the :class:`dli.client.Session` to get the current JWT (client.session.auth_key).
        Under common circumstances, you should not need to use this directly.
        """
        return self._session_func()

    def _session_func(self) -> 'Session':
        if self._session and self._session.has_expired:
            # if the session expired, then re-auth
            # and create a new context
            self._session = self._new_session()
        return self._session

    @property
    def aws_authenticator(self):
        """
        Worker object that can be called with:

        >>> client = dli.connect()
        >>> client.aws_authenticator.start()

        In order to sync the ~/.aws/credentials file with
        the current user. Can be explicitly stopped via:

        >>> client.aws_authenticator.stop()

        Will simply shutdown when the DLI exits.
        """
        if (
            not self._boto_authenticator or
            not self._boto_authenticator.is_alive()
        ):
            self._boto_authenticator = BotoAuthenticator(self)

        return self._boto_authenticator


class Session(requests.Session):

    # Default the request timeout to 60 seconds when no timeout is provided.
    __REQUESTS_DEFAULT_TIMEOUT = int(os.environ.get('REQUESTS_DEFAULT_TIMEOUT', '60'))

    def __init__(
        self, access_id, secret_key, environment, logger,
        auth_key=None, auth_prompt=True, use_keyring=True, show_login_url=False
    ):
        super().__init__()
        self.auth_key = None
        self.logger = logger
        self.access_id = access_id
        self.secret_key = secret_key
        self._environment = environment
        self.use_keyring = use_keyring
        self.show_login_url = show_login_url

        if auth_prompt:
            self._auth_init(auth_key)
        # mount points to add headers to specific routing requests
        self._set_mount_adapters()

        # Don't allow cookies to be set.
        # The new API will reject requests with both a cookie
        # and a auth header (as there's no predictable crediential to choose).
        #
        # However the old API, once authenticated using a Bearer token, will
        # as a side effect of a request return a oidc_id_token which matches
        # the auth header. This is ignored.
        self.cookies.set_policy(BlockAll())

    def __check(self, issplit, splitlen):
        check_key = keyring.get_password(
            __product__, self._environment.catalogue)
        if check_key:
            split_check = check_key.split("**split**")
            if len(split_check) > 1:
                issplit = True
                splitlen = int(split_check[-1])
                chunked_jwt = ''
                # we must re-form the jwt
                for ix in range(splitlen):
                    chunked_jwt += keyring.get_password(
                        __product__,
                        self._environment.catalogue + f"-{ix}")

                check_key = chunked_jwt
        return check_key, issplit, splitlen

    def __exception_handler(self, nke, raises):
        # disable the use of keyring
        self.use_keyring = False
        print(
            "We have noticed you are trying to run the SDK on a headless "
            "machine but your application credential environment variables "
            "(DLI_ACCESS_KEY_ID and DLI_SECRET_ACCESS_KEY) "
            "are not set or there is no keyring manager available. \n\n"
            "YOU MAY NEED TO LOGIN EVERY TIME. \n"
            "Please contact support at datalake-support@ihsmarkit.com "
            "if you need more help. \n\n"
            f"{str(nke)}\n\n"
        )
        if raises:
            raise nke

    def _reload_or_web_flow(self, raises=False):
        from keyring.errors import PasswordDeleteError

        check_key = None
        issplit = False
        splitlen = 0

        if hasattr(self, "use_keyring") and self.use_keyring:
            try:
                from keyring.errors import NoKeyringError
                try:
                    check_key, issplit, splitlen = self.__check(issplit, splitlen)
                except NoKeyringError as nke:
                    self.__exception_handler(nke, raises)
            except ImportError:
                try:
                    check_key, issplit, splitlen = self.__check(issplit, splitlen)
                except RuntimeError as nke:
                    self.__exception_handler(nke, raises)

        reloaded = None
        if check_key:
            try:
                reloaded = check_key
                decoded = _decode_token(str.encode(reloaded))
                if decoded.get("exp", 0) <= time.time():
                    try:
                        keyring.delete_password(__product__,
                                                self._environment.catalogue)
                        if issplit:
                            for ix in range(splitlen):
                                keyring.delete_password(
                                    __product__,
                                    self._environment.catalogue + f"-{ix}"
                                )
                    except PasswordDeleteError as e:
                        self.logger.debug("No such password")
                    finally:
                        reloaded = None
            except Exception as e:
                raise e

        if reloaded:
            self.logger.debug(f"Using vault JWT "
                             f"{__product__} "
                             f"{self._environment.catalogue}")
            self.auth_key = reloaded
        elif not self.secret_key and not self.access_id:
            self.auth_key = self._get_web_auth_key()

    def _auth_init(self, auth_key=None):
        if auth_key:
            self.auth_key = auth_key
        elif self.access_id and self.secret_key:
            self.auth_key = self._get_SAM_auth_key()
        else:
            self._reload_or_web_flow()

        self.decoded_token = self._get_decoded_token()
        self.token_expires_on = self._get_expiration_date()

    def request(self, method, url, *args, **kwargs):
        headers = kwargs.pop('headers', {})

        if not urlparse(url).netloc:

            # HACK, todo 2020-07
            # we have this because catalogue has ingress rules to map back to identity based on the /identity/ regex
            # we could instead setup nginx ingress in docker, but its heavy-weight. So if DEV_MODE is set
            # we just target identity directly, if the url matches the nginx rule (exported from nginx) below.
            # we then need to patch the jwt back on to send directly to identity
            if os.environ.get('DEV_MODE', 'False').lower() == 'true':
                identity = re.compile("/api/identity(/|${literal_dollar})(.*)")
                if identity.match(url):
                    url = urljoin(os.environ.get('DATA_LAKE_ACCOUNTS_URL'), url.replace("/api/identity", ""))
                    headers["Authorization"] = f"Bearer {self.auth_key}"
                else:
                    url = urljoin(self._environment.catalogue, url)
            else:
                url = urljoin(self._environment.catalogue, url)

        kwargs.pop('hooks', None)
        hooks = {'response': self._response_hook}

        # Default the request timeout to 60 seconds when no timeout is provided in the calling method.
        # "By default, requests do not time out unless a timeout value is set explicitly. Without a timeout, your
        # code may hang for minutes or more."
        # https://docs.python-requests.org/en/master/user/advanced/#timeouts
        kwargs.setdefault('timeout', self.__REQUESTS_DEFAULT_TIMEOUT)

        # Adding this here in order to log the request ID
        request_id = str(uuid.uuid4())
        headers['X-Request-ID'] = request_id
        headers["X-Data-Lake-SDK-Version"] = str(__version__)

        try:
            self.logger.debug(
                f'{method} Request to {url} with request_id: {request_id}',
                extra={
                    'method': method,
                    'request': url,
                    '-args': args,
                    '-kwargs': kwargs,
                    'request_id': request_id
                }
            )

            return super().request(
                method, url, hooks=hooks, headers=headers, *args, **kwargs
            )
        except requests.exceptions.ConnectTimeout as e:
            trace_logger.exception('Connection timeout sending request', e)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionException(e)
        except socket.error as e:
            raise ValueError(
                'Unable to process request due to a networking issue '
                'root cause could be a bad connection, '
                'not being on the correct VPN, '
                'or a network timeout '
            ) from e

    @property
    def has_expired(self):
        # We subtract timedelta from the expiration time in order to allow a safety window for
        # a code block to execute after a check has been asserted.
        return datetime.datetime.utcnow() > \
               (self.token_expires_on - datetime.timedelta(minutes=1))

    def _response_hook(self, response, *args, **kwargs):

        if self.logger:
            self.logger.debug(
                'Response',
                extra={
                    # 'content': response.content,
                    'status': response.status_code,
                    'method': response.request.method,
                    'request': response.request.url,
                    'headers': response.request.headers
                }
            )

        if not response.ok:
            exceptions = defaultdict(
                lambda: DatalakeException,
                {
                 # 400 errors
                 HTTPStatus.BAD_REQUEST: InvalidPayloadException,
                 HTTPStatus.UNPROCESSABLE_ENTITY: InvalidPayloadException,
                 HTTPStatus.UNAUTHORIZED: UnAuthorisedAccessException,
                 HTTPStatus.FORBIDDEN: InsufficientPrivilegesException,
                 HTTPStatus.NOT_FOUND: CatalogueEntityNotFoundException,

                 # 500 errors
                 HTTPStatus.REQUEST_ENTITY_TOO_LARGE: DatalakePayloadTooLargeException,
                 HTTPStatus.SERVICE_UNAVAILABLE: DatalakeServiceUnavailable,
                 HTTPStatus.BAD_GATEWAY: DatalakeServiceUnavailable,
                 HTTPStatus.GATEWAY_TIMEOUT: DatalakeGatewayTimeout,
                 }
            )

            try:
                message = response.json()
            except (JSONDecodeError, ValueError):
                message = response.text

            raise exceptions[response.status_code](
                message=message,
                params=parse_qs(urlparse(response.request.url).query),
                response=response
            )

        return response

    def _set_mount_adapters(self):
        self.mount(
            urljoin(self._environment.catalogue, '__api/'),
            DLIInterfaceV1Adapter(self)
        )

        self.mount(
            urljoin(self._environment.catalogue, '__api_v2/'),
            DLIBearerAuthAdapter(self)
        )

        self.mount(
            self._environment.consumption, DLIBearerAuthAdapter(self)
        )

        self.mount(
            urljoin(self._environment.accounts, 'api/identity/v1/'),
            DLIAccountsV1Adapter(self)
        )

        self.mount(
            urljoin(self._environment.accounts, 'api/identity/v2/'),
            DLIBearerAuthAdapter(self)
        )

        self.mount(
            self._environment.sam, DLISamAdapter(self)
        )

        self.mount(
            self._environment.consumption, DLIBearerAuthAdapter(self)
        )

    def _get_decoded_token(self):
        return _decode_token(self.auth_key)

    def _get_expiration_date(self):
        default_timeout = (
            datetime.datetime.utcnow() +
            datetime.timedelta(minutes=55)
        )

        if 'exp' not in self.decoded_token:
            return default_timeout

        return datetime.datetime.utcfromtimestamp(
            self.decoded_token['exp']
        ) - datetime.timedelta(minutes=5)

    def _get_SAM_auth_key(self):
        return _sam_app_flow(self._environment, self.access_id, self.secret_key, origin="SDK")

    def _get_web_auth_key(self, callback=None):

        postbox = base64.urlsafe_b64encode(uuid.uuid4().bytes)\
            .decode('utf-8').replace('=', '')
        str_jwt = None

        if callback is None:
            # todo-would need to resolve callback on identity
            if os.environ.get('DEV_MODE', 'False').lower() == 'true':
                login_url = f"{self._environment.accounts}" \
                            f"/v2/auth/login-postbox" \
                            f"?postbox={postbox}&" \
                            f"target=/v2/auth/postbox_confirmation"
            else:
                login_url = f"{self._environment.catalogue}" \
                            f"{identity_urls.identity_postbox}" \
                            f"?postbox={postbox}&" \
                            f"target=/api/identity/v2/auth/postbox_confirmation"
            if self.show_login_url:
                print(f'Login url is: {login_url}')

            # we need to check that the listener can actually listen
            # before we open the browser - so establish that a listener
            # is up and running, or can listen (not firewalled)
            # else we need to tell the user that their firewall is shut.

            isopen=webbrowser.open(login_url, new=1)
            if not isopen:
                print(f"WARNING: We could not open a usable web browser for authentication purposes, or alternatively,"
                      f" please copy the below:\n\n{login_url}\n\nEnter this into a web browser that you can access, "
                      f"or alternatively, you can use your phone or a web browser on another machine. "
                      f"After this step, by returning here, you will see this console un-blocked.\n"
                      f"If you wish to abort enter Ctrl/Cmd + C on your keyboard.\n\n")
        else:
            callback(0, postbox)

        # Cloudfront caches the calls to this URL with a TTL of
        # one minute. The result is that if the first response is a
        # HTTP status 404 then it keeps that result in cache for one
        # minute. Setting the headers to disable cache just didn't make
        # a difference, but adding a pause before the first call did.
        time.sleep(1)

        while True:
            try:
                #todo-would need to resolve callback on identity to work
                if os.environ.get('DEV_MODE', 'False').lower() == 'true':
                    query = self.get(
                        f"{self._environment.accounts}"
                        f"/v2/auth/postbox"
                        f"?postbox={postbox}",
                    )
                else:
                    query = self.get(
                        f"{self._environment.catalogue}"
                        f"{identity_urls.identity_poll}"
                        f"?postbox={postbox}",
                    )

                if query.ok:
                    str_jwt = query.text
                    _jwt = str.encode(str_jwt)
                    break
            except ConnectionException as e:
                print(
                    "Sorry, the connection timed out. Please try again in "
                    "one minute. If this is your first time trying to connect "
                    "and the problem continues then it is possible you have "
                    "a firewall issue (please contact your IT team to "
                    "check if a firewall rule needs to be added, see "
                    "https://supportlibrary.ihsmarkit.com/display/DLSL/"
                    "Firewalls+and+proxies ).\n\n"
                    "Technical details:"
                    f"{e.message}"
                )
                sys.exit(0)

            except DatalakeException as e:
                # anti-pattern time - to be able to patch session appropriately
                # i need to modify the get, but the responsehook sees the 404
                # prior to the above logic
                if e.response.status_code == 404 or e.response.status_code == 409:
                    time.sleep(0.5)
                elif e.response.status_code == 401:
                    print("We couldn't log you in. A problem was encountered\n"
                          "If this issue persists please contact DL-Support")
                    sys.exit(0)

        if str_jwt and hasattr(self, "use_keyring") and self.use_keyring:
            try:
                keyring.set_password(__product__, self._environment.catalogue,
                                     str_jwt)
            except (Exception, OSError) as e:
                # length issue on Windows > 1280 chars in Windows Credentials
                if os.name == 'nt':
                    lens = 1000
                    chunks = [
                        str_jwt[i:i + lens]
                        for i in range(0, len(str_jwt), lens)
                    ]
                    try:
                        # index
                        keyring.set_password(
                            __product__,
                            self._environment.catalogue,
                            f"**split**{len(chunks)}"
                        )

                        # segments
                        for ix, chunk in enumerate(chunks):
                            keyring.set_password(
                                __product__,
                                self._environment.catalogue + f"-{ix}",
                                chunk
                            )
                    except Exception as e:
                        logging.warning(str(e))
                else:
                    logging.warning(str(e))
        return str_jwt


class BlockAll(CookiePolicy):
    return_ok = set_ok = domain_return_ok = path_return_ok = lambda self, *args, **kwargs: False
    netscape = True
    rfc2965 = hide_cookie2 = False
