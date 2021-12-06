
class AnalyticsAspect:

    # N.B. The contract is that the wrapped_object HAS_A _analytics_handler property, and logger property

    @staticmethod
    def invoke_pre_call_aspects(wrapped_object, metadata):
        pass

    def invoke_post_call_aspects(self, wrapped_object, metadata):
        try:
            additional_properties = metadata.get('properties', {})
            self._create_event(wrapped_object, metadata, status_code=200, additional_properties=additional_properties)
        except Exception as e:
            wrapped_object.logger.exception(
                'Error while invoking post-call aspects.', e
            )

    def invoke_after_exception_aspects(self, wrapped_object, metadata, exception):
        try:
            status_code = self._retrieve_status_code_from_exception(exception)
            additional_properties = metadata.get('properties', {})
            self._create_event(
                wrapped_object, metadata,
                status_code=status_code,
                additional_properties=additional_properties)
        except Exception as e:
            wrapped_object.logger.exception(
                'Error while invoking after-exception aspects.', e
            )

    @staticmethod
    def _create_event(wrapped_object, metadata, status_code, additional_properties):
        if getattr(wrapped_object, '_analytics_handler', None):
            wrapped_object._analytics_handler.create_event(
                metadata['subject'], metadata['organisation_id'],
                metadata['func'].__qualname__.split('.')[0],
                metadata['func'].__name__,
                {**metadata['arguments'], **metadata['kwargs'], **additional_properties},
                result_status_code=status_code
            )

    @staticmethod
    def _retrieve_status_code_from_exception(exception):
        try:
            return exception.response.status_code
        except AttributeError:
            return 500
