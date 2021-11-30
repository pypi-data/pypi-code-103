# -*- coding: utf-8 -*-

import sys
import os

import fast_tracker.api.transaction
import fast_tracker.api.import_hook
import fast_tracker.api.wsgi_application
import fast_tracker.api.external_trace
import fast_tracker.api.function_trace
import fast_tracker.api.transaction_name
import fast_tracker.api.object_wrapper
import fast_tracker.api.pre_function

from fast_tracker.api.time_trace import record_exception


def instrument_gluon_compileapp(module):
    def transaction_name_run_models_in(environment):
        return '%s::%s' % (environment['request'].application,
                           environment['response'].view)

    fast_tracker.api.transaction_name.wrap_transaction_name(module,
                                                            'run_models_in', name=transaction_name_run_models_in,
                                                            group='Web2Py')

    def name_function_run_models_in(environment):
        return '%s/%s' % (environment['request'].controller,
                          environment['request'].function)

    fast_tracker.api.function_trace.wrap_function_trace(module,
                                                        'run_models_in', name=name_function_run_models_in,
                                                        group='Python/Web2Py/Models')

    def name_function_run_controller_in(controller, function, environment):
        return '%s/%s' % (controller, function)

    fast_tracker.api.function_trace.wrap_function_trace(module,
                                                        'run_controller_in', name=name_function_run_controller_in,
                                                        group='Python/Web2Py/Controller')

    def name_function_run_view_in(environment):
        return '%s/%s' % (environment['request'].controller,
                          environment['request'].function)

    fast_tracker.api.function_trace.wrap_function_trace(module,
                                                        'run_view_in', name=name_function_run_view_in,
                                                        group='Python/Web2Py/View')


def instrument_gluon_restricted(module):

    def name_function_restricted(code, environment={}, layer='Unknown'):
        if 'request' in environment:
            folder = environment['request'].folder
            if layer.startswith(folder):
                return layer[len(folder):]
        return layer

    def group_function_restricted(code, environment={}, layer='Unknown'):
        parts = layer.split('.')
        if parts[-1] in ['html'] or parts[-2:] in [['html', 'pyc']]:
            return 'Template/Render'
        return 'Script/Execute'

    fast_tracker.api.function_trace.wrap_function_trace(module, 'restricted',
                                                        name=name_function_restricted, group=group_function_restricted)


def instrument_gluon_main(module):
    fast_tracker.api.wsgi_application.wrap_wsgi_application(module, 'wsgibase')

    class error_serve_controller(object):
        def __init__(self, wrapped):
            fast_tracker.api.object_wrapper.update_wrapper(self, wrapped)
            self._nr_next_object = wrapped
            if not hasattr(self, '_nr_last_object'):
                self._nr_last_object = wrapped

        def __call__(self, request, response, session):
            txn = fast_tracker.api.transaction.current_transaction()
            if txn:
                HTTP = fast_tracker.api.import_hook.import_module('gluon.http').HTTP
                try:
                    return self._nr_next_object(request, response, session)
                except HTTP:
                    raise
                except:  # Catch all
                    record_exception()
                    raise
            else:
                return self._nr_next_object(request, response, session)

        def __getattr__(self, name):
            return getattr(self._nr_next_object, name)

    fast_tracker.api.object_wrapper.wrap_object(
        module, 'serve_controller', error_serve_controller)


def instrument_gluon_template(module):

    def name_function_parse_template(filename, path='views/',
                                     context=dict(), *args, **kwargs):
        if 'request' in context:
            folder = context['request'].folder
            if path.startswith(folder):
                return '%s/%s' % (path[len(folder):], filename)
        else:
            return '%s/%s' % (path, filename)

    fast_tracker.api.function_trace.wrap_function_trace(module, 'parse_template',
                                                        name=name_function_parse_template, group='Template/Compile')


def instrument_gluon_tools(module):
    # Wrap utility function for fetching an external URL.

    def url_external_fetch(url, *args, **kwargs):
        return url

    fast_tracker.api.external_trace.wrap_external_trace(
        module, 'fetch', library='gluon.tools.fetch',
        url=url_external_fetch)

    fast_tracker.api.external_trace.wrap_external_trace(
        module, 'geocode', library='gluon.tools.geocode',
        url='http://maps.google.com/maps/geo')


def instrument_gluon_http(module):

    def transaction_name_name_not_found(response, *args, **kwargs):
        txn = fast_tracker.api.transaction.current_transaction()
        if not txn:
            return

        frame = sys._getframe(1)

        if os.path.split(frame.f_code.co_filename)[-1] == 'pre_function.py':
            frame = frame.f_back

        if os.path.split(frame.f_code.co_filename)[-1] != 'main.py':
            return

        if frame.f_code.co_name != 'wsgibase':
            return

        if response.status == 400:
            txn.set_transaction_name('400', 'Uri')
            return

        if response.status == 404:
            txn.set_transaction_name('404', 'Uri')
            return

        if 'static_file' not in frame.f_locals:
            return

        if frame.f_locals['static_file']:
            if 'environ' in frame.f_locals:
                environ = frame.f_locals['environ']
                path_info = environ.get('PATH_INFO', '')

                if path_info:
                    parts = os.path.split(path_info)
                    if parts[1] == '':
                        if parts[0] == '/':
                            txn.set_transaction_name('*', 'Web2Py')
                        else:
                            name = '%s/*' % parts[0].lstrip('/')
                            txn.set_transaction_name(name, 'Web2Py')
                    else:
                        extension = os.path.splitext(parts[1])[-1]
                        name = '%s/*%s' % (parts[0].lstrip('/'), extension)
                        txn.set_transaction_name(name, 'Web2Py')
                else:
                    txn.set_transaction_name('*', 'Web2Py')

            else:
                txn.set_transaction_name('*', 'Web2Py')

    fast_tracker.api.pre_function.wrap_pre_function(
        module, 'HTTP.to', transaction_name_name_not_found)
