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
""" TeSLA CE Verification tasks module """
from celery.exceptions import Reject
from tesla_ce_client.exception import ObjectNotFoundException

from .base import BaseTask
from ..celery_app import app
from ..provider.result import VerificationDelayedResult
from ..provider.result import VerificationResult
from ..models.base import Request
from tesla_ce_client.provider.verification import RequestResultStatus


class VerificationTask(BaseTask):
    """ Verification Task for TeSLA Providers """
    name = 'tesla_ce.tasks.requests.verification.verify_request'

    def run(self, request_id, result_id):
        """
            Start verification of a request

            :param request_id: Sample ID
            :type request_id: int
            :param result_id: Verification Request ID.
            :type result_id: int
        """
        # Store the context
        self._unlock_on_failure = False
        self._learner = None

        # Get request result
        try:
            request = self.client.provider.verification.get_provider_request_result(
                self.client._connector.get_provider_id(),
                request_id)
        except ObjectNotFoundException:
            raise Reject('Request not found')

        # is this provider require_enrolment and model_data is needed?
        provider = self.client.provider.get(self.client._connector.get_provider_id())
        model_data = None
        if provider['instrument']['requires_enrolment'] is True:
            # Download learner model
            try:
                model = self.client.provider.enrolment.get_model(
                    self.client._connector.get_provider_id(), request['learner_id']
                )
            except ObjectNotFoundException:
                raise Reject('Model not found')

            if not model['can_analyse']:
                self.retry(countdown=120)

            # Get model data
            model_data = self.get_model_data(model['model'])

        # Download request data
        request['request']['data'] = self.get_request_data(request['request']['data'])

        # Perform enrolment process
        try:
            verify_response = self.provider.verify(Request(request), model=model_data)
        except Exception as exc:
            raise Reject('Exception from provider: ' + exc.__str__())

        if isinstance(verify_response, VerificationResult):
            # Store verification result
            self.client.provider.verification.set_provider_request_result(self.client._connector.get_provider_id(),
                                                                          request_id, verify_response.json())
        elif isinstance(verify_response, VerificationDelayedResult):
            self.client.provider.verification.set_provider_request_status(self.get_provider_id(), request_id,
                                                                          RequestResultStatus.WAITING_EXTERNAL_SERVICE)
        else:
            exc = RuntimeError("Unexpected result type in verify")
            self.capture_exception(exc)
            verify_response = VerificationResult(False, error_message="Internal provider error",
                                                 message_code="INTERNAL_ERROR")
            self.client.provider.verification.set_provider_request_result(self.get_provider_id(), request_id,
                                                                          verify_response.json())

            raise exc

        # Send delayed results
        self.add_trace('VerificationTask: Sending delayed results')
        self.send_delayed_results()
        self.add_trace('VerificationTask: End task')

        # Send notifications
        self.add_trace('VerificationTask: Sending notifications')
        self.send_notifications()
        self.add_trace('VerificationTask: End task')


VerificationTask = app.register_task(VerificationTask())
