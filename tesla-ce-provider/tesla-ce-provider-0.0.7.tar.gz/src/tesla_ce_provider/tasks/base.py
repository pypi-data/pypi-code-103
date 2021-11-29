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
""" TeSLA CE Base Task module """
import os
import requests
import sentry_sdk
from sentry_sdk import capture_exception
from sentry_sdk.integrations.celery import CeleryIntegration
from celery import Task
from celery.utils.log import task_logger
from ..provider.base import BaseProvider
from ..provider.result import EnrolmentDelayedResult, VerificationDelayedResult, ValidationDelayedResult
from ..celery_app import client
from ..models import parse_validation_data
from ..models.base import Sample


if os.getenv('SENTRY_ENABLED') in ['1', 1, 'True', 'yes', 'true'] and os.getenv('SENTRY_DSN') is not None:
    sentry_sdk.init(
        os.getenv('SENTRY_DSN'),
        integrations=[CeleryIntegration()],
        max_breadcrumbs=50,
        debug=os.getenv('DEBUG', '0') in ['1', 1, 'True', 'yes', 'true'],
        release=os.getenv('PROVIDER_VERSION', 'n/a'),
        environment=os.getenv('SENTRY_ENVIRONMENT', 'production'),
        server_name=os.getenv('SENTRY_SERVER_NAME', None)
    )


class BaseTask(Task):
    """ Base Task for TeSLA Providers """

    # Instrument provider implementation -> BaseProvider
    _provider = None

    # TeSLA Client
    _client = client

    # Current learner
    _learner = None

    # Whether model needs to be unlocked in case of failure
    _unlock_on_failure = False

    @property
    def provider(self):
        """
            Access to the provider implementation
            :return: Provider instance
            :rtype: BaseProvider
        """
        if self._provider is None:
            self._provider = BaseProvider.get_provider()
            self._provider.set_logger(self.add_trace)
        # Set required credentials
        for key in self._provider.get_required_credentials():
            value = self.client._find_config_value(key)
            self._provider.set_credential(key, value)
        # Update provider options
        if self._provider is not None:
            self._provider.provider_id = self.get_provider_id()
            provider_info = self.get_provider_info()
            if provider_info is not None:
                self._provider.instrument = {
                    'id': provider_info['instrument']['id'],
                    'acronym': provider_info['instrument']['acronym'],
                    'description': provider_info['description']
                }
                self._provider.info = {
                    'name': provider_info['name'],
                    'description': provider_info['description'],
                    'url': provider_info['url'],
                    'version': provider_info['version'],
                    'acronym': provider_info['acronym']
                }
                if 'options' in provider_info:
                    self._provider.set_options(provider_info['options'])

        return self._provider

    @property
    def client(self):
        """
            Access to the TeSLA CE Client instance
            :return: Client instance
            :rtype: tesla_ce_client.Client
        """
        return self._client

    def get_provider_id(self):
        """
            Get the Provider ID
            :return: Provider ID
            :rtype: int
        """
        return self._client._connector.get_provider_id()

    def get_provider_info(self):
        """
            Get the Provider information
            :return: Provider information
            :rtype: dict
        """
        return self._client.provider.get(self.get_provider_id())

    def get_provider_options(self):
        """
            Get the Provider options
            :return: Provider options
            :rtype: dict
        """
        provider_info = self._client.provider.get(self.get_provider_id())
        if provider_info is not None and 'options' in provider_info:
            return provider_info['options']
        return None

    def get_validated_enrolment_samples(self, learner_id):
        """
            Return the list of enrolment samples that are available for this learner. Only returns those samples
            that are not included in current model.

            :param learner_id: The learner UUID
            :type learner_id: str
            :return: Enrolment samples
            :rtype: list
        """

        result = self._client.provider.enrolment.get_available_samples(self.get_provider_id(), learner_id)
        if result is None or result['count'] == 0:
            return None
        while result is not None:
            page = []
            # Read data for each sample
            for sample in result['results']:
                # Get the validations
                sample['validations'] = self.get_sample_validations(sample)
                # Get the data
                sample_data = self.get_sample_data(sample['data'])
                sample['data'] = sample_data
                page.append(sample)
            for sample in page:
                yield Sample(sample)

            # Move to next page
            result = self._client.get_next(result)

    def get_sample_data(self, url):
        """
            Download sample data from storage url
            :param url: Storage URL
            :type url: str
            :return: Sample data
            :rtype: dict
        """
        if os.getenv('SSL_VERIFY', True) in ['False', 'false', 0, False, '0']:
            data_resp = requests.get(url, verify=False)
        else:
            data_resp = requests.get(url)
        if data_resp.status_code != 200:
            self.retry(countdown=5 * 60, max_retries=3)
        return data_resp.json()

    def get_sample_validations(self, sample):
        """
            Get sample available validations

            :param sample: A sample object
            :type sample: dict
            :return: Validation generator
        """
        validations = self.client.provider.enrolment.get_sample_validation_list(self.get_provider_id(),
                                                                                sample['learner_id'],
                                                                                sample['id'])
        for validation in validations['results']:
            if 'info' in validation and validation['info'] is not None:
                data = self.get_sample_data(validation['info'])
                validation['info'] = data
                validation_data = parse_validation_data(data)
                if validation_data is not None:
                    yield validation_data

    def get_request_data(self, url):
        """
            Download request data from storage url
            :param url: Storage URL
            :type url: str
            :return: Request data
            :rtype: dict
        """
        return self.get_sample_data(url)

    def get_model_data(self, url):
        """
            Download model data from storage url
            :param url: Storage URL
            :type url: str
            :return: Model data
            :rtype: dict
        """
        if os.getenv('SSL_VERIFY', True) in ['False', 'false', 0, False, '0']:
            data_resp = requests.get(url, verify=False)
        else:
            data_resp = requests.get(url)
        if data_resp.status_code != 200:
            self.retry(countdown=5 * 60, max_retries=3)
        return data_resp.json()

    def send_notifications(self):
        """
            Send notification tasks
        """
        for notification in self.provider.notifications:
            self.client.provider.notification.update_or_create(self.get_provider_id(), notification.key,
                                                               notification.when, notification.info)
        self.provider.notifications.clear()

    def get_notification_data(self, notification_id):
        """
            Get information for a given notification
            :param notification_id: Notification unique id
            :type notification_id: int
            :return: Notification object
            :rtype: dict
        """
        return self.client.provider.notification.get(self.get_provider_id(), notification_id)

    def delete_notification(self, notification_id):
        """
            Delete a notification task
            :param notification_id: Notification unique id
            :type notification_id: int
        """
        return self.client.provider.notification.delete(self.get_provider_id(), notification_id)

    def send_delayed_results(self):
        """
            Send notification tasks
        """
        for delayed_result in self.provider.delayed_results:
            if isinstance(delayed_result, ValidationDelayedResult):
                self.client.provider.enrolment.set_sample_validation(self.get_provider_id(),
                                                                     delayed_result.learner_id,
                                                                     delayed_result.sample_id,
                                                                     delayed_result.validation_id,
                                                                     delayed_result.result.json()
                                                                     )

            if isinstance(delayed_result, EnrolmentDelayedResult):
                model = delayed_result.model

                if delayed_result.result.valid:
                    model['model'] = delayed_result.result.model
                    model['percentage'] = delayed_result.result.percentage
                    model['can_analyse'] = delayed_result.result.can_analyse
                    model['used_samples'] = delayed_result.result.used_samples

                # Store new model
                self.add_trace('EnrolmentTask: Saving new model')
                self.client.provider.enrolment.save_model(self.get_provider_id(), delayed_result.learner_id,
                                                          self.request.id, model)

            if isinstance(delayed_result, VerificationDelayedResult):
                self.client.provider.verification.set_provider_request_result(provider_id=self.get_provider_id(),
                                                                              request_id=delayed_result.request_id,
                                                                              result=delayed_result.result.json())

        self.provider.delayed_results.clear()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Perform default actions when an uncontrolled exception is raised

        :param exc: The exception raised by the task.
        :type exc: Exception
        :param task_id: The task identifier
        :type task_id: uuid
        :param args: Original arguments for the task that failed.
        :type args: tuple
        :param kwargs: Original keyword arguments for the task that failed.
        :type kwargs: dict
        :param einfo:
        """
        self.capture_exception(exc)
        if self._unlock_on_failure and self._learner is not None:
            self.client.provider.enrolment.unlock_model(self.get_provider_id(), self._learner, self.request.id)

    @staticmethod
    def capture_exception(exception):
        """
            Capture exception and send it to Sentry if it is enabled
            :param exception: Captured exception
        """
        if os.getenv('SENTRY_ENABLED') in ['1', 1, 'True', 'yes', 'true'] and os.getenv('SENTRY_DSN') is not None:
            capture_exception(exception)

    @staticmethod
    def add_trace(message):
        """
            Add task trace for current task. This trace is shown on logs at info state
            :param message: Message to be shown
        """
        if os.getenv('LOG_TASK_TRACE', False) in ['1', 'True', 'true', 1, True]:
            task_logger.info(message)
