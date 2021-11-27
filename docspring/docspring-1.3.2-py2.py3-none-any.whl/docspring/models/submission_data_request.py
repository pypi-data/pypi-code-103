# coding: utf-8

"""
    API v1

    DocSpring is a service that helps you fill out and sign PDF templates.  # noqa: E501

    OpenAPI spec version: v1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class SubmissionDataRequest(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'id': 'str',
        'name': 'str',
        'email': 'str',
        'order': 'int',
        'sort_order': 'int',
        'fields': 'list[str]',
        'metadata': 'object',
        'state': 'str',
        'viewed_at': 'str',
        'completed_at': 'str',
        'auth_type': 'str',
        'auth_second_factor_type': 'str',
        'auth_provider': 'str',
        'auth_session_started_at': 'str',
        'auth_session_id_hash': 'str',
        'auth_user_id_hash': 'str',
        'auth_username_hash': 'str',
        'auth_phone_number_hash': 'str',
        'ip_address': 'str',
        'user_agent': 'str'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'email': 'email',
        'order': 'order',
        'sort_order': 'sort_order',
        'fields': 'fields',
        'metadata': 'metadata',
        'state': 'state',
        'viewed_at': 'viewed_at',
        'completed_at': 'completed_at',
        'auth_type': 'auth_type',
        'auth_second_factor_type': 'auth_second_factor_type',
        'auth_provider': 'auth_provider',
        'auth_session_started_at': 'auth_session_started_at',
        'auth_session_id_hash': 'auth_session_id_hash',
        'auth_user_id_hash': 'auth_user_id_hash',
        'auth_username_hash': 'auth_username_hash',
        'auth_phone_number_hash': 'auth_phone_number_hash',
        'ip_address': 'ip_address',
        'user_agent': 'user_agent'
    }

    def __init__(self, id=None, name=None, email=None, order=None, sort_order=None, fields=None, metadata=None, state=None, viewed_at=None, completed_at=None, auth_type=None, auth_second_factor_type=None, auth_provider=None, auth_session_started_at=None, auth_session_id_hash=None, auth_user_id_hash=None, auth_username_hash=None, auth_phone_number_hash=None, ip_address=None, user_agent=None):  # noqa: E501
        """SubmissionDataRequest - a model defined in OpenAPI"""  # noqa: E501

        self._id = None
        self._name = None
        self._email = None
        self._order = None
        self._sort_order = None
        self._fields = None
        self._metadata = None
        self._state = None
        self._viewed_at = None
        self._completed_at = None
        self._auth_type = None
        self._auth_second_factor_type = None
        self._auth_provider = None
        self._auth_session_started_at = None
        self._auth_session_id_hash = None
        self._auth_user_id_hash = None
        self._auth_username_hash = None
        self._auth_phone_number_hash = None
        self._ip_address = None
        self._user_agent = None
        self.discriminator = None

        self.id = id
        self.name = name
        self.email = email
        self.order = order
        self.sort_order = sort_order
        self.fields = fields
        self.metadata = metadata
        self.state = state
        self.viewed_at = viewed_at
        self.completed_at = completed_at
        if auth_type is not None:
            self.auth_type = auth_type
        if auth_second_factor_type is not None:
            self.auth_second_factor_type = auth_second_factor_type
        self.auth_provider = auth_provider
        self.auth_session_started_at = auth_session_started_at
        self.auth_session_id_hash = auth_session_id_hash
        self.auth_user_id_hash = auth_user_id_hash
        self.auth_username_hash = auth_username_hash
        self.auth_phone_number_hash = auth_phone_number_hash
        self.ip_address = ip_address
        self.user_agent = user_agent

    @property
    def id(self):
        """Gets the id of this SubmissionDataRequest.  # noqa: E501


        :return: The id of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this SubmissionDataRequest.


        :param id: The id of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Gets the name of this SubmissionDataRequest.  # noqa: E501


        :return: The name of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this SubmissionDataRequest.


        :param name: The name of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def email(self):
        """Gets the email of this SubmissionDataRequest.  # noqa: E501


        :return: The email of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this SubmissionDataRequest.


        :param email: The email of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._email = email

    @property
    def order(self):
        """Gets the order of this SubmissionDataRequest.  # noqa: E501


        :return: The order of this SubmissionDataRequest.  # noqa: E501
        :rtype: int
        """
        return self._order

    @order.setter
    def order(self, order):
        """Sets the order of this SubmissionDataRequest.


        :param order: The order of this SubmissionDataRequest.  # noqa: E501
        :type: int
        """
        if order is None:
            raise ValueError("Invalid value for `order`, must not be `None`")  # noqa: E501

        self._order = order

    @property
    def sort_order(self):
        """Gets the sort_order of this SubmissionDataRequest.  # noqa: E501


        :return: The sort_order of this SubmissionDataRequest.  # noqa: E501
        :rtype: int
        """
        return self._sort_order

    @sort_order.setter
    def sort_order(self, sort_order):
        """Sets the sort_order of this SubmissionDataRequest.


        :param sort_order: The sort_order of this SubmissionDataRequest.  # noqa: E501
        :type: int
        """
        if sort_order is None:
            raise ValueError("Invalid value for `sort_order`, must not be `None`")  # noqa: E501

        self._sort_order = sort_order

    @property
    def fields(self):
        """Gets the fields of this SubmissionDataRequest.  # noqa: E501


        :return: The fields of this SubmissionDataRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._fields

    @fields.setter
    def fields(self, fields):
        """Sets the fields of this SubmissionDataRequest.


        :param fields: The fields of this SubmissionDataRequest.  # noqa: E501
        :type: list[str]
        """

        self._fields = fields

    @property
    def metadata(self):
        """Gets the metadata of this SubmissionDataRequest.  # noqa: E501


        :return: The metadata of this SubmissionDataRequest.  # noqa: E501
        :rtype: object
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this SubmissionDataRequest.


        :param metadata: The metadata of this SubmissionDataRequest.  # noqa: E501
        :type: object
        """
        if metadata is None:
            raise ValueError("Invalid value for `metadata`, must not be `None`")  # noqa: E501

        self._metadata = metadata

    @property
    def state(self):
        """Gets the state of this SubmissionDataRequest.  # noqa: E501


        :return: The state of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this SubmissionDataRequest.


        :param state: The state of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """
        if state is None:
            raise ValueError("Invalid value for `state`, must not be `None`")  # noqa: E501
        allowed_values = ["pending", "completed"]  # noqa: E501
        if state not in allowed_values:
            raise ValueError(
                "Invalid value for `state` ({0}), must be one of {1}"  # noqa: E501
                .format(state, allowed_values)
            )

        self._state = state

    @property
    def viewed_at(self):
        """Gets the viewed_at of this SubmissionDataRequest.  # noqa: E501


        :return: The viewed_at of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._viewed_at

    @viewed_at.setter
    def viewed_at(self, viewed_at):
        """Sets the viewed_at of this SubmissionDataRequest.


        :param viewed_at: The viewed_at of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._viewed_at = viewed_at

    @property
    def completed_at(self):
        """Gets the completed_at of this SubmissionDataRequest.  # noqa: E501


        :return: The completed_at of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._completed_at

    @completed_at.setter
    def completed_at(self, completed_at):
        """Sets the completed_at of this SubmissionDataRequest.


        :param completed_at: The completed_at of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._completed_at = completed_at

    @property
    def auth_type(self):
        """Gets the auth_type of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_type of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_type

    @auth_type.setter
    def auth_type(self, auth_type):
        """Sets the auth_type of this SubmissionDataRequest.


        :param auth_type: The auth_type of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """
        allowed_values = ["none", "password", "oauth", "email_link", "phone_number", "ldap", "saml"]  # noqa: E501
        if auth_type not in allowed_values:
            raise ValueError(
                "Invalid value for `auth_type` ({0}), must be one of {1}"  # noqa: E501
                .format(auth_type, allowed_values)
            )

        self._auth_type = auth_type

    @property
    def auth_second_factor_type(self):
        """Gets the auth_second_factor_type of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_second_factor_type of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_second_factor_type

    @auth_second_factor_type.setter
    def auth_second_factor_type(self, auth_second_factor_type):
        """Sets the auth_second_factor_type of this SubmissionDataRequest.


        :param auth_second_factor_type: The auth_second_factor_type of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """
        allowed_values = ["none", "phone_number", "totp", "mobile_push", "security_key", "fingerprint"]  # noqa: E501
        if auth_second_factor_type not in allowed_values:
            raise ValueError(
                "Invalid value for `auth_second_factor_type` ({0}), must be one of {1}"  # noqa: E501
                .format(auth_second_factor_type, allowed_values)
            )

        self._auth_second_factor_type = auth_second_factor_type

    @property
    def auth_provider(self):
        """Gets the auth_provider of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_provider of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_provider

    @auth_provider.setter
    def auth_provider(self, auth_provider):
        """Sets the auth_provider of this SubmissionDataRequest.


        :param auth_provider: The auth_provider of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._auth_provider = auth_provider

    @property
    def auth_session_started_at(self):
        """Gets the auth_session_started_at of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_session_started_at of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_session_started_at

    @auth_session_started_at.setter
    def auth_session_started_at(self, auth_session_started_at):
        """Sets the auth_session_started_at of this SubmissionDataRequest.


        :param auth_session_started_at: The auth_session_started_at of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._auth_session_started_at = auth_session_started_at

    @property
    def auth_session_id_hash(self):
        """Gets the auth_session_id_hash of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_session_id_hash of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_session_id_hash

    @auth_session_id_hash.setter
    def auth_session_id_hash(self, auth_session_id_hash):
        """Sets the auth_session_id_hash of this SubmissionDataRequest.


        :param auth_session_id_hash: The auth_session_id_hash of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._auth_session_id_hash = auth_session_id_hash

    @property
    def auth_user_id_hash(self):
        """Gets the auth_user_id_hash of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_user_id_hash of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_user_id_hash

    @auth_user_id_hash.setter
    def auth_user_id_hash(self, auth_user_id_hash):
        """Sets the auth_user_id_hash of this SubmissionDataRequest.


        :param auth_user_id_hash: The auth_user_id_hash of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._auth_user_id_hash = auth_user_id_hash

    @property
    def auth_username_hash(self):
        """Gets the auth_username_hash of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_username_hash of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_username_hash

    @auth_username_hash.setter
    def auth_username_hash(self, auth_username_hash):
        """Sets the auth_username_hash of this SubmissionDataRequest.


        :param auth_username_hash: The auth_username_hash of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._auth_username_hash = auth_username_hash

    @property
    def auth_phone_number_hash(self):
        """Gets the auth_phone_number_hash of this SubmissionDataRequest.  # noqa: E501


        :return: The auth_phone_number_hash of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._auth_phone_number_hash

    @auth_phone_number_hash.setter
    def auth_phone_number_hash(self, auth_phone_number_hash):
        """Sets the auth_phone_number_hash of this SubmissionDataRequest.


        :param auth_phone_number_hash: The auth_phone_number_hash of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._auth_phone_number_hash = auth_phone_number_hash

    @property
    def ip_address(self):
        """Gets the ip_address of this SubmissionDataRequest.  # noqa: E501


        :return: The ip_address of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._ip_address

    @ip_address.setter
    def ip_address(self, ip_address):
        """Sets the ip_address of this SubmissionDataRequest.


        :param ip_address: The ip_address of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._ip_address = ip_address

    @property
    def user_agent(self):
        """Gets the user_agent of this SubmissionDataRequest.  # noqa: E501


        :return: The user_agent of this SubmissionDataRequest.  # noqa: E501
        :rtype: str
        """
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent):
        """Sets the user_agent of this SubmissionDataRequest.


        :param user_agent: The user_agent of this SubmissionDataRequest.  # noqa: E501
        :type: str
        """

        self._user_agent = user_agent

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, SubmissionDataRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
