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
""" TeSLA CE Keystroke GaussianModel module """
from math import sqrt
from tesla_ce_provider.models import SimpleModel
from ..constants import DWELL, FLIGHT, DIGRAPH, TRIGRAPH, FOURGRAPH


class GaussianModel(SimpleModel):
    """
        Model for FaceRecognition based on a list of reference images
    """
    def __init__(self, model_object=None):
        super().__init__(model_object=model_object)

    def can_analyse(self):
        '''
        Can analyse function
        :return:
        '''
        if self._percentage >= 1:
            return True
        return False

    def enrol(self, features):
        '''
        Enrol features in this model
        :param features:
        :return:
        '''
        if self._data is None:
            self._data = {}

        for feature_array in features:
            for feature in feature_array['features']:
                aux = {"n": 0, "xsq": 0, "x": 0}
                if str(feature['type']) not in self._data:
                    self._data[str(feature['type'])] = {
                        'id': None,
                        'model': {}
                    }

                if feature['code'] in self._data[str(feature['type'])]['model']:
                    aux = self._data[str(feature['type'])]['model'][feature['code']]

                aux['n'] += 1
                aux['x'] += feature['time']
                aux['xsq'] += feature['time']**2

                self._data[str(feature['type'])]['model'][feature['code']] = aux

        return {}

    def verify(self, features, config):
        '''
        Verify if features are from this model
        :param features:
        :param config:
        :return:
        '''

        samples_discarded = 0
        number_features = 0
        decision_threshold = config['start_decision_threshold']

        for feature_array in features:
            for feature in feature_array['features']:
                number_features += 1
                if str(feature['type']) not in self._data:
                    samples_discarded += 1
                    continue

                if feature['code'] not in self._data[str(feature['type'])]['model']:
                    samples_discarded += 1
                    continue

                key_model = self._data[str(feature['type'])]['model'][feature['code']]

                muu = key_model['x']/key_model['n']
                roo = 0
                try:
                    roo = sqrt(key_model['xsq']/key_model['n']
                              - ((key_model['x']/key_model['n'])**2))
                except ValueError:
                    # sqrt negative -> ro = 0
                    pass

                # muu = mean
                # roo = standard deviation
                if roo == 0:
                    samples_discarded += 1
                    continue

                dist = abs(feature['time'] - muu)/roo

                delta = 0
                if dist <= 1:
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
                        DWELL: config['result_invalid_delta_di'],
                        FLIGHT: config['result_invalid_delta_di'],
                        DIGRAPH: config['result_invalid_delta_di'],
                        TRIGRAPH: config['result_invalid_delta_tri'],
                        FOURGRAPH: config['result_invalid_delta_four'],
                    }
                delta = result_dict[feature['type']]

                decision_threshold += delta

                if decision_threshold > 1:
                    decision_threshold = 1
                elif decision_threshold < 0:
                    decision_threshold = 0

        #if samples_discarded > number_features*0.5:
        #    return None

        return [decision_threshold, samples_discarded, number_features]
