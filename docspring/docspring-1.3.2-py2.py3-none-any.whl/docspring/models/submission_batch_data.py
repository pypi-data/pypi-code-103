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


class SubmissionBatchData(object):
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
        'metadata': 'object',
        'submissions': 'list[SubmissionDataBatchRequest]',
        'template_id': 'str',
        'test': 'bool'
    }

    attribute_map = {
        'metadata': 'metadata',
        'submissions': 'submissions',
        'template_id': 'template_id',
        'test': 'test'
    }

    def __init__(self, metadata=None, submissions=None, template_id=None, test=None):  # noqa: E501
        """SubmissionBatchData - a model defined in OpenAPI"""  # noqa: E501

        self._metadata = None
        self._submissions = None
        self._template_id = None
        self._test = None
        self.discriminator = None

        if metadata is not None:
            self.metadata = metadata
        self.submissions = submissions
        self.template_id = template_id
        if test is not None:
            self.test = test

    @property
    def metadata(self):
        """Gets the metadata of this SubmissionBatchData.  # noqa: E501


        :return: The metadata of this SubmissionBatchData.  # noqa: E501
        :rtype: object
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        """Sets the metadata of this SubmissionBatchData.


        :param metadata: The metadata of this SubmissionBatchData.  # noqa: E501
        :type: object
        """

        self._metadata = metadata

    @property
    def submissions(self):
        """Gets the submissions of this SubmissionBatchData.  # noqa: E501


        :return: The submissions of this SubmissionBatchData.  # noqa: E501
        :rtype: list[SubmissionDataBatchRequest]
        """
        return self._submissions

    @submissions.setter
    def submissions(self, submissions):
        """Sets the submissions of this SubmissionBatchData.


        :param submissions: The submissions of this SubmissionBatchData.  # noqa: E501
        :type: list[SubmissionDataBatchRequest]
        """
        if submissions is None:
            raise ValueError("Invalid value for `submissions`, must not be `None`")  # noqa: E501

        self._submissions = submissions

    @property
    def template_id(self):
        """Gets the template_id of this SubmissionBatchData.  # noqa: E501


        :return: The template_id of this SubmissionBatchData.  # noqa: E501
        :rtype: str
        """
        return self._template_id

    @template_id.setter
    def template_id(self, template_id):
        """Sets the template_id of this SubmissionBatchData.


        :param template_id: The template_id of this SubmissionBatchData.  # noqa: E501
        :type: str
        """

        self._template_id = template_id

    @property
    def test(self):
        """Gets the test of this SubmissionBatchData.  # noqa: E501


        :return: The test of this SubmissionBatchData.  # noqa: E501
        :rtype: bool
        """
        return self._test

    @test.setter
    def test(self, test):
        """Sets the test of this SubmissionBatchData.


        :param test: The test of this SubmissionBatchData.  # noqa: E501
        :type: bool
        """

        self._test = test

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
        if not isinstance(other, SubmissionBatchData):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
