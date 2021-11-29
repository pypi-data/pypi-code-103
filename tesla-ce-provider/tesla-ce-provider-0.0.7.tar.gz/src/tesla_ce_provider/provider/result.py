#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" TeSLA CE Provider Result module """
import datetime
from .audit.base import BaseAudit


class StatusCode:
    PENDING = 0
    PROCESSED = 1
    ERROR = 2
    TIMEOUT = 3
    MISSING_PROVIDER = 4
    MISSING_ENROLMENT = 5
    WAITING_EXTERNAL_SERVICE = 6


class ValidationResult:
    """ Validation Result class """

    def __init__(self, valid, error_message=None, info=None, contribution=None, message_code_id=None):
        """
            Create a validation result instance for an enrolment sample

            :param valid: Whether this sample is valid (True) or not (False)
            :type valid: bool
            :param error_message: An error message in case of invalid sample
            :type error_message: str
            :param info: Additional information regarding the sample verification
            :type info: dict
            :param message_code_id: Message code
            :type message_code_id: str
        """
        if valid is True:
            self.status = StatusCode.PROCESSED
        else:
            self.status = StatusCode.ERROR
        self.error_message = error_message
        self.message_code_id = message_code_id
        self.info = info
        self.contribution = contribution

    def json(self):
        return {
            'status': self.status,
            'error_message': self.error_message,
            'validation_info': self.info,
            'message_code_id': self.message_code_id,
            'contribution': self.contribution
        }


class EnrolmentResult:
    """ Enrolment Result class """

    def __init__(self, model, percentage, can_analyse, valid=True, error_message=None, used_samples=None):
        """
            Create an enrolment result instance for an enrolment sample

            :param model: Updated model object
            :type model: dict
            :param can_analyse: Whether with current model we can start analysing learner data, or we need more samples
            :type can_analyse: bool
            :param valid: Whether this sample is valid (True) or not (False)
            :type valid: bool
            :param error_message: An error message in case of invalid sample
            :type error_message: str
            :param used_samples: List of sample IDs used to create this model
            :type used_samples: list
        """
        self.valid = valid
        self.error_message = error_message
        self.model = model
        self.can_analyse = can_analyse
        self.percentage = percentage
        self.used_samples = used_samples or []

    def json(self):
        return {
            'valid': self.valid,
            'error_message': self.error_message,
            'model': self.model,
            'can_analyze': self.can_analyse,
            'percentage': self.percentage,
            'used_samples': self.used_samples
        }


class VerificationResult:
    """ Verification Result class """

    class AlertCode:
        PENDING = 0
        OK = 1
        WARNING = 2
        ALERT = 3

    def __init__(self, valid, code=AlertCode.OK, error_message=None, audit=None, result=None, message_code=None):
        """
            Create a verification result instance for a verification request

            :param valid: Whether this request is valid (True) or not (False)
            :type valid: bool
            :param code: Alert level code for this request
            :type code: AlertCode
            :param error_message: An error message in case of invalid request
            :type error_message: str
            :param audit: Additional information regarding the request verification
            :type audit: BaseAudit
            :param result: The numeric result from 0 to 1 for this sample
            :type result: float
            :param message_code: Message related to this result
            :type message_code: Message
        """
        if valid:
            self.status = StatusCode.PROCESSED
        else:
            self.status = StatusCode.ERROR
        self.error_message = error_message
        self.message_code = message_code
        self.audit = None
        if audit is not None:
            self.audit = audit.json()
        self.result = result
        self.code = code

    def json(self):
        return {
            'status': self.status,
            'error_message': self.error_message,
            'audit': self.audit,
            'result': self.result,
            'code': self.code,
            'message_code': self.message_code
        }


class NotificationTask:
    """ Notification task class """

    def __init__(self, key, countdown=None, when=None, info=None):
        """
            Create a notification task

            :param key: Unique key for the notification
            :type key: str
            :param countdown: Minimum delay in seconds for the notification
            :type countdown: int
            :param when: Minimum date and time in UTC for the notification
            :type when: datetime
            :param info: Additional data for this task
            :type info: dict
        """
        if when is None and countdown is None:
            countdown = 60
        if when is None:
            when = datetime.datetime.utcnow() + datetime.timedelta(seconds=countdown)
        self.key = key
        self.when = when
        self.info = info

    def json(self):
        return {
            'key': self.key,
            'when': self.when,
            'info': self.info
        }


class EnrolmentDelayedResult:
    """ EnrolmentDelayedResult class """

    def __init__(self, learner_id, sample_id, result, task_id, model, info=None):
        """
            Create a delayed result
            :param learner_id: Unique learner identification
            :type learner_id: str
            :param sample_id: Unique sample identification
            :type sample_id: int
            :param result: Delayed result
            :type result: EnrolmentResult
            :param task_id: Task identification
            :type task_id: int
            :param model: Model
            :type model: object
            :param info: An extra information about result
            :type info: object
        """
        self.result = result
        self.status = StatusCode.WAITING_EXTERNAL_SERVICE
        self.info = info
        self.learner_id = learner_id
        self.sample_id = sample_id
        self.task_id = task_id
        self.model = model

    def json(self):
        return {
            'result': self.result.json(),
            'info': self.info,
            'status': self.status,
            'learner_id': self.learner_id,
            'sample_id': self.sample_id,
            'model': self.model,
            'task_id': self.task_id
        }


class ValidationDelayedResult:
    """ ValidationDelayedResult class """

    def __init__(self, learner_id, sample_id, validation_id, result, info=None):
        """
            Create a delayed result
            :param learner_id: Unique learner identification
            :type learner_id: str
            :param sample_id: Unique sample identification
            :type sample_id: int
            :param validation_id: Unique validation identification
            :type validation_id: int
            :param result: Delayed result
            :type result: EnrolmentResult
            :param info: An extra information about result
            :type info: object
        """
        self.result = result
        self.status = StatusCode.WAITING_EXTERNAL_SERVICE
        self.info = info
        self.learner_id = learner_id
        self.sample_id = sample_id
        self.validation_id = validation_id

    def json(self):
        return {
            'result': self.result.json(),
            'info': self.info,
            'status': self.status,
            'learner_id': self.learner_id,
            'sample_id': self.sample_id,
            'validation_id': self.validation_id
        }


class VerificationDelayedResult:
    """ VerificationDelayedResult class """

    def __init__(self, learner_id, request_id, result, info=None):
        """
            Create a delayed result
            :param request_id: Unique request identification
            :type request_id: int
            :param result: Delayed result
            :type result: VerificationResult
            :param info: An extra information about result
            :type info: object
        """
        self.result = result
        self.status = StatusCode.WAITING_EXTERNAL_SERVICE
        self.info = info
        self.request_id = request_id

    def json(self):
        return {
            'result': self.result.json(),
            'info': self.info,
            'status': self.status,
            'request_id': self.request_id,
        }
