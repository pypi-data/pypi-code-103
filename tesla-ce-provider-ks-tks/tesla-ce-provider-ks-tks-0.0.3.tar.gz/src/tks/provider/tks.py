#  Copyright (c) 2021 Roger Muñoz
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


""" TeSLA CE Face Recognition module """
import simplejson
from tesla_ce_provider import BaseProvider, result
from tesla_ce_provider.provider.audit import KeystrokeAudit
from . import utils
from .models import GaussianModel, GaussianMixturesModel


class TKSProvider(BaseProvider):
    """
        TeSLA Face Recognition implementation
    """
    _logger = None

    def __init__(self):
        super().__init__()

        self.accepted_mimetypes = ['text/plain']
        self.config = {
            'model': 'GaussianMixturesModel',
            'min_enrol_samples': 10,
            'target_enrol_samples': 15,
            'start_decision_threshold': 0.5,
            'result_valid_delta_di': 0.02,
            'result_valid_delta_tri': 0.03,
            'result_valid_delta_four': 0.04,
            'result_invalid_delta_di': 0.04,
            'result_invalid_delta_tri': 0.03,
            'result_invalid_delta_four': 0.02,
            'failed_missing_data': False,
            'missing_data_threshold': 0.5
        }

    def _get_model_class(self, model):
        if self.config['model'] == 'GaussianModel':
            return GaussianModel(model)
        elif self.config['model'] == 'GaussianMixturesModel':
            return GaussianMixturesModel(model)

        raise ValueError('Model is not available')

    def set_options(self, options):
        """
            Set options for the provider
            :param options: Provider options following provider options_scheme definition
            :type options: dict
        """
        if options is not None:
            permitted_options = self.config.keys()

            for permitted_option in permitted_options:
                if permitted_option in options:
                    self.config[permitted_option] = options[permitted_option]

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
        # Load model
        self.log_trace('TKS: Start enrolment process.')
        tks_model = self._get_model_class(model)
        tks_model.set_required_samples(self.config['target_enrol_samples'])
        tks_model.set_min_required_samples(self.config['min_enrol_samples'])

        self.log_trace('TKS: Start processing enrolment samples')
        for sample in samples:
            self.log_trace('TKS: Sample process START')
            # Get the image
            ks_array = utils.get_sample_ks(sample)

            if ks_array is None:
                json_sample = simplejson.dumps(sample, indent=4, skipkeys=True)
                trace = f"TKS: KS data is None. Skip enrolment for current sample: {json_sample}"
                self.log_trace(trace)
                continue

            features = tks_model.enrol(features=ks_array)
            tks_model.add_sample(sample, features)

        return result.EnrolmentResult(tks_model.to_json(), tks_model.get_percentage(), tks_model.can_analyse(),
                                      used_samples=tks_model.get_used_samples())

    def validate_sample(self, sample, validation_id):
        """
            Validate an enrolment sample
            :param sample: Enrolment sample
            :type sample: tesla_ce_provider.models.base.Sample
            :param validation_id: Request validation identification
            :type validation_id: int
            :return: Validation result
            :rtype: tesla_ce_provider.ValidationResult
        """
        # Check provided input
        sample_check = utils.check_sample_ks(sample, self.accepted_mimetypes)
        if not sample_check['valid']:
            return result.ValidationResult(False, sample_check['msg'],
                                           message_code_id=sample_check['code'])

        return result.ValidationResult(True,
                                       contribution=1.0 / float(self.config['target_enrol_samples']))

    def verify(self, request, model):
        """
            Verify a learner request
            :param request: Verification request
            :type request: tesla_ce_provider.models.base.Request
            :param model: Provider model
            :type model: dict
            :return: Verification result
            :rtype: tesla_ce_provider.VerificationResult
        """
        # Load model
        tks_model = self._get_model_class(model)

        # Check provided input
        sample_check = utils.check_sample_ks(request, self.accepted_mimetypes)
        if not sample_check['valid']:
            return result.VerificationResult(True, error_message=sample_check['msg'],
                                             message_code=sample_check['code'])

        ks_data = sample_check['ks_data']

        [score, samples_discarded, number_features] = tks_model.verify(ks_data, self.config)

        code = result.VerificationResult.AlertCode.OK

        if samples_discarded > number_features*self.config['missing_data_threshold']:
            code = result.VerificationResult.AlertCode.ALERT

            if self.config['failed_missing_data'] is True:
                score = 0

        audit = KeystrokeAudit(num_samples_discarded=samples_discarded, num_features=number_features)
        return result.VerificationResult(True, result=score, code=code, audit=audit)

    def on_notification(self, key, info):
        """
            Respond to a notification task
            :param key: The notification task unique key
            :type key: str
            :param info: Information stored in the notification
            :type info: dict

            self.update_or_create_notification(result.NotificationTask('key', countdown=30, info={'my_field': 3}))
        """
        raise NotImplementedError('Method not implemented on provider')
