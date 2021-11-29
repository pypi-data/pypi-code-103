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


class Sample:
    """
        Sample object class for providers
    """
    def __init__(self, object):
        """
            Base constructor, that creates the object from JSON description
            :param object: JSON dictionary of a sample
            :type object: dict
        """
        if 'sample' in object:
            self._object = object['sample']
        else:
            self._object = object

    @property
    def learner_id(self):
        """
            Get Learner ID
            :return: UUIDv4 id of the learner owning this sample
            :rtype: str
        """
        if self._object is not None and 'learner_id' in self._object:
            return self._object['learner_id']
        return None

    @property
    def sample_id(self):
        """
            Get Sample ID
            :return: Sample unique identifier in the API
            :rtype: int
        """
        if self._object is not None and 'id' in self._object:
            return self._object['id']
        return None

    @property
    def validations(self):
        """
            Get available validations for this sample
            :return: A generator providing all available validations
            :rtype: generator
        """
        if self._object is not None and 'validations' in self._object:
            return self._object['validations']
        return None

    @property
    def data(self):
        """
            Get sample data
            :return: The base64 codification of the sample as provided by sensors
            :rtype: str
        """
        if self._object is not None and 'data' in self._object and 'data' in self._object['data']:
            return self._object['data']['data']
        return None

    @property
    def context(self):
        """
            Get the context provided by the sensors
            :return: Context information for the sample
            :rtype: dict
        """
        if self.metadata is not None and 'context' in self.metadata:
            return self.metadata['context']
        return None

    @property
    def metadata(self):
        """
            Get the metadata provided by the sensors
            :return: Metadata information for the sample
            :rtype: dict
        """
        if self._object is not None and 'data' in self._object and 'metadata' in self._object['data']:
            return self._object['data']['metadata']
        return None

    @property
    def instruments(self):
        """
            Get the list of instruments selected for this sample
            :return: List of instrument id's
            :rtype: list
        """
        if self._object is not None and 'data' in self._object and 'instruments' in self._object['data']:
            return self._object['data']['instruments']
        return None

    @property
    def mime_type(self):
        """
            Get the mime type of the request
            :return: Request mime type
            :rtype: str
        """
        if self.metadata is not None and 'mimetype' in self.metadata:
            return self.metadata['mimetype']
        return None


class Request:
    """
        Request object class for providers
    """
    def __init__(self, object):
        """
            Base constructor, that creates the object from JSON description
            :param object: JSON dictionary of a request
            :type object: dict
        """
        if 'request' in object:
            self._object = object['request']
        else:
            self._object = object

    @property
    def request_id(self):
        """
            Get Request ID
            :return: Request unique identifier in the API
            :rtype: int
        """
        if self._object is not None and 'id' in self._object:
            return self._object['id']
        return None

    @property
    def learner_id(self):
        """
            Get Learner ID
            :return: UUIDv4 id of the learner owning this request
            :rtype: str
        """
        if self._object is not None and 'learner_id' in self._object['data']:
            return self._object['data']['learner_id']
        return None

    @property
    def course_id(self):
        """
            Get Course ID
            :return: Course unique identifier in the API
            :rtype: int
        """
        if self._object is not None and 'course_id' in self._object['data']:
            return self._object['data']['course_id']
        return None

    @property
    def activity_id(self):
        """
            Get Activity ID
            :return: Activity unique identifier in the API
            :rtype: int
        """
        if self._object is not None and 'activity_id' in self._object['data']:
            return self._object['data']['activity_id']
        return None

    @property
    def session_id(self):
        """
            Get Session ID
            :return: Session unique identifier in the API
            :rtype: int
        """
        if self._object is not None and 'session_id' in self._object['data']:
            return self._object['data']['session_id']
        return None

    @property
    def data(self):
        """
            Get request data
            :return: The base64 codification of the sample as provided by sensors
            :rtype: str
        """
        if self._object is not None and 'data' in self._object and 'data' in self._object['data']:
            return self._object['data']['data']
        return None

    @property
    def context(self):
        """
            Get the context provided by the sensors
            :return: Context information for the request
            :rtype: dict
        """
        if self.metadata is not None and 'context' in self.metadata:
            return self.metadata['context']
        return None

    @property
    def metadata(self):
        """
            Get the metadata provided by the sensors
            :return: Metadata information for the request
            :rtype: dict
        """
        if self._object is not None and 'metadata' in self._object['data']:
            return self._object['data']['metadata']
        return None

    @property
    def instruments(self):
        """
            Get the list of instruments selected for this request
            :return: List of instrument id's
            :rtype: list
        """
        if self._object is not None and 'instruments' in self._object['data']:
            return self._object['data']['instruments']
        return None

    @property
    def mime_type(self):
        """
            Get the mime type of the request
            :return: Request mime type
            :rtype: str
        """
        if self.metadata is not None and 'mimetype' in self.metadata:
            return self.metadata['mimetype']
        return None


class ValidationData:
    """
        Validation class for providers
    """

    def __init__(self, data_object=None):
        """
            Default constructor
        """
        #: Instrument
        self.instrument = None

        #: Additional information
        self.info = None

        #: Provider information
        self.provider = None

        if data_object is not None:
            self.load(data_object)

    def set_instrument(self, id, acronym):
        """
            Set the information for the instrument
            :param id: Id of the instrument
            :type id: int
            :param acronym: Acronym of the instrument
            :type acronym: str
        """
        self.instrument = {
            'id': id,
            'acronym': acronym
        }

    def set_provider(self, id, acronym, version):
        """
            Set the information for the provider that performed the validation
            :param id: Id of the provider
            :type id: int
            :param acronym: Acronym of the provider
            :type acronym: str
            :param version: Version of the provider implementation
            :type version: str
        """
        self.provider = {
            'id': id,
            'acronym': acronym,
            'version': version
        }

    def set_info(self, info):
        """
            Set additional information specific for the provider
            :param info: Additional information
            :type info: dict
        """
        self.info = info

    def to_json(self):
        """
            Get a JSON representation of the object
            :return: JSON representation
            :rtype: dict
        """
        return {
            'provider': self.provider,
            'instrument': self.instrument,
            'info': self.info
        }

    def load(self, object):
        """
            Load an object from a JSON representation
            :param object: JSON representation of the object
            :type object: dict
            :return: Whether this object is a valid representation or not
            :rtype: bool
        """
        if 'provider' in object and 'instrument' in object and 'info' in object:
            self.provider = object['provider']
            self.instrument = object['instrument']
            self.info = object['info']
            return True
        return False
