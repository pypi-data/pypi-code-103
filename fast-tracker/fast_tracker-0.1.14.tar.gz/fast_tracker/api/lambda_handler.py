# -*- coding: utf-8 -*-

import functools
from fast_tracker.common.object_wrapper import FunctionWrapper
from fast_tracker.api.transaction import current_transaction
from fast_tracker.api.web_transaction import WebTransaction
from fast_tracker.api.application import application_instance
from fast_tracker.core.config import global_settings


COLD_START_RECORDED = False
MEGABYTE_IN_BYTES = 2**20


def _LambdaHandlerWrapper(wrapped, application=None, name=None, group=None):

    def _nr_lambda_handler_wrapper_(wrapped, instance, args, kwargs):

        transaction = current_transaction(active_only=False)

        if transaction:
            return wrapped(*args, **kwargs)

        try:
            event, context = args[:2]
        except Exception:
            return wrapped(*args, **kwargs)

        target_application = application

        if not hasattr(application, 'activate'):
            target_application = application_instance(application)

        try:
            request_method = event['httpMethod']
            request_path = event['path']
            headers = event['headers']
            query_params = event.get('multiValueQueryStringParameters')
            background_task = False
        except Exception:
            request_method = None
            request_path = None
            headers = None
            query_params = None
            background_task = True

        transaction_name = name or getattr(context, 'function_name', None)

        transaction = WebTransaction(
                target_application,
                transaction_name,
                group=group,
                request_method=request_method,
                request_path=request_path,
                headers=headers)

        transaction.background_task = background_task

        global COLD_START_RECORDED
        if COLD_START_RECORDED is False:
            COLD_START_RECORDED = True

        settings = global_settings()
        if query_params and not settings.high_security:
            try:
                transaction._request_params.update(query_params)
            except:
                pass
        with transaction:
            result = wrapped(*args, **kwargs)

            if not background_task:
                try:
                    status_code = result.get('statusCode')
                    response_headers = result.get('headers')

                    try:
                        response_headers = response_headers.items()
                    except Exception:
                        response_headers = None

                    transaction.process_response(status_code, response_headers)
                except Exception:
                    pass

            return result

    return FunctionWrapper(wrapped, _nr_lambda_handler_wrapper_)


def LambdaHandlerWrapper(*args, **kwargs):
    return _LambdaHandlerWrapper(*args, **kwargs)


def lambda_handler(application=None, name=None, group=None):

    return functools.partial(_LambdaHandlerWrapper, application=application, name=name, group=group)
