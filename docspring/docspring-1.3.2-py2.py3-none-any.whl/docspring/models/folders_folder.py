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


class FoldersFolder(object):
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
        'parent_folder_id': 'str',
        'name': 'str'
    }

    attribute_map = {
        'parent_folder_id': 'parent_folder_id',
        'name': 'name'
    }

    def __init__(self, parent_folder_id=None, name=None):  # noqa: E501
        """FoldersFolder - a model defined in OpenAPI"""  # noqa: E501

        self._parent_folder_id = None
        self._name = None
        self.discriminator = None

        if parent_folder_id is not None:
            self.parent_folder_id = parent_folder_id
        if name is not None:
            self.name = name

    @property
    def parent_folder_id(self):
        """Gets the parent_folder_id of this FoldersFolder.  # noqa: E501


        :return: The parent_folder_id of this FoldersFolder.  # noqa: E501
        :rtype: str
        """
        return self._parent_folder_id

    @parent_folder_id.setter
    def parent_folder_id(self, parent_folder_id):
        """Sets the parent_folder_id of this FoldersFolder.


        :param parent_folder_id: The parent_folder_id of this FoldersFolder.  # noqa: E501
        :type: str
        """

        self._parent_folder_id = parent_folder_id

    @property
    def name(self):
        """Gets the name of this FoldersFolder.  # noqa: E501


        :return: The name of this FoldersFolder.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this FoldersFolder.


        :param name: The name of this FoldersFolder.  # noqa: E501
        :type: str
        """

        self._name = name

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
        if not isinstance(other, FoldersFolder):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
