# -*- coding: utf-8 -*-


import fast_tracker.api.function_trace
import fast_tracker.api.object_wrapper


class TemplateRenderWrapper(object):

    def __init__(self, wrapped):
        self.__wrapped = wrapped

    def __getattr__(self, name):
        return getattr(self.__wrapped, name)

    def __get__(self, instance, klass):
        if instance is None:
            return self
        descriptor = self.__wrapped.__get__(instance, klass)
        return self.__class__(descriptor)

    def __call__(self, template, *args, **kwargs):
        transaction = fast_tracker.api.transaction.current_transaction()
        if transaction:
            if hasattr(template, 'filename'):
                name = template.filename or '<template>'
                with fast_tracker.api.function_trace.FunctionTrace(
                        name=name, group='Template/Render'):
                    return self.__wrapped(template, *args, **kwargs)
            else:
                return self.__wrapped(template, *args, **kwargs)
        else:
            return self.__wrapped(template, *args, **kwargs)


def instrument_mako_runtime(module):
    fast_tracker.api.object_wrapper.wrap_object(module,
                                                '_render', TemplateRenderWrapper)


def instrument_mako_template(module):
    def template_filename(template, text, filename, *args):
        return filename

    fast_tracker.api.function_trace.wrap_function_trace(
        module, '_compile_text',
        name=template_filename, group='Template/Compile')
    fast_tracker.api.function_trace.wrap_function_trace(
        module, '_compile_module_file',
        name=template_filename, group='Template/Compile')
