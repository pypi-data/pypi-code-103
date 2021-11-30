# -*- coding: utf-8 -*-

import functools
import time
import logging

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from fast_tracker.api.application import Application, application_instance
from fast_tracker.api.transaction import Transaction, current_transaction

from fast_tracker.common.async_proxy import async_proxy, TransactionContext
from fast_tracker.common.encoding_utils import (obfuscate, json_encode,
                                                decode_fast_header, ensure_str)

from fast_tracker.core.attribute import create_attributes, process_user_attribute
from fast_tracker.core.attribute_filter import DST_BROWSER_MONITORING, DST_NONE

from fast_tracker.packages import six

from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import FunctionWrapper, wrap_object

_logger = logging.getLogger(__name__)

_js_agent_header_fragment = '<script type="text/javascript">%s</script>'
_js_agent_footer_fragment = '<script type="text/javascript">' \
                            'window.NREUM||(NREUM={});NREUM.info=%s</script>'

# Seconds since epoch for Jan 1 2000
JAN_1_2000 = time.mktime((2000, 1, 1, 0, 0, 0, 0, 0, 0))
MICROSECOND_MIN = JAN_1_2000 * 1000000.0
MILLISECOND_MIN = JAN_1_2000 * 1000.0


def _parse_time_stamp(time_stamp):
    """
    将时间戳转化成秒
    """

    now = time.time()

    if time_stamp > MICROSECOND_MIN:
        divisor = 1000000.0
    elif time_stamp > MILLISECOND_MIN:
        divisor = 1000.0
    elif time_stamp > JAN_1_2000:
        divisor = 1.0
    else:
        return 0.0

    converted_time = time_stamp / divisor

    if converted_time > now:
        return 0.0

    return converted_time


TRUE_VALUES = {'on', 'true', '1'}
FALSE_VALUES = {'off', 'false', '0'}


def _lookup_environ_setting(environ, name, default=False):
    if name not in environ:
        return default

    flag = environ[name]

    if isinstance(flag, six.string_types):
        flag = flag.lower()

        if flag in TRUE_VALUES:
            return True
        elif flag in FALSE_VALUES:
            return False

    return flag


def _parse_synthetics_header(header):
    synthetics = {}
    version = None

    try:
        if len(header) > 0:
            version = int(header[0])

        if version == 1:
            synthetics['version'] = version
            synthetics['account_id'] = int(header[1])
            synthetics['resource_id'] = header[2]
            synthetics['job_id'] = header[3]
            synthetics['monitor_id'] = header[4]
    except Exception:
        return

    return synthetics


def _remove_query_string(url):
    out = urlparse.urlsplit(url)
    return urlparse.urlunsplit((out.scheme, out.netloc, out.path, '', ''))


def _is_websocket(environ):
    return environ.get('HTTP_UPGRADE', '').lower() == 'websocket'


class WebTransaction(Transaction):
    unicode_error_reported = False
    QUEUE_TIME_HEADERS = ('x-request-start', 'x-queue-start')

    def __init__(self, application, name, group=None, scheme=None, host=None, port=None,
                 request_method=None, request_path=None, query_string=None, headers=None, enabled=None):

        super(WebTransaction, self).__init__(application, enabled)

        if not self.enabled:
            return

        # Inputs
        self._request_uri = request_path
        self._request_method = request_method
        self._request_scheme = scheme
        self._request_host = host
        self._request_params = {}
        self._request_headers = {}

        try:
            self._port = int(port)
        except Exception:
            self._port = None

        # Response
        self._response_headers = {}
        self._response_code = None

        if headers is not None:
            try:
                headers = headers.items()
            except Exception:
                pass

            for k, v in headers:
                k = ensure_str(k)
                if k is not None:
                    self._request_headers[k.lower()] = v

        if query_string and not self._settings.high_security:
            query_string = ensure_str(query_string)
            try:
                params = urlparse.parse_qs(
                    query_string,
                    keep_blank_values=True)
                self._request_params.update(params)
            except Exception:
                pass

        self._process_queue_time()
        self._process_synthetics_header()
        self._process_context_headers()

        if name is not None:
            self.set_transaction_name(name, group, priority=1)
        elif request_path is not None:
            self.set_transaction_name(request_path, 'Uri', priority=1)

        self.rum_header_generated = False
        self.rum_footer_generated = False

    def _process_queue_time(self):
        for queue_time_header in self.QUEUE_TIME_HEADERS:
            value = self._request_headers.get(queue_time_header)
            if not value:
                continue
            value = ensure_str(value)

            try:
                if value.startswith('t='):
                    self.queue_start = _parse_time_stamp(float(value[2:]))
                else:
                    self.queue_start = _parse_time_stamp(float(value))
            except Exception:
                pass

            if self.queue_start > 0.0:
                break

    def _process_synthetics_header(self):
        # Check for Synthetics header

        settings = self._settings

        if settings.synthetics.enabled and \
                settings.trusted_account_ids and \
                settings.encoding_key:

            encoded_header = self._request_headers.get('x-fast-synthetics')
            encoded_header = encoded_header and ensure_str(encoded_header)
            if not encoded_header:
                return

            decoded_header = decode_fast_header(
                encoded_header,
                settings.encoding_key)
            synthetics = _parse_synthetics_header(decoded_header)

            if synthetics and \
                    synthetics['account_id'] in \
                    settings.trusted_account_ids:
                self.synthetics_header = encoded_header
                self.synthetics_resource_id = synthetics['resource_id']
                self.synthetics_job_id = synthetics['job_id']
                self.synthetics_monitor_id = synthetics['monitor_id']

    def _process_context_headers(self):

        if self._settings.distributed_tracing.enabled:
            self.accept_distributed_trace_headers(self._request_headers)
        else:
            client_cross_process_id = \
                self._request_headers.get('x-fast-id')
            txn_header = self._request_headers.get('x-fast-transaction')
            self._process_incoming_cat_headers(client_cross_process_id,
                                               txn_header)

    def process_response(self, status_code, response_headers):
        if not self.enabled:
            return []

        # Extract response headers
        if response_headers:
            try:
                response_headers = response_headers.items()
            except Exception:
                pass

            for header, value in response_headers:
                header = ensure_str(header)
                if header is not None:
                    self._response_headers[header.lower()] = value

        try:
            self._response_code = int(status_code)

            if self._response_code == 304:
                return []
        except Exception:
            pass

        if self.client_cross_process_id is None:
            return []
        try:
            read_length = int(self._request_headers.get('content-length'))
        except Exception:
            read_length = -1

        return self._generate_response_headers(read_length)

    @property
    def agent_attributes(self):
       
        if 'host' in self._request_headers:
            self._add_agent_attribute('request.headers.host',
                                      self._request_headers['host'])
        if self._request_method:
            self._add_agent_attribute('request.method', self._request_method)
        if self._request_uri:
            self._add_agent_attribute('request.uri', self._request_uri)
        try:
            content_length = int(self._response_headers['content-length'])
            self._add_agent_attribute('response.headers.contentLength',
                                      content_length)
        except:
            pass
        if 'content-type' in self._response_headers:
            self._add_agent_attribute('response.headers.contentType',
                                      self._response_headers['content-type'])
        if self._response_code is not None:
            self._add_agent_attribute('response.status',
                                      str(self._response_code))

        return super(WebTransaction, self).agent_attributes

    @property
    def request_parameters_attributes(self):
        attributes_request = []

        if self._request_params:

            r_attrs = {}

            for k, v in self._request_params.items():
                new_key = 'request.parameters.%s' % k
                new_val = ",".join(v)

                final_key, final_val = process_user_attribute(new_key, new_val)

                if final_key:
                    r_attrs[final_key] = final_val

            attributes_request = create_attributes(r_attrs, DST_NONE,
                                                   self._settings.attribute_filter)

        return attributes_request

    def browser_timing_header(self):
        if not self.enabled:
            return ''

        if self._state != self.STATE_RUNNING:
            return ''

        if self.background_task:
            return ''

        if self.ignore_transaction:
            return ''

        if not self._settings:
            return ''

        if not self._settings.browser_monitoring.enabled:
            return ''

        if self.rum_header_generated:
            return ''

        if self._settings.js_agent_loader:
            header = _js_agent_header_fragment % self._settings.js_agent_loader

            try:
                if six.PY2:
                    header = header.encode('ascii')
                else:
                    header.encode('ascii')

            except UnicodeError:
                if not WebTransaction.unicode_error_reported:
                    _logger.error('ASCII encoding of js-agent-header failed.',
                                  header)
                    WebTransaction.unicode_error_reported = True

                header = ''

        else:
            header = ''
        if header:
            self.rum_header_generated = True

        return header

    def browser_timing_footer(self):

        if not self.enabled:
            return ''

        if self._state != self.STATE_RUNNING:
            return ''

        if self.ignore_transaction:
            return ''

        if not self.rum_header_generated:
            return ''

        if self.rum_footer_generated:
            return ''
        self._freeze_path()

        obfuscation_key = self._settings.license_key[:13]

        attributes = {}

        user_attributes = {}
        for attr in self.user_attributes:
            if attr.destinations & DST_BROWSER_MONITORING:
                user_attributes[attr.name] = attr.value

        if user_attributes:
            attributes['u'] = user_attributes

        agent_attributes = {}
        for attr in self.request_parameters_attributes:
            if attr.destinations & DST_BROWSER_MONITORING:
                agent_attributes[attr.name] = attr.value

        if agent_attributes:
            attributes['a'] = agent_attributes

        footer_data = self.browser_monitoring_intrinsics(obfuscation_key)

        if attributes:
            attributes = obfuscate(json_encode(attributes), obfuscation_key)
            footer_data['atts'] = attributes

        footer = _js_agent_footer_fragment % json_encode(footer_data)

        try:
            if six.PY2:
                footer = footer.encode('ascii')
            else:
                footer.encode('ascii')

        except UnicodeError:
            if not WebTransaction.unicode_error_reported:
                _logger.error('ASCII encoding of js-agent-footer failed.', footer)
                WebTransaction.unicode_error_reported = True

            footer = ''

        if footer:
            self.rum_footer_generated = True

        return footer

    def browser_monitoring_intrinsics(self, obfuscation_key):
        txn_name = obfuscate(self.path, obfuscation_key)

        queue_start = self.queue_start or self.start_time
        start_time = self.start_time
        end_time = time.time()

        queue_duration = int((start_time - queue_start) * 1000)
        request_duration = int((end_time - start_time) * 1000)

        intrinsics = {
            "beacon": self._settings.beacon,
            "errorBeacon": self._settings.error_beacon,
            "licenseKey": self._settings.browser_key,
            "applicationID": self._settings.application_id,
            "transactionName": txn_name,
            "queueTime": queue_duration,
            "applicationTime": request_duration,
            "agent": self._settings.js_agent_file,
        }

        if self._settings.browser_monitoring.ssl_for_http is not None:
            ssl_for_http = self._settings.browser_monitoring.ssl_for_http
            intrinsics['sslForHttp'] = ssl_for_http

        return intrinsics


class WSGIHeaderProxy(object):
    def __init__(self, environ):
        self.environ = environ
        self.length = None

    @staticmethod
    def _to_wsgi(key):
        key = key.upper()
        if key == 'CONTENT-LENGTH':
            return 'CONTENT_LENGTH'
        elif key == 'CONTENT-TYPE':
            return 'CONTENT_TYPE'
        return 'HTTP_' + key.replace('-', '_')

    @staticmethod
    def _from_wsgi(key):
        key = key.lower()
        return key[5:].replace('_', '-')

    def __getitem__(self, key):
        wsgi_key = self._to_wsgi(key)
        return self.environ[wsgi_key]

    def __iter__(self):
        for key in self.environ:
            if key == 'CONTENT_LENGTH':
                yield 'content-length', self.environ['CONTENT_LENGTH']
            elif key == 'CONTENT_TYPE':
                yield 'content-type', self.environ['CONTENT_TYPE']
            elif key == 'HTTP_CONTENT_LENGTH' or key == 'HTTP_CONTENT_TYPE':
                # These keys are illegal and should be ignored
                continue
            elif key.startswith('HTTP_'):
                yield self._from_wsgi(key), self.environ[key]

    def __len__(self):
        if self.length is None:
            self.length = sum(1 for _ in iter(self))
        return self.length


class WSGIWebTransaction(WebTransaction):
    MOD_WSGI_HEADERS = ('mod_wsgi.request_start', 'mod_wsgi.queue_start')

    def __init__(self, application, environ):

        enabled = _lookup_environ_setting(environ, 'fast.enabled', None)

        super(WSGIWebTransaction, self).__init__(
            application, name=None, port=environ.get('SERVER_PORT'),
            request_method=environ.get('REQUEST_METHOD'),
            query_string=environ.get('QUERY_STRING'),
            headers=iter(WSGIHeaderProxy(environ)),
            enabled=enabled)

        if _is_websocket(environ):
            self.autorum_disabled = True
            self.enabled = False

        if not self.enabled:
            return
        settings = self._settings

        self.background_task = _lookup_environ_setting(environ, 'fast.set_background_task', False)
        self.ignore_transaction = _lookup_environ_setting(environ, 'fast.ignore_transaction', False)
        self.suppress_apdex = _lookup_environ_setting(environ, 'fast.suppress_apdex_metric', False)
        self.suppress_transaction_trace = _lookup_environ_setting(environ, 'fast.suppress_transaction_trace', False)
        self.capture_params = _lookup_environ_setting(environ, 'fast.capture_request_params', settings.capture_params)
        self.autorum_disabled = _lookup_environ_setting(environ, 'fast.disable_browser_autorum',
                                                        not settings.browser_monitoring.auto_instrument)

        if settings.high_security:
            self.capture_params = False

        if self.capture_params is False:
            self._request_params.clear()

        request_uri = environ.get('REQUEST_URI', None)
        if request_uri is None:
            request_uri = environ.get('RAW_URI', None)

        script_name = environ.get('SCRIPT_NAME', None)
        path_info = environ.get('PATH_INFO', None)

        self._request_uri = request_uri

        if self._request_uri is not None:
            self._request_uri = urlparse.urlparse(self._request_uri)[2]

        if script_name is not None or path_info is not None:
            if path_info is None:
                path = script_name
            elif script_name is None:
                path = path_info
            else:
                path = script_name + path_info

            self.set_transaction_name(path, 'Uri', priority=1)

            if self._request_uri is None:
                self._request_uri = path
        else:
            if self._request_uri is not None:
                self.set_transaction_name(self._request_uri, 'Uri', priority=1)

        for queue_time_header in self.MOD_WSGI_HEADERS:
            if self.queue_start > 0.0:
                break

            value = environ.get(queue_time_header)
            if not value:
                continue

            try:
                if value.startswith('t='):
                    try:
                        self.queue_start = _parse_time_stamp(float(value[2:]))
                    except Exception:
                        pass
                else:
                    try:
                        self.queue_start = _parse_time_stamp(float(value))
                    except Exception:
                        pass
            except Exception:
                pass

        self.rum_header_generated = False
        self.rum_footer_generated = False

    def __exit__(self, exc, value, tb):
        self.record_custom_metric('Python/WSGI/Input/Bytes', self._bytes_read)
        self.record_custom_metric('Python/WSGI/Input/Time', self.read_duration)
        self.record_custom_metric('Python/WSGI/Input/Calls/read', self._calls_read)
        self.record_custom_metric('Python/WSGI/Input/Calls/readline', self._calls_readline)
        self.record_custom_metric('Python/WSGI/Input/Calls/readlines', self._calls_readlines)
        self.record_custom_metric('Python/WSGI/Output/Bytes', self._bytes_sent)
        self.record_custom_metric('Python/WSGI/Output/Time', self.sent_duration)
        self.record_custom_metric('Python/WSGI/Output/Calls/yield', self._calls_yield)
        self.record_custom_metric('Python/WSGI/Output/Calls/write', self._calls_write)

        return super(WSGIWebTransaction, self).__exit__(exc, value, tb)

    @property
    def agent_attributes(self):

        if self.capture_params is True:
            for k, v in self._request_params.items():
                new_key = 'request.parameters.%s' % k
                new_val = ",".join(v)

                final_key, final_val = process_user_attribute(new_key,
                                                              new_val)

                if final_key:
                    self._add_agent_attribute(final_key, final_val)

            self._request_params.clear()
        return super(WSGIWebTransaction, self).agent_attributes

    def process_response(self, status, response_headers, *args):
        try:
            status = status.split(' ', 1)[0]
        except Exception:
            status = None
        return super(WSGIWebTransaction, self).process_response(
            status, response_headers)


def WebTransactionWrapper(wrapped, application=None, name=None, group=None,
                          scheme=None, host=None, port=None, request_method=None,
                          request_path=None, query_string=None, headers=None):
    def wrapper(wrapped, instance, args, kwargs):

        transaction = current_transaction(active_only=False)
        if transaction:
            return wrapped(*args, **kwargs)

        if type(application) != Application:
            _application = application_instance(application)
        else:
            _application = application

        if callable(name):
            if instance is not None:
                _name = name(instance, *args, **kwargs)
            else:
                _name = name(*args, **kwargs)
        elif name is None:
            _name = callable_name(wrapped)
        else:
            _name = name

        if callable(group):
            if instance is not None:
                _group = group(instance, *args, **kwargs)
            else:
                _group = group(*args, **kwargs)
        else:
            _group = group

        if callable(scheme):
            if instance is not None:
                _scheme = scheme(instance, *args, **kwargs)
            else:
                _scheme = scheme(*args, **kwargs)
        else:
            _scheme = scheme

        if callable(host):
            if instance is not None:
                _host = host(instance, *args, **kwargs)
            else:
                _host = host(*args, **kwargs)
        else:
            _host = host

        if callable(port):
            if instance is not None:
                _port = port(instance, *args, **kwargs)
            else:
                _port = port(*args, **kwargs)
        else:
            _port = port

        if callable(request_method):
            if instance is not None:
                _request_method = request_method(instance, *args, **kwargs)
            else:
                _request_method = request_method(*args, **kwargs)
        else:
            _request_method = request_method

        if callable(request_path):
            if instance is not None:
                _request_path = request_path(instance, *args, **kwargs)
            else:
                _request_path = request_path(*args, **kwargs)
        else:
            _request_path = request_path

        if callable(query_string):
            if instance is not None:
                _query_string = query_string(instance, *args, **kwargs)
            else:
                _query_string = query_string(*args, **kwargs)
        else:
            _query_string = query_string

        if callable(headers):
            if instance is not None:
                _headers = headers(instance, *args, **kwargs)
            else:
                _headers = headers(*args, **kwargs)
        else:
            _headers = headers

        transaction = WebTransaction(
            _application, _name, _group, _scheme, _host, _port,
            _request_method, _request_path, _query_string, _headers)

        proxy = async_proxy(wrapped)
        if proxy:
            context_manager = TransactionContext(transaction)
            return proxy(wrapped(*args, **kwargs), context_manager)

        with transaction:
            return wrapped(*args, **kwargs)

    return FunctionWrapper(wrapped, wrapper)


def web_transaction(application=None, name=None, group=None,
                    scheme=None, host=None, port=None, request_method=None,
                    request_path=None, query_string=None, headers=None):
    return functools.partial(WebTransactionWrapper,
                             application=application, name=name, group=group,
                             scheme=scheme, host=host, port=port, request_method=request_method,
                             request_path=request_path, query_string=query_string,
                             headers=headers)


def wrap_web_transaction(module, object_path,
                         application=None, name=None, group=None,
                         scheme=None, host=None, port=None, request_method=None,
                         request_path=None, query_string=None, headers=None):
    return wrap_object(module, object_path, WebTransactionWrapper,
                       (application, name, group, scheme, host, port, request_method,
                        request_path, query_string, headers))
