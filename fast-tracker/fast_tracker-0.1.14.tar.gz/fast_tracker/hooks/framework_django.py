# -*- coding: utf-8 -*-

import sys
import threading
import logging
import functools

from fast_tracker.packages import six

from fast_tracker.api.application import register_application
from fast_tracker.api.background_task import BackgroundTask
from fast_tracker.api.error_trace import wrap_error_trace
from fast_tracker.api.function_trace import (FunctionTrace, wrap_function_trace,
                                             FunctionTraceWrapper)
from fast_tracker.api.html_insertion import insert_html_snippet
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.time_trace import record_exception
from fast_tracker.api.transaction_name import wrap_transaction_name
from fast_tracker.api.wsgi_application import WSGIApplicationWrapper

from fast_tracker.common.object_wrapper import (FunctionWrapper, wrap_in_function,
                                                wrap_post_function, wrap_function_wrapper, function_wrapper)
from fast_tracker.common.object_names import callable_name
from fast_tracker.config import extra_settings
from fast_tracker.core.config import global_settings, ignore_status_code

_logger = logging.getLogger(__name__)

_boolean_states = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False
}


def _setting_boolean(value):
    if value.lower() not in _boolean_states:
        raise ValueError('Not a boolean: %s' % value)
    return _boolean_states[value.lower()]


def _setting_set(value):
    return set(value.split())


_settings_types = {
    'browser_monitoring.auto_instrument': _setting_boolean,
    'instrumentation.templates.inclusion_tag': _setting_set,
    'instrumentation.background_task.startup_timeout': float,
    'instrumentation.scripts.django_admin': _setting_set,
}

_settings_defaults = {
    'browser_monitoring.auto_instrument': True,
    'instrumentation.templates.inclusion_tag': set(),
    'instrumentation.background_task.startup_timeout': 10.0,
    'instrumentation.scripts.django_admin': set(),
}

django_settings = extra_settings('import-hook:django',
                                 types=_settings_types, defaults=_settings_defaults)


def should_add_browser_timing(response, transaction):

    if hasattr(response, 'streaming_content'):
        return False
    if not transaction:
        return False
    if not transaction.settings.browser_monitoring.enabled:
        return False

    if transaction.autorum_disabled:
        return False

    if not django_settings.browser_monitoring.auto_instrument:
        return False

    if transaction.rum_header_generated:
        return False

    ctype = response.get('Content-Type', '').lower().split(';')[0]

    if ctype not in transaction.settings.browser_monitoring.content_type:
        return False

    if response.has_header('Content-Encoding'):
        return False
    cdisposition = response.get('Content-Disposition', '').lower()

    if cdisposition.split(';')[0].strip().lower() == 'attachment':
        return False

    return True


def browser_timing_insertion(response, transaction):
    header = transaction.browser_timing_header()

    if not header:
        return response

    def html_to_be_inserted():
        return six.b(header) + six.b(transaction.browser_timing_footer())

    result = insert_html_snippet(response.content, html_to_be_inserted)

    if result is not None:
        if transaction.settings.debug.log_autorum_middleware:
            _logger.debug('RUM insertion from Django middleware '
                          'triggered. Bytes added was %r.',
                          len(result) - len(response.content))

        response.content = result

        if response.get('Content-Length', None):
            response['Content-Length'] = str(len(response.content))

    return response


def fast_browser_timing_header():
    from django.utils.safestring import mark_safe

    transaction = current_transaction()
    return transaction and mark_safe(transaction.browser_timing_header()) or ''


def fast_browser_timing_footer():
    from django.utils.safestring import mark_safe

    transaction = current_transaction()
    return transaction and mark_safe(transaction.browser_timing_footer()) or ''


middleware_instrumentation_lock = threading.Lock()


def wrap_leading_middleware(middleware):

    def wrapper(wrapped):

        name = callable_name(wrapped)

        def wrapper(wrapped, instance, args, kwargs):
            transaction = current_transaction()

            if transaction is None:
                return wrapped(*args, **kwargs)

            before = (transaction.name, transaction.group)

            with FunctionTrace(name=name):
                try:
                    return wrapped(*args, **kwargs)

                finally:
                    after = (transaction.name, transaction.group)
                    if before == after:
                        transaction.set_transaction_name(name, priority=2)

        return FunctionWrapper(wrapped, wrapper)

    for wrapped in middleware:
        yield wrapper(wrapped)


def wrap_view_middleware(middleware):

    def wrapper(wrapped):
        name = callable_name(wrapped)

        def wrapper(wrapped, instance, args, kwargs):
            transaction = current_transaction()

            def _wrapped(request, view_func, view_args, view_kwargs):

                if hasattr(view_func, '_nr_last_object'):
                    view_func = view_func._nr_last_object

                return wrapped(request, view_func, view_args, view_kwargs)

            if transaction is None:
                return _wrapped(*args, **kwargs)

            before = (transaction.name, transaction.group)

            with FunctionTrace(name=name):
                try:
                    return _wrapped(*args, **kwargs)

                finally:

                    after = (transaction.name, transaction.group)
                    if before == after:
                        transaction.set_transaction_name(name, priority=2)

        return FunctionWrapper(wrapped, wrapper)

    for wrapped in middleware:
        yield wrapper(wrapped)


def wrap_trailing_middleware(middleware):

    def wrapper(wrapped):
        name = callable_name(wrapped)

        def wrapper(wrapped, instance, args, kwargs):
            with FunctionTrace(name=name):
                return wrapped(*args, **kwargs)

        return FunctionWrapper(wrapped, wrapper)

    for wrapped in middleware:
        yield wrapper(wrapped)


def insert_and_wrap_middleware(handler, *args, **kwargs):

    global middleware_instrumentation_lock

    if not middleware_instrumentation_lock:
        return

    lock = middleware_instrumentation_lock

    lock.acquire()

    # Check again in case two threads grab lock at same time.

    if not middleware_instrumentation_lock:
        lock.release()
        return

    middleware_instrumentation_lock = None

    try:

        if hasattr(handler, '_request_middleware'):
            handler._request_middleware = list(
                wrap_leading_middleware(
                    handler._request_middleware))

        if hasattr(handler, '_view_middleware'):
            handler._view_middleware = list(
                wrap_leading_middleware(
                    handler._view_middleware))

        if hasattr(handler, '_template_response_middleware'):
            handler._template_response_middleware = list(
                wrap_trailing_middleware(
                    handler._template_response_middleware))

        if hasattr(handler, '_response_middleware'):
            handler._response_middleware = list(
                wrap_trailing_middleware(
                    handler._response_middleware))

        if hasattr(handler, '_exception_middleware'):
            handler._exception_middleware = list(
                wrap_trailing_middleware(
                    handler._exception_middleware))

    finally:
        lock.release()


def _nr_wrapper_GZipMiddleware_process_response_(wrapped, instance, args,
                                                 kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    def _bind_params(request, response, *args, **kwargs):
        return request, response

    request, response = _bind_params(*args, **kwargs)

    if should_add_browser_timing(response, transaction):
        with FunctionTrace(
                name=callable_name(browser_timing_insertion)):
            response_with_browser = browser_timing_insertion(
                response, transaction)

        return wrapped(request, response_with_browser)

    return wrapped(request, response)


def _bind_get_response(request, *args, **kwargs):
    return request


def _nr_wrapper_BaseHandler_get_response_(wrapped, instance, args, kwargs):
    response = wrapped(*args, **kwargs)

    transaction = current_transaction()

    if transaction is None:
        return response

    request = _bind_get_response(*args, **kwargs)

    if hasattr(request, '_nr_exc_info'):
        if not ignore_status_code(response.status_code):
            record_exception(*request._nr_exc_info)
        delattr(request, '_nr_exc_info')

    return response


def instrument_django_core_handlers_base(module):
    wrap_post_function(module, 'BaseHandler.load_middleware',
                       insert_and_wrap_middleware)

    wrap_function_wrapper(module, 'BaseHandler.get_response',
                          _nr_wrapper_BaseHandler_get_response_)


def instrument_django_gzip_middleware(module):
    wrap_function_wrapper(module, 'GZipMiddleware.process_response',
                          _nr_wrapper_GZipMiddleware_process_response_)


def wrap_handle_uncaught_exception(middleware):

    name = callable_name(middleware)

    def wrapper(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)

        def _wrapped(request, resolver, exc_info):
            transaction.set_transaction_name(name, priority=1)
            record_exception(*exc_info)

            try:
                return wrapped(request, resolver, exc_info)

            except:  # Catch all
                record_exception()
                raise

        with FunctionTrace(name=name):
            return _wrapped(*args, **kwargs)

    return FunctionWrapper(middleware, wrapper)


def instrument_django_core_handlers_wsgi(module):

    import django

    framework = ('Django', django.get_version())

    module.WSGIHandler.__call__ = WSGIApplicationWrapper(
        module.WSGIHandler.__call__, framework=framework)

    if hasattr(module.WSGIHandler, 'handle_uncaught_exception'):
        module.WSGIHandler.handle_uncaught_exception = (
            wrap_handle_uncaught_exception(
                module.WSGIHandler.handle_uncaught_exception))


def wrap_view_handler(wrapped, priority=3):

    if hasattr(wrapped, '_nr_django_view_handler'):
        return wrapped

    name = callable_name(wrapped)

    def wrapper(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)

        transaction.set_transaction_name(name, priority=priority)

        with FunctionTrace(name=name):
            try:
                return wrapped(*args, **kwargs)

            except:  # Catch all
                exc_info = sys.exc_info()
                try:
                    # Store exc_info on the request to check response code
                    # prior to reporting
                    args[0]._nr_exc_info = exc_info
                except:
                    record_exception(*exc_info)
                raise

    result = FunctionWrapper(wrapped, wrapper)
    result._nr_django_view_handler = True

    return result


def wrap_url_resolver(wrapped):
    name = callable_name(wrapped)

    def wrapper(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)

        if hasattr(transaction, '_nr_django_url_resolver'):
            return wrapped(*args, **kwargs)

        transaction._nr_django_url_resolver = True

        def _wrapped(path):

            with FunctionTrace(name=name, label=path):
                result = wrapped(path)

                if type(result) is tuple:
                    callback, callback_args, callback_kwargs = result
                    result = (wrap_view_handler(callback, priority=5),
                              callback_args, callback_kwargs)
                else:
                    result.func = wrap_view_handler(result.func, priority=5)

                return result

        try:
            return _wrapped(*args, **kwargs)

        finally:
            del transaction._nr_django_url_resolver

    return FunctionWrapper(wrapped, wrapper)


def wrap_url_resolver_nnn(wrapped, priority=1):

    name = callable_name(wrapped)

    def wrapper(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)

        with FunctionTrace(name=name):
            callback, param_dict = wrapped(*args, **kwargs)
            return (wrap_view_handler(callback, priority=priority),
                    param_dict)

    return FunctionWrapper(wrapped, wrapper)


def wrap_url_reverse(wrapped):

    def wrapper(wrapped, instance, args, kwargs):
        def execute(viewname, *args, **kwargs):
            if hasattr(viewname, '_nr_last_object'):
                viewname = viewname._nr_last_object
            return wrapped(viewname, *args, **kwargs)

        return execute(*args, **kwargs)

    return FunctionWrapper(wrapped, wrapper)


def instrument_django_core_urlresolvers(module):

    wrap_error_trace(module, 'get_callable')

    if hasattr(module, 'RegexURLResolver'):
        urlresolver = module.RegexURLResolver
    else:
        urlresolver = module.URLResolver

    urlresolver.resolve = wrap_url_resolver(
        urlresolver.resolve)

    if hasattr(urlresolver, 'resolve403'):
        urlresolver.resolve403 = wrap_url_resolver_nnn(
            urlresolver.resolve403, priority=3)

    if hasattr(urlresolver, 'resolve404'):
        urlresolver.resolve404 = wrap_url_resolver_nnn(
            urlresolver.resolve404, priority=3)

    if hasattr(urlresolver, 'resolve500'):
        urlresolver.resolve500 = wrap_url_resolver_nnn(
            urlresolver.resolve500, priority=1)

    if hasattr(urlresolver, 'resolve_error_handler'):
        urlresolver.resolve_error_handler = wrap_url_resolver_nnn(
            urlresolver.resolve_error_handler, priority=1)

    if hasattr(module, 'reverse'):
        module.reverse = wrap_url_reverse(module.reverse)


def instrument_django_urls_base(module):

    if hasattr(module, 'reverse'):
        module.reverse = wrap_url_reverse(module.reverse)


def instrument_django_template(module):

    def template_name(template, *args):
        return template.name

    if hasattr(module.Template, '_render'):
        wrap_function_trace(module, 'Template._render',
                            name=template_name, group='Template/Render')
    else:
        wrap_function_trace(module, 'Template.render',
                            name=template_name, group='Template/Render')

    if not hasattr(module, 'libraries'):
        return

    library = module.Library()
    library.simple_tag(fast_browser_timing_header)
    library.simple_tag(fast_browser_timing_footer)

    module.libraries['django.templatetags.fast_tracker'] = library


def wrap_template_block(wrapped):
    def wrapper(wrapped, instance, args, kwargs):
        with FunctionTrace(name=instance.name,
                           group='Template/Block'):
            return wrapped(*args, **kwargs)

    return FunctionWrapper(wrapped, wrapper)


def instrument_django_template_loader_tags(module):

    module.BlockNode.render = wrap_template_block(module.BlockNode.render)


def instrument_django_core_servers_basehttp(module):

    def wrap_wsgi_application_entry_point(server, application, **kwargs):
        return ((server, WSGIApplicationWrapper(application,
                                                framework='Django'),), kwargs)

    if (not hasattr(module, 'simple_server') and
            hasattr(module.ServerHandler, 'run')):

        def run(self, application):
            try:
                self.setup_environ()
                self.result = application(self.environ, self.start_response)
                self.finish_response()
            except Exception:
                self.handle_error()
            finally:
                self.close()

        def close(self):
            if self.result is not None:
                try:
                    self.request_handler.log_request(
                        self.status.split(' ', 1)[0], self.bytes_sent)
                finally:
                    try:
                        if hasattr(self.result, 'close'):
                            self.result.close()
                    finally:
                        self.result = None
                        self.headers = None
                        self.status = None
                        self.environ = None
                        self.bytes_sent = 0
                        self.headers_sent = False

        wrap_in_function(module, 'ServerHandler.run',
                         wrap_wsgi_application_entry_point)


def instrument_django_contrib_staticfiles_views(module):
    if not hasattr(module.serve, '_nr_django_view_handler'):
        module.serve = wrap_view_handler(module.serve, priority=3)


def instrument_django_contrib_staticfiles_handlers(module):
    wrap_transaction_name(module, 'StaticFilesHandler.serve')


def instrument_django_views_debug(module):

    module.technical_404_response = wrap_view_handler(
        module.technical_404_response, priority=3)
    module.technical_500_response = wrap_view_handler(
        module.technical_500_response, priority=1)


def wrap_view_dispatch(wrapped):

    def wrapper(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)

        def _args(request, *args, **kwargs):
            return request

        view = instance
        request = _args(*args, **kwargs)

        if request.method.lower() in view.http_method_names:
            handler = getattr(view, request.method.lower(),
                              view.http_method_not_allowed)
        else:
            handler = view.http_method_not_allowed

        name = callable_name(handler)

        priority = 4

        if transaction.group == 'Function':
            if transaction.name == callable_name(view):
                priority = 5

        transaction.set_transaction_name(name, priority=priority)

        with FunctionTrace(name=name):
            return wrapped(*args, **kwargs)

    return FunctionWrapper(wrapped, wrapper)


def instrument_django_views_generic_base(module):
    module.View.dispatch = wrap_view_dispatch(module.View.dispatch)


def instrument_django_http_multipartparser(module):
    wrap_function_trace(module, 'MultiPartParser.parse')


def instrument_django_core_mail(module):
    wrap_function_trace(module, 'mail_admins')
    wrap_function_trace(module, 'mail_managers')
    wrap_function_trace(module, 'send_mail')


def instrument_django_core_mail_message(module):
    wrap_function_trace(module, 'EmailMessage.send')


def _nr_wrapper_BaseCommand___init___(wrapped, instance, args, kwargs):
    instance.handle = FunctionTraceWrapper(instance.handle)
    if hasattr(instance, 'handle_noargs'):
        instance.handle_noargs = FunctionTraceWrapper(instance.handle_noargs)
    return wrapped(*args, **kwargs)


def _nr_wrapper_BaseCommand_run_from_argv_(wrapped, instance, args, kwargs):
    def _args(argv, *args, **kwargs):
        return argv

    _argv = _args(*args, **kwargs)

    subcommand = _argv[1]

    commands = django_settings.instrumentation.scripts.django_admin
    startup_timeout = \
        django_settings.instrumentation.background_task.startup_timeout

    if subcommand not in commands:
        return wrapped(*args, **kwargs)

    application = register_application(timeout=startup_timeout)

    with BackgroundTask(application, subcommand, 'Django'):
        return wrapped(*args, **kwargs)


def instrument_django_core_management_base(module):
    wrap_function_wrapper(module, 'BaseCommand.__init__',
                          _nr_wrapper_BaseCommand___init___)
    wrap_function_wrapper(module, 'BaseCommand.run_from_argv',
                          _nr_wrapper_BaseCommand_run_from_argv_)


@function_wrapper
def _nr_wrapper_django_inclusion_tag_wrapper_(wrapped, instance,
                                              args, kwargs):
    name = hasattr(wrapped, '__name__') and wrapped.__name__

    if name is None:
        return wrapped(*args, **kwargs)

    qualname = callable_name(wrapped)

    tags = django_settings.instrumentation.templates.inclusion_tag

    if '*' not in tags and name not in tags and qualname not in tags:
        return wrapped(*args, **kwargs)

    with FunctionTrace(name, group='Template/Tag'):
        return wrapped(*args, **kwargs)


@function_wrapper
def _nr_wrapper_django_inclusion_tag_decorator_(wrapped, instance,
                                                args, kwargs):
    def _bind_params(func, *args, **kwargs):
        return func, args, kwargs

    func, _args, _kwargs = _bind_params(*args, **kwargs)

    func = _nr_wrapper_django_inclusion_tag_wrapper_(func)

    return wrapped(func, *_args, **_kwargs)


def _nr_wrapper_django_template_base_Library_inclusion_tag_(wrapped,
                                                            instance, args, kwargs):
    return _nr_wrapper_django_inclusion_tag_decorator_(
        wrapped(*args, **kwargs))


@function_wrapper
def _nr_wrapper_django_template_base_InclusionNode_render_(wrapped,
                                                           instance, args, kwargs):
    if wrapped.__self__ is None:
        return wrapped(*args, **kwargs)

    file_name = getattr(wrapped.__self__, '_nr_file_name', None)

    if file_name is None:
        return wrapped(*args, **kwargs)

    name = wrapped.__self__._nr_file_name

    with FunctionTrace(name, 'Template/Include'):
        return wrapped(*args, **kwargs)


def _nr_wrapper_django_template_base_generic_tag_compiler_(wrapped, instance,
                                                           args, kwargs):
    if wrapped.__code__.co_argcount > 6:
        # Django > 1.3.

        def _bind_params(parser, token, params, varargs, varkw, defaults,
                         name, takes_context, node_class, *args, **kwargs):
            return node_class
    else:
        # Django <= 1.3.

        def _bind_params(params, defaults, name, node_class, parser, token,
                         *args, **kwargs):
            return node_class

    node_class = _bind_params(*args, **kwargs)

    if node_class.__name__ == 'InclusionNode':
        result = wrapped(*args, **kwargs)

        result.render = (
            _nr_wrapper_django_template_base_InclusionNode_render_(
                result.render))

        return result

    return wrapped(*args, **kwargs)


def _nr_wrapper_django_template_base_Library_tag_(wrapped, instance,
                                                  args, kwargs):
    def _bind_params(name=None, compile_function=None, *args, **kwargs):
        return compile_function

    compile_function = _bind_params(*args, **kwargs)

    if not callable(compile_function):
        return wrapped(*args, **kwargs)

    def _get_node_class(compile_function):

        node_class = None

        # Django >= 1.4 uses functools.partial

        if isinstance(compile_function, functools.partial):
            node_class = compile_function.keywords.get('node_class')

        # Django < 1.4 uses their home-grown "curry" function,
        # not functools.partial.

        if (hasattr(compile_function, 'func_closure') and
                hasattr(compile_function, '__name__') and
                compile_function.__name__ == '_curried'):

            cells = dict(zip(compile_function.__code__.co_freevars,
                             (c.cell_contents for c in compile_function.func_closure)))

            # node_class is the 4th arg passed to generic_tag_compiler()

            if 'args' in cells and len(cells['args']) > 3:
                node_class = cells['args'][3]

        return node_class

    node_class = _get_node_class(compile_function)

    if node_class is None or node_class.__name__ != 'InclusionNode':
        return wrapped(*args, **kwargs)

    file_name = None
    stack_levels = 2

    for i in range(1, stack_levels + 1):
        frame = sys._getframe(i)

        if ('generic_tag_compiler' in frame.f_code.co_names and
                'file_name' in frame.f_code.co_freevars):
            file_name = frame.f_locals.get('file_name')

    if file_name is None:
        return wrapped(*args, **kwargs)

    if isinstance(file_name, module_django_template_base.Template):
        file_name = file_name.name

    node_class._nr_file_name = file_name

    return wrapped(*args, **kwargs)


def instrument_django_template_base(module):
    global module_django_template_base
    module_django_template_base = module
    settings = global_settings()
    if 'django.instrumentation.inclusion-tags.r1' in settings.feature_flag:

        if hasattr(module, 'generic_tag_compiler'):
            wrap_function_wrapper(module, 'generic_tag_compiler',
                                  _nr_wrapper_django_template_base_generic_tag_compiler_)

        if hasattr(module, 'Library'):
            wrap_function_wrapper(module, 'Library.tag',
                                  _nr_wrapper_django_template_base_Library_tag_)

            wrap_function_wrapper(module, 'Library.inclusion_tag',
                                  _nr_wrapper_django_template_base_Library_inclusion_tag_)


def _nr_wrap_converted_middleware_(middleware, name):
    @function_wrapper
    def _wrapper(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)

        transaction.set_transaction_name(name, priority=2)

        with FunctionTrace(name=name):
            return wrapped(*args, **kwargs)

    return _wrapper(middleware)


def _nr_wrapper_convert_exception_to_response_(wrapped, instance, args,
                                               kwargs):
    def _bind_params(original_middleware, *args, **kwargs):
        return original_middleware

    original_middleware = _bind_params(*args, **kwargs)
    converted_middleware = wrapped(*args, **kwargs)
    name = callable_name(original_middleware)

    return _nr_wrap_converted_middleware_(converted_middleware, name)


def instrument_django_core_handlers_exception(module):
    if hasattr(module, 'convert_exception_to_response'):
        wrap_function_wrapper(module, 'convert_exception_to_response',
                              _nr_wrapper_convert_exception_to_response_)

    if hasattr(module, 'handle_uncaught_exception'):
        module.handle_uncaught_exception = (
            wrap_handle_uncaught_exception(
                module.handle_uncaught_exception))
