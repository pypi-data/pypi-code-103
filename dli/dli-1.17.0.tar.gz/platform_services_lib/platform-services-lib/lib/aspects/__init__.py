import inspect
from typing import Callable


def __call_extract_fn(application_extract_func, target, function, arguments, keyword_args, class_fields_to_include=None):
    metadata, obj = application_extract_func(
        target, function, arguments, keyword_args, class_fields_to_include)
    return metadata, obj


def __get_analytic_fns_object_from_target(target) -> Callable:

    # HACK2: Firstly you can't not do this check, with MagicMock or UnstructuredDatasetModel, since
    # any unknown variable is a DeferInCaseCall, i.e. always exists, even if it doesnt.
    # Secondly, you can't check for _client, since a Model HAS_A client, but doesnt not have the method callback
    # that aspects needs to call, so we have to redirect the method call (target_a), but keep the target
    if not hasattr(target, "_analytics_extract_metadata") \
            or not inspect.ismethod(target._analytics_extract_metadata):  # magicmock/deferincasecall yield True
        # TODO dirty module, must check reference trait/properties of target and choose _client for SDK
        target_a = target._client._analytics_extract_metadata
    else:
        target_a = target._analytics_extract_metadata

    return target_a


def _make_function_call(aspects, target, function, args, kwargs, class_fields_to_include):

    '''
     Explanation of who the hell is target.
     ====
     on SDK Mixins -
     see Component_Aspect_Wrapper, handled whereby target (the mixin) extends the client,
     so target IS client which HAS _analytics_handler, _analytics_extract_metadata
     ---
     on SDK Models -
     target is e.g FileModel/DatasetModel, so target HAS a client
     and a client HAS _analytics_handler, _analytics_extract_metadata

     Because of UnstructuredDatasetModel, it HAS _client, but also states that it HAS any function/property
     as this gets turned into a deferincasecall, so will pass any check. The way we can capture this is to look
     for whether _analytics_extract_metadata (any property of the target - the one with the aspects required methods)
     is a function (or NOT an object)
     ---
     on S3Proxy -
     similar to mixin case
     target IS Dispatcher which HAS _analytics_handler, _analytics_extract_metadata
     ---
     on Tests -
     target is a magicmock and/or target._client is a magicmock. _analytics_extract_metadata should return a SkipError
     to skip over analytics, if there is no real implementation to use.
    '''

    def inner():
        try:
            result = function(target, *args, **kwargs)
        except TypeError as t:
            # HACK1: its a pity to put this here, but we need to hijack TypeError for UnstructuredDatasetModel
            # we can't use hasattr, since the TypeError hijack will return something!
            # N.B. if you need to see the real cause, comment out the _type_exception_handler of the class.
            # TODO dirty module, must check whether target is UnstructuredModel for SDK
            if "_type_exception_handler" in dir(target):
                target._type_exception_handler(t, function, args, kwargs)
                return
            else:
                for aspect in aspects:
                    aspect.invoke_after_exception_aspects(obj, metadata, t)
                raise t

        return result

    try:
        application_extract_func = __get_analytic_fns_object_from_target(target)
        metadata, obj = __call_extract_fn(application_extract_func, target, function, args, kwargs, class_fields_to_include)
    except Exception as e:
        # just because extraction for analytics fails, doesnt mean we should fail the call undecorated. Still do it!
        metadata = {}
        obj = application_extract_func
        return inner()

    # if we're here, then we can run the function and wrap with analytics as the extract passed,
    # we did not hit exception
    try:
        for aspect in aspects:
            aspect.invoke_pre_call_aspects(obj, metadata)

        result = inner()

        for aspect in aspects:
            aspect.invoke_post_call_aspects(obj, metadata)
    except Exception as e:
        # If the object contains a `strict` boolean and it is set to
        # True, then print out the exception message and a full stack
        # trace.
        # DEFAULTED to True to match the current behaviour. This default
        # can be changed in a later release. When we change the default
        # we will have to update the tests to explicitly set strict to
        # True to maintain the previous test behaviour.
        if getattr(obj, 'strict', True):
            for aspect in aspects:
                aspect.invoke_after_exception_aspects(obj, metadata, e)
            raise e
        elif getattr(obj, 'logger', None):
            # Data scientists do not want to see stack dumps by
            # default, especially when we have a root cause that
            # triggers secondary exceptions.
            obj.logger.warning(
                '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
                '\nAn exception occurred so we are returning None.'
                '\nTo see the exception and stack trace, please start '
                'the session again with the parameter `strict=True`'
                '\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
            )
            return None

    return result
