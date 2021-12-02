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
''' TeSLA CE Keystroke GaussianMixturesModel module'''
import base64
from io import BytesIO
from sklearn import mixture
from joblib import dump, load
import numpy as np
from tesla_ce_provider.models import SimpleModel
from ..constants import DWELL, FLIGHT, DIGRAPH, TRIGRAPH, FOURGRAPH


class GaussianMixturesModel(SimpleModel):
    """
        Model for FaceRecognition based on a list of reference images
    """
    def __init__(self, model_object=None):
        super().__init__(model_object=model_object)
        if model_object is not None:
            with BytesIO() as tmp_bytes:
                if self._data is not None:
                    tmp_b64 = self._data.encode('utf-8')
                    data_model = base64.b64decode(tmp_b64)
                    tmp_bytes.write(data_model)
                    self._data = load(tmp_bytes)


    def to_json(self):
        """
            Get a JSON representation of the object
            :return: JSON representation
            :rtype: dict
        """
        # convert to base64 file model
        if self._data is not None:
            with BytesIO() as tmp_bytes:
                dump(self._data, tmp_bytes)
                bytes_obj = tmp_bytes.getvalue()
                base64_obj = base64.b64encode(bytes_obj)
                self._data = base64_obj.decode('utf-8')

        return {
            'percentage': self._percentage,
            'samples': self._samples,
            'data': self._data
        }

    def can_analyse(self):
        if self._percentage >= 1:
            return True
        return False

    def enrol(self, features):
        """
        Enrol features in this model
        :param features:
        :return:
        """
        if self._data is None:
            self._data = {}

        codes = {}
        n_components = 3

        # get features from other enrolment samples
        for sample in self._samples:
            for feature in sample['features']:
                if feature not in codes:
                    codes[f"{feature}"] = []

                codes[f"{feature}"] += sample['features'][feature]

        # add new features to model
        new_codes = {}
        for feature_array in features:
            for feature in feature_array['features']:
                if f"{feature['type']}_{feature['code']}" not in codes:
                    codes[f"{feature['type']}_{feature['code']}"] = []
                if f"{feature['type']}_{feature['code']}" not in new_codes:
                    new_codes[f"{feature['type']}_{feature['code']}"] = []

                codes[f"{feature['type']}_{feature['code']}"].append(feature['time'])
                new_codes[f"{feature['type']}_{feature['code']}"].append(feature['time'])

        user_model = self._data

        for code, x_train in codes.items():
            if len(x_train) < n_components:
                continue

            x_train = np.array(x_train)/500
            x_train = x_train.reshape(-1, 1)

            clf = mixture.GaussianMixture(n_components=n_components,
                                          covariance_type='full')
            clf.fit(x_train)

            user_model[code] = clf

        self._data = user_model

        return new_codes

    def verify(self, features, config):
        """
        Verify if features are from this model
        :param features:
        :param config:
        :return:
        """
        samples_discarded = 0
        number_features = 0
        codes = {}
        decision_threshold = config['start_decision_threshold']

        for feature_array in features:
            for feature in feature_array['features']:
                if f"{feature['type']}_{feature['code']}" not in codes:
                    codes[f"{feature['type']}_{feature['code']}"] = []
                codes[f"{feature['type']}_{feature['code']}"].append(feature['time'])
                number_features += 1

        for code in codes:

            if code not in self._data:
                samples_discarded += 1
                continue

            clf = self._data[code]
            y_test = codes[code]

            y_test = np.array(y_test, dtype=float)
            y_test[np.isnan(y_test)] = 0
            y_test = np.array(y_test, dtype=int)

            y_test = np.array(y_test)/500
            y_test = y_test.reshape(-1, 1)

            for result in clf.score_samples(y_test):
                delta = 0

                if result > np.log(0.7):
                    # sample is of this user
                    result_dict = {
                        DWELL: config['result_valid_delta_di'],
                        FLIGHT: config['result_valid_delta_di'],
                        DIGRAPH: config['result_valid_delta_di'],
                        TRIGRAPH: config['result_valid_delta_tri'],
                        FOURGRAPH: config['result_valid_delta_four'],
                    }
                else:
                    result_dict = {
                        DWELL: -config['result_invalid_delta_di'],
                        FLIGHT: -config['result_invalid_delta_di'],
                        DIGRAPH: -config['result_invalid_delta_di'],
                        TRIGRAPH: -config['result_invalid_delta_tri'],
                        FOURGRAPH: -config['result_invalid_delta_four'],
                    }

                delta = result_dict[int(code.split('_')[0], 10)]
                decision_threshold += delta

                if decision_threshold < 0:
                    decision_threshold = 0.
                elif decision_threshold > 1:
                    decision_threshold = 1.

        return [decision_threshold, samples_discarded, number_features]
