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
""" TeSLA CE Enrolment related tasks module """
from celery.exceptions import Reject
from tesla_ce_client.exception import LockedResourceException
from tesla_ce_client.provider.enrolment import SampleValidationStatus
from ..provider.result import EnrolmentDelayedResult
from ..provider.result import EnrolmentResult
from ..provider.result import ValidationDelayedResult
from ..provider.result import ValidationResult

from .base import BaseTask
from ..celery_app import app
from ..models.base import Sample


class EnrolmentTask(BaseTask):
    """ Enrolment Task for TeSLA Providers """
    name = 'tesla_ce.tasks.requests.enrolment.enrol_learner'

    def run(self, learner_id, sample_id=None):
        # Store the context
        self._learner = learner_id
        self._unlock_on_failure = False
        model = None

        self.add_trace('EnrolmentTask: Start running task {}.'.format(self.request.id))

        # Download learner model
        try:
            model = self.client.provider.enrolment.get_model_lock(self.client._connector.get_provider_id(),
                                                                  learner_id, self.request.id)
            self._unlock_on_failure = True
            self.add_trace('EnrolmentTask: Model ready for modification.')
        except LockedResourceException:
            # Model is locked by another task
            self.add_trace('EnrolmentTask: Model is locked. Stop execution and retry later.')
            self.retry(countdown=30, max_retries=10)

        # Get model data
        model_data = None
        if model is not None and model['model'] is not None:
            self.add_trace('EnrolmentTask: Loading model data.')
            model_data = self.get_model_data(model['model'])
            self.add_trace('EnrolmentTask: Model data loaded.')
        else:
            self.add_trace('EnrolmentTask: Model data is empty.')

        # Get Sample information
        self.add_trace('EnrolmentTask: Retrieving enrolment samples.')
        samples = self.get_validated_enrolment_samples(learner_id)
        if samples is None:
            self.add_trace('EnrolmentTask: No available enrolment samples. Reject task.')
            self.client.provider.enrolment.unlock_model(self.get_provider_id(), learner_id, self.request.id)
            raise Reject('No available samples to enrol')
        self.add_trace('EnrolmentTask: enrolment samples ready.')

        # Perform enrolment process
        try:
            self.add_trace('EnrolmentTask: starting enrolment.')
            enrol_response = self.provider.enrol(samples, model=model_data)
            self.add_trace('EnrolmentTask: enrolment done: [valid={}, percentage={}, samples={}]'.format(
                enrol_response.percentage, enrol_response.percentage, enrol_response.used_samples
            ))
        except Exception as exc:
            self.add_trace('EnrolmentTask: exception detected. {}'.format(exc.__str__()))
            self.capture_exception(exc)
            if self._unlock_on_failure:
                self.client.provider.enrolment.unlock_model(self.get_provider_id(), learner_id, self.request.id)
            raise Reject('Exception from provider: ' + exc.__str__())

        if isinstance(enrol_response, EnrolmentResult):
            if enrol_response.valid:
                model['model'] = enrol_response.model
                model['percentage'] = enrol_response.percentage
                model['can_analyse'] = enrol_response.can_analyse
                model['used_samples'] = enrol_response.used_samples

            # Store new model
            self.add_trace('EnrolmentTask: Saving new model')
            self.client.provider.enrolment.save_model(self.get_provider_id(), learner_id,
                                                      self.request.id, model)
            self.add_trace('EnrolmentTask: New model saved')
        elif isinstance(enrol_response, EnrolmentDelayedResult):
            self.client.provider.enrolment.set_sample_status(provider_id=self.get_provider_id(), learner_id=learner_id,
                                                             sample_id=self.request.id,
                                                             status=SampleValidationStatus.WAITING_EXTERNAL_SERVICE)

        else:
            # internal server
            exc = RuntimeError("Unexpected result type in enrol")
            self.capture_exception(exc)
            self.client.provider.enrolment.set_sample_status(provider_id=self.get_provider_id(), learner_id=learner_id,
                                                             sample_id=self.request.id,
                                                             status=SampleValidationStatus.ERROR)

        # Send delayed results
        self.add_trace('EnrolmentTask: Sending delayed results')
        self.send_delayed_results()
        self.add_trace('EnrolmentTask: End task')

        # Send notifications
        self.add_trace('EnrolmentTask: Sending notifications')
        self.send_notifications()
        self.add_trace('EnrolmentTask: End task')


class ValidationTask(BaseTask):
    """ Validation Task for TeSLA Providers """
    name = 'tesla_ce.tasks.requests.enrolment.validate_request'

    def run(self, learner_id, sample_id, validation_id):
        # Store the context
        self._learner = learner_id
        self._unlock_on_failure = False

        # Get Sample information
        sample = self.client.provider.enrolment.get_sample_validation(self.get_provider_id(), learner_id,
                                                                      sample_id, validation_id)

        # Download sample content
        sample['sample']['data'] = self.get_sample_data(sample['sample']['data'])

        # Validate the sample
        validation_result = self.provider.validate_sample(Sample(sample), validation_id=validation_id)

        # Update validation status
        if isinstance(validation_result, ValidationResult):
            self.client.provider.enrolment.set_sample_validation(self.get_provider_id(), learner_id, sample_id,
                                                                 validation_id, validation_result.json())
        elif isinstance(validation_result, ValidationDelayedResult):
            status_wait = SampleValidationStatus.WAITING_EXTERNAL_SERVICE
            self.client.provider.enrolment.set_sample_validation_status(provider_id=self.get_provider_id(),
                                                                        learner_id=learner_id, sample_id=sample_id,
                                                                        validation_id=validation_id,
                                                                        status=status_wait)
        else:
            # internal server
            exc = RuntimeError("Unexpected result type in validation")
            self.capture_exception(exc)
            self.client.provider.enrolment.set_sample_validation_status(provider_id=self.get_provider_id(),
                                                                        learner_id=learner_id, sample_id=sample_id,
                                                                        validation_id=validation_id,
                                                                        status=SampleValidationStatus.ERROR)
        # Send delayed results
        self.add_trace('ValidationTask: Sending delayed results')
        self.send_delayed_results()
        self.add_trace('ValidationTask: End task')

        # Send notifications
        self.add_trace('ValidationTask: Sending notifications')
        self.send_notifications()
        self.add_trace('ValidationTask: End task')


EnrolmentTask = app.register_task(EnrolmentTask())
ValidationTask = app.register_task(ValidationTask())
