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
""" TeSLA CE Base Provider base model module """


class BaseModel:
    """
        Model class for providers
    """

    def __init__(self, model_object=None):
        """
            Default constructor
        """
        #: Current enrolment percentage
        self._percentage = 0.0

        #: List of samples included in this model
        self._samples = []

        #: Model data
        self._data = None

        if model_object is not None:
            self.load(model_object)

    def to_json(self):
        """
            Get a JSON representation of the object
            :return: JSON representation
            :rtype: dict
        """
        return {
            'percentage': self._percentage,
            'samples': self._samples,
            'data': self._data
        }

    def load(self, model_object):
        """
            Load an object from a JSON representation
            :param model_object: JSON representation of the object
            :type model_object: dict
            :return: Whether this object is a valid representation or not
            :rtype: bool
        """
        if 'percentage' in model_object and 'samples' in model_object and 'data' in model_object:
            self._percentage = model_object['percentage']
            self._samples = model_object['samples']
            self._data = model_object['data']
            return True
        return False

    def add_sample(self, sample, features=None):
        """
            Add given sample to model
            :param sample: Sample object
            :type sample: tesla_ce_provider.models.base.Sample
            :param features: Optional provider representation for this sample
            :type features: dict
        """
        self._samples.append({
            'id': sample.sample_id,
            'features': features
        })

    def get_samples(self):
        """
            Get samples stored in the model
            :return: Sample generator
        """
        for sample in self._samples:
            yield sample

    def get_percentage(self):
        """
            Get the enrolment percentage
            :return: Enrolment percentage
            :rtype: float
        """
        return self._percentage

    def set_data(self, data):
        """
            Set model data
            :param data: Model data
            :type data: dict
        """
        self._data = data

    def can_analyse(self):
        """
            Check if current model is able to be used or need more enrolment samples
            :return: True if this model can be used or False otherwise
            :rtype: bool
        """
        raise NotImplementedError('Method not implemented')

    def get_used_samples(self):
        """
            Return a list of the sample IDs used by this model
            :return: List of sample ID's
            :rtype: list
        """
        used_samples = []
        for sample in self._samples:
            used_samples.append(sample['id'])
        return used_samples

    def get_sample_id(self, idx):
        """
            Return the sample ID from the index in the list of samples in the model
            :param idx: Index in the list of samples
            :type idx: int
            :return: Enrolment sample ID
            :rtype: int
        """
        if idx < 0 or idx > len(self._samples) - 1:
            return None
        return list(self._samples)[idx]['id']


class SimpleModel(BaseModel):
    """
        Simple Model based on a list of reference samples
    """

    def __init__(self, model_object=None):
        super().__init__(model_object=model_object)

        #: Minimum number of reference samples required to start analysing
        self._min_required_samples = 5

        #: Target number of reference samples for the model
        self._required_samples = 15

    def set_required_samples(self, num_samples):
        """
            Set the number of samples required for this model
            :param num_samples: Number of samples
            :type num_samples: int
        """
        self._required_samples = num_samples

    def set_min_required_samples(self, num_samples):
        """
            Set the minimum number of samples required to be able to analyse
            :param num_samples: Number of samples
            :type num_samples: int
        """
        self._min_required_samples = num_samples

    def can_analyse(self):
        """
            Check if current model is able to be used or need more enrolment samples
            :return: True if this model can be used or False otherwise
            :rtype: bool
        """
        return len(self._samples) >= self._min_required_samples

    def add_sample(self, sample, features=None):
        """
            Add given sample to model and update the enrolment percentage
            :param sample: Sample object
            :type sample: tesla_ce_provider.models.base.Sample
            :param features: Optional provider representation for this sample
            :type features: dict
        """
        super().add_sample(sample, features)
        self._percentage = min(1.0, float(len(self._samples)) / float(self._required_samples))

    def load(self, model_object):
        """
            Load an object from a JSON representation
            :param model_object: JSON representation of the object
            :type model_object: dict
            :return: Whether this object is a valid representation or not
            :rtype: bool
        """
        if super().load(model_object) and 'min_required_samples' in model_object and 'required_samples' in model_object:
            self._min_required_samples = model_object['percentage']
            self._required_samples = model_object['required_samples']
            return True
        return False
