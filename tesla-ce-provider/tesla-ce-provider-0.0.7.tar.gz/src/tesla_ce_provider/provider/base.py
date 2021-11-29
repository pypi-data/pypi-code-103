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
""" TeSLA CE Base Provider module """
import os
from .. import models


class BaseProvider:
    """ Base class for TeSLA CE Instrument providers """

    #: Credentials required by this provider
    _required_credentials = []

    #: Credentials read from environment variables or secrets
    _credentials = {}

    def __init__(self):
        #: Notification tasks
        self._notifications = []

        #: DelayedResults tasks
        self._delayed_results = []

        #: Provider ID
        self.provider_id = None

        #: Provider information
        self.info = None

        #: Instrument details
        self.instrument = None

        #: Base model
        self._model_class = models.BaseModel

    @classmethod
    def get_required_credentials(cls):
        """
            Get the credentials required by the provider
            :return: List of credential names (environment variables or secrets)
        """
        return cls._required_credentials

    @property
    def credentials(self):
        """
            Access to the provider credentials
            :return: Provider credentials
        """
        return self._credentials

    def set_credential(self, key, value):
        """
            Set a provider credential

            :param key: Credential Key
            :param value: Credential value
        """
        self._credentials[key] = value

    @staticmethod
    def get_provider(provider=None):
        """
            Create an instance of the provider
            :param provider: Full class name for the provider
            :type provider: str
            :return: Provider instance
            :rtype: BaseProvider
        """
        # Get the provider class
        if provider is None:
            provider = os.getenv('PROVIDER_CLASS', None)
        if provider is None:
            raise ModuleNotFoundError('Provider implementation class is not provider. Set PROVIDER_CLASS.')
        components = provider.split('.')
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod()

    def set_logger(self, logger):
        """
            Set a logging function
            :param logger: Logging function that accepts a message as argument
        """
        self._logger = logger

    def log_trace(self, message):
        """
            Add a trace message for task. Only works if logger has been initialized using set_logger.
            :param message: Message to add to trace
        """
        if self._logger is not None:
            self._logger(message)

    def set_options(self, options):
        """
            Set options for the provider
            :param options: Provider options following provider options_scheme definition
            :type options: dict
        """
        pass

    def verify(self, request, model):
        """
            Verify a learner request
            :param request: Verification request
            :type request: dict
            :param model: Provider model
            :type model: dict
            :return: Verification result
            :rtype: tesla_ce_provider.result.VerificationResult
        """
        raise NotImplementedError('Method not implemented on provider')

    def enrol(self, samples, model=None):
        """
            Update the model with a new enrolment sample
            :param samples: Enrolment samples
            :type samples: list
            :param model: Current model
            :type model: dict
            :return: Enrolment result
            :rtype: tesla_ce_provider.result.EnrolmentResult
        """
        raise NotImplementedError('Method not implemented on provider')

    def validate_sample(self, sample, validation_id):
        """
            Validate an enrolment sample
            :param sample: Enrolment sample
            :type sample: tesla_ce_provider.models.base.Sample
            :param validation_id: Validation identification
            :type validation_id: int
            :return: Validation result
            :rtype: tesla_ce_provider.result.ValidationResult
        """
        raise NotImplementedError('Method not implemented on provider')

    def on_notification(self, key, info):
        """
            Respond to a notification task
            :param key: The notification task unique key
            :type key: str
            :param info: Information stored in the notification
            :type info: dict
        """
        raise NotImplementedError('Method not implemented on provider')

    def update_or_create_notification(self, notification):
        """
            Schedule a notification task

            :param notification: Notification object
            :type: tesla_ce_provider.result.NotificationTask
        """
        # Add notification to the list of notifications
        self._notifications.append(notification)

    def update_delayed_result(self, result):
        """
            Schedule a delayed result

            :param result: Result
            :type: tesla_ce_provider.result.DelayedResult
        """
        self._delayed_results.append(result)

    @property
    def notifications(self):
        """
            Access to the list of notifications

            :return: List of notifications
            :rtype: list
        """
        return self._notifications

    @property
    def delayed_results(self):
        """
            Access to the list of delayed_results

            :return: List of delayed_results
            :rtype: list
        """
        return self._delayed_results
