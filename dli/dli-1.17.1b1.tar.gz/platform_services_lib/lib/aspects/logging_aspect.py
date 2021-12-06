#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import inspect


class LoggingAspect:

    # N.B. The contract is that the wrapped_object HAS_A logger property

    @staticmethod
    def invoke_pre_call_aspects(wrapped_object, metadata):
        if getattr(wrapped_object, 'logger', None):
            try:
                wrapped_object.logger.debug('Client Function Called', extra=metadata)
            except Exception as e:
                wrapped_object.logger.exception(
                    'Error while invoking pre-call aspects.', e
                )

    @staticmethod
    def invoke_post_call_aspects(wrapped, metadata):
        pass

    @staticmethod
    def invoke_after_exception_aspects(wrapped_object, metadata, exception):
        # If the object contains a `strict` boolean and it is set to
        # True, then print out the exception message and a full stack
        # trace.
        # DEFAULTED to True to match the current behaviour. This default
        # can be changed in a later release. When we change the default
        # we will have to update the tests to explicitly set strict to
        # True to maintain the previous test behaviour.
        if getattr(wrapped_object, 'logger', None):
            try:
                wrapped_object.logger.exception(
                    'Unhandled Exception', stack_info=False, extra={
                        'locals': inspect.trace()[-1][0].f_locals
                    })
            except Exception as e:
                wrapped_object.logger.exception(
                    'Error while invoking pre-call aspects.', e
                )