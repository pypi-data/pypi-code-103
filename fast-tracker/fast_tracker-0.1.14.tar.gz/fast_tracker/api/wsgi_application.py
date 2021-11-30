# -*- coding: utf-8 -*-
import sys
import time
import logging
import functools

from fast_tracker.api.application import application_instance
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.time_trace import record_exception
from fast_tracker.api.web_transaction import WSGIWebTransaction
from fast_tracker.api.function_trace import FunctionTrace
from fast_tracker.api.html_insertion import insert_html_snippet, verify_body_exists

from fast_tracker.common.object_names import callable_name
from fast_tracker.common.object_wrapper import wrap_object, FunctionWrapper

from fast_tracker.packages import six

_logger = logging.getLogger(__name__)


class _WSGIApplicationIterable(object):

    def __init__(self, transaction, generator):
        self.transaction = transaction
        self.generator = generator
        self.response_trace = None
        self.closed = False

    def __iter__(self):
        self.start_trace()

        try:
            for item in self.generator:
                try:
                    self.transaction._calls_yield += 1
                    self.transaction._bytes_sent += len(item)
                except Exception:
                    pass

                yield item

        except GeneratorExit:
            raise

        except:  # Catch all
            record_exception()
            raise

        finally:
            self.close()

    def start_trace(self):
        if not self.transaction._sent_start:
            self.transaction._sent_start = time.time()

        if not self.response_trace:
            self.response_trace = FunctionTrace(
                name='Response', group='Python/WSGI')
            self.response_trace.__enter__()

    def close(self):
        if self.closed:
            return

        if self.response_trace:
            self.response_trace.__exit__(None, None, None)
            self.response_trace = None

        try:
            with FunctionTrace(
                    name='Finalize', group='Python/WSGI'):

                if isinstance(self.generator, _WSGIApplicationMiddleware):
                    self.generator.close()

                elif hasattr(self.generator, 'close'):
                    name = callable_name(self.generator.close)
                    with FunctionTrace(name):
                        self.generator.close()

        except:  # Catch all
            self.transaction.__exit__(*sys.exc_info())
            raise

        else:
            self.transaction.__exit__(None, None, None)
            self.transaction._sent_end = time.time()

        finally:
            self.closed = True


class _WSGIInputWrapper(object):

    def __init__(self, transaction, input):
        self.__transaction = transaction
        self.__input = input

    def __getattr__(self, name):
        return getattr(self.__input, name)

    def close(self):
        if hasattr(self.__input, 'close'):
            self.__input.close()

    def read(self, *args, **kwargs):
        if not self.__transaction._read_start:
            self.__transaction._read_start = time.time()
        try:
            data = self.__input.read(*args, **kwargs)
            try:
                self.__transaction._calls_read += 1
                self.__transaction._bytes_read += len(data)
            except Exception:
                pass
        finally:
            self.__transaction._read_end = time.time()
        return data

    def readline(self, *args, **kwargs):
        if not self.__transaction._read_start:
            self.__transaction._read_start = time.time()
        try:
            line = self.__input.readline(*args, **kwargs)
            try:
                self.__transaction._calls_readline += 1
                self.__transaction._bytes_read += len(line)
            except Exception:
                pass
        finally:
            self.__transaction._read_end = time.time()
        return line

    def readlines(self, *args, **kwargs):
        if not self.__transaction._read_start:
            self.__transaction._read_start = time.time()
        try:
            lines = self.__input.readlines(*args, **kwargs)
            try:
                self.__transaction._calls_readlines += 1
                self.__transaction._bytes_read += sum(map(len, lines))
            except Exception:
                pass
        finally:
            self.__transaction._read_end = time.time()
        return lines


class _WSGIApplicationMiddleware(object):
    search_maximum = 64 * 1024

    def __init__(self, application, environ, start_response, transaction):
        self.application = application

        self.pass_through = True

        self.request_environ = environ
        self.outer_start_response = start_response
        self.outer_write = None

        self.transaction = transaction

        self.response_status = None
        self.response_headers = []
        self.response_args = ()

        self.content_length = None

        self.response_length = 0
        self.response_data = []

        settings = transaction.settings

        self.debug = settings and settings.debug.log_autorum_middleware

        self.iterable = self.application(self.request_environ,
                                         self.start_response)

    def process_data(self, data):

        def html_to_be_inserted():
            header = self.transaction.browser_timing_header()

            if not header:
                return b''

            footer = self.transaction.browser_timing_footer()

            return six.b(header) + six.b(footer)

        if not self.response_data:
            modified = insert_html_snippet(data, html_to_be_inserted)

            if modified is not None:
                if self.debug:
                    _logger.debug('RUM insertion from WSGI middleware '
                                  'triggered on first yielded string from '
                                  'response. Bytes added was %r.',
                                  len(modified) - len(data))

                if self.content_length is not None:
                    length = len(modified) - len(data)
                    self.content_length += length

                return [modified]

        if not self.response_data or not verify_body_exists(data):
            self.response_length += len(data)
            self.response_data.append(data)

            if self.response_length >= self.search_maximum:
                buffered_data = self.response_data
                self.response_data = []
                return buffered_data

            return

        if self.response_data:
            self.response_data.append(data)
            data = b''.join(self.response_data)
            self.response_data = []

        modified = insert_html_snippet(data, html_to_be_inserted)

        if modified is not None:
            if self.debug:
                _logger.debug('RUM insertion from WSGI middleware '
                              'triggered on subsequent string yielded from '
                              'response. Bytes added was %r.',
                              len(modified) - len(data))

            if self.content_length is not None:
                length = len(modified) - len(data)
                self.content_length += length

            return [modified]
        return [data]

    def flush_headers(self):
        if self.content_length is not None:
            header = ('Content-Length', str(self.content_length))
            self.response_headers.append(header)

        self.outer_write = self.outer_start_response(self.response_status,
                                                     self.response_headers, *self.response_args)

    def inner_write(self, data):

        self.pass_through = True

        if self.outer_write is None:
            self.flush_headers()

        if self.response_data:
            for buffered_data in self.response_data:
                self.outer_write(buffered_data)
            self.response_data = []

        return self.outer_write(data)

    def start_response(self, status, response_headers, *args):

        self.pass_through = True

        self.response_status = status
        self.response_headers = response_headers
        self.response_args = args

        self.content_length = None
        if self.transaction.autorum_disabled or getattr(self.transaction, 'rum_header_generated', None):
            self.flush_headers()
            self.pass_through = True

            return self.inner_write

        pass_through = False

        headers = []

        content_type = None
        content_length = None
        content_encoding = None
        content_disposition = None

        for (name, value) in response_headers:
            _name = name.lower()

            if _name == 'content-length':
                try:
                    content_length = int(value)
                    continue

                except ValueError:
                    pass_through = True

            elif _name == 'content-type':
                content_type = value

            elif _name == 'content-encoding':
                content_encoding = value

            elif _name == 'content-disposition':
                content_disposition = value

            headers.append((name, value))

        def should_insert_html():
            if pass_through:
                return False

            if content_encoding is not None:

                return False

            if (content_disposition is not None and
                    content_disposition.split(';')[0].strip().lower() ==
                    'attachment'):
                return False

            if content_type is None:
                return False

            settings = self.transaction.settings
            if settings:
                allowed_content_type = settings.browser_monitoring.content_type

                if content_type.split(';')[0] not in allowed_content_type:
                    return False

            return True

        if should_insert_html():
            self.pass_through = False

            self.content_length = content_length
            self.response_headers = headers

        if self.pass_through:
            self.flush_headers()

        return self.inner_write

    def close(self):

        if hasattr(self.iterable, 'close'):
            name = callable_name(self.iterable.close)
            with FunctionTrace(name):
                self.iterable.close()

    def __iter__(self):
        for data in self.iterable:

            if self.pass_through:
                yield data

                continue

            if self.outer_write is None:
                # Ignore any empty strings.

                if not data:
                    continue

                buffered_data = self.process_data(data)

                if buffered_data is None:
                    continue

                self.flush_headers()
                self.pass_through = True

                for data in buffered_data:
                    yield data

            else:

                yield data

        if self.outer_write is None:
            self.flush_headers()
            self.pass_through = True

        if self.response_data:
            for data in self.response_data:
                yield data


def WSGIApplicationWrapper(wrapped, application=None, name=None,
                           group=None, framework=None):
    if framework is not None and not isinstance(framework, tuple):
        framework = (framework, None)

    def _nr_wsgi_application_wrapper_(wrapped, instance, args, kwargs):
        transaction = current_transaction(active_only=False)

        if transaction:
            if transaction.ignore_transaction or transaction.stopped:
                return wrapped(*args, **kwargs)

            if framework:
                transaction.add_framework_info(
                    name=framework[0], version=framework[1])
            settings = transaction._settings
            if name is None and settings:
                if framework is not None:
                    naming_scheme = settings.transaction_name.naming_scheme
                    if naming_scheme in (None, 'framework'):
                        transaction.set_transaction_name(
                            callable_name(wrapped), priority=1)

            elif name:
                transaction.set_transaction_name(name, group, priority=1)

            return wrapped(*args, **kwargs)

        def _args(environ, start_response, *args, **kwargs):
            return environ, start_response

        environ, start_response = _args(*args, **kwargs)

        target_application = application

        if 'fast.app_name' in environ:
            app_name = environ['fast.app_name']
            target_application = application_instance()
        else:
            if not hasattr(application, 'activate'):
             
                target_application = application_instance()

        transaction = WSGIWebTransaction(target_application, environ)
        transaction.__enter__()

        if framework:
            transaction.add_framework_info(
                name=framework[0], version=framework[1])

        settings = transaction._settings

        if name is None and settings:
            naming_scheme = settings.transaction_name.naming_scheme

            if framework is not None:
                if naming_scheme in (None, 'framework'):
                    transaction.set_transaction_name(
                        callable_name(wrapped), priority=1)

            elif naming_scheme in ('component', 'framework'):
                transaction.set_transaction_name(
                    callable_name(wrapped), priority=1)

        elif name:
            transaction.set_transaction_name(name, group, priority=1)

        def _start_response(status, response_headers, *args):
            additional_headers = transaction.process_response(
                status, response_headers, *args)

            _write = start_response(status,
                                    response_headers + additional_headers, *args)

            def write(data):
                if not transaction._sent_start:
                    transaction._sent_start = time.time()
                result = _write(data)
                transaction._calls_write += 1
                try:
                    transaction._bytes_sent += len(data)
                except Exception:
                    pass
                transaction._sent_end = time.time()
                return result

            return write

        try:
            # Should always exist, but check as test harnesses may not
            # have it.

            if 'wsgi.input' in environ:
                environ['wsgi.input'] = _WSGIInputWrapper(transaction,
                                                          environ['wsgi.input'])
            with FunctionTrace(
                    name='Application', group='Python/WSGI'):
                with FunctionTrace(name=callable_name(wrapped)):
                    if not (settings and settings.browser_monitoring.enabled and
                            not transaction.autorum_disabled):
                        result = _WSGIApplicationMiddleware(wrapped,
                                                            environ, _start_response, transaction)
                    else:
                        result = wrapped(environ, _start_response)

        except Exception as e:  # Catch all
            transaction._response_code = 500
            transaction.__exit__(*sys.exc_info())
            raise

        return _WSGIApplicationIterable(transaction, result)

    return FunctionWrapper(wrapped, _nr_wsgi_application_wrapper_)


def wsgi_application(application=None, name=None, group=None, framework=None):
    return functools.partial(WSGIApplicationWrapper, application=application,
                             name=name, group=group, framework=framework)


def wrap_wsgi_application(module, object_path, application=None,
                          name=None, group=None, framework=None):
    wrap_object(module, object_path, WSGIApplicationWrapper,
                (application, name, group, framework))
