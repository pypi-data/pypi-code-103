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


class PendingTemplate(object):
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
        'expiration_interval': 'str',
        'webhook_url': 'str',
        'parent_folder_id': 'str',
        'expire_after': 'float',
        'allow_additional_properties': 'bool',
        'description': 'str',
        'public_submissions': 'bool',
        'slack_webhook_url': 'str',
        'path': 'str',
        'public_web_form': 'bool',
        'editable_submissions': 'bool',
        'expire_submissions': 'bool',
        'name': 'str',
        'template_type': 'str',
        'id': 'str',
        'locked': 'bool',
        'redirect_url': 'str'
    }

    attribute_map = {
        'expiration_interval': 'expiration_interval',
        'webhook_url': 'webhook_url',
        'parent_folder_id': 'parent_folder_id',
        'expire_after': 'expire_after',
        'allow_additional_properties': 'allow_additional_properties',
        'description': 'description',
        'public_submissions': 'public_submissions',
        'slack_webhook_url': 'slack_webhook_url',
        'path': 'path',
        'public_web_form': 'public_web_form',
        'editable_submissions': 'editable_submissions',
        'expire_submissions': 'expire_submissions',
        'name': 'name',
        'template_type': 'template_type',
        'id': 'id',
        'locked': 'locked',
        'redirect_url': 'redirect_url'
    }

    def __init__(self, expiration_interval=None, webhook_url=None, parent_folder_id=None, expire_after=None, allow_additional_properties=None, description=None, public_submissions=None, slack_webhook_url=None, path=None, public_web_form=None, editable_submissions=None, expire_submissions=None, name=None, template_type=None, id=None, locked=None, redirect_url=None):  # noqa: E501
        """PendingTemplate - a model defined in OpenAPI"""  # noqa: E501

        self._expiration_interval = None
        self._webhook_url = None
        self._parent_folder_id = None
        self._expire_after = None
        self._allow_additional_properties = None
        self._description = None
        self._public_submissions = None
        self._slack_webhook_url = None
        self._path = None
        self._public_web_form = None
        self._editable_submissions = None
        self._expire_submissions = None
        self._name = None
        self._template_type = None
        self._id = None
        self._locked = None
        self._redirect_url = None
        self.discriminator = None

        if expiration_interval is not None:
            self.expiration_interval = expiration_interval
        self.webhook_url = webhook_url
        self.parent_folder_id = parent_folder_id
        if expire_after is not None:
            self.expire_after = expire_after
        if allow_additional_properties is not None:
            self.allow_additional_properties = allow_additional_properties
        self.description = description
        if public_submissions is not None:
            self.public_submissions = public_submissions
        self.slack_webhook_url = slack_webhook_url
        if path is not None:
            self.path = path
        if public_web_form is not None:
            self.public_web_form = public_web_form
        if editable_submissions is not None:
            self.editable_submissions = editable_submissions
        if expire_submissions is not None:
            self.expire_submissions = expire_submissions
        self.name = name
        if template_type is not None:
            self.template_type = template_type
        if id is not None:
            self.id = id
        if locked is not None:
            self.locked = locked
        self.redirect_url = redirect_url

    @property
    def expiration_interval(self):
        """Gets the expiration_interval of this PendingTemplate.  # noqa: E501


        :return: The expiration_interval of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._expiration_interval

    @expiration_interval.setter
    def expiration_interval(self, expiration_interval):
        """Sets the expiration_interval of this PendingTemplate.


        :param expiration_interval: The expiration_interval of this PendingTemplate.  # noqa: E501
        :type: str
        """
        allowed_values = ["minutes", "hours", "days"]  # noqa: E501
        if expiration_interval not in allowed_values:
            raise ValueError(
                "Invalid value for `expiration_interval` ({0}), must be one of {1}"  # noqa: E501
                .format(expiration_interval, allowed_values)
            )

        self._expiration_interval = expiration_interval

    @property
    def webhook_url(self):
        """Gets the webhook_url of this PendingTemplate.  # noqa: E501


        :return: The webhook_url of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, webhook_url):
        """Sets the webhook_url of this PendingTemplate.


        :param webhook_url: The webhook_url of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._webhook_url = webhook_url

    @property
    def parent_folder_id(self):
        """Gets the parent_folder_id of this PendingTemplate.  # noqa: E501


        :return: The parent_folder_id of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._parent_folder_id

    @parent_folder_id.setter
    def parent_folder_id(self, parent_folder_id):
        """Sets the parent_folder_id of this PendingTemplate.


        :param parent_folder_id: The parent_folder_id of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._parent_folder_id = parent_folder_id

    @property
    def expire_after(self):
        """Gets the expire_after of this PendingTemplate.  # noqa: E501


        :return: The expire_after of this PendingTemplate.  # noqa: E501
        :rtype: float
        """
        return self._expire_after

    @expire_after.setter
    def expire_after(self, expire_after):
        """Sets the expire_after of this PendingTemplate.


        :param expire_after: The expire_after of this PendingTemplate.  # noqa: E501
        :type: float
        """

        self._expire_after = expire_after

    @property
    def allow_additional_properties(self):
        """Gets the allow_additional_properties of this PendingTemplate.  # noqa: E501


        :return: The allow_additional_properties of this PendingTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._allow_additional_properties

    @allow_additional_properties.setter
    def allow_additional_properties(self, allow_additional_properties):
        """Sets the allow_additional_properties of this PendingTemplate.


        :param allow_additional_properties: The allow_additional_properties of this PendingTemplate.  # noqa: E501
        :type: bool
        """

        self._allow_additional_properties = allow_additional_properties

    @property
    def description(self):
        """Gets the description of this PendingTemplate.  # noqa: E501


        :return: The description of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this PendingTemplate.


        :param description: The description of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def public_submissions(self):
        """Gets the public_submissions of this PendingTemplate.  # noqa: E501


        :return: The public_submissions of this PendingTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._public_submissions

    @public_submissions.setter
    def public_submissions(self, public_submissions):
        """Sets the public_submissions of this PendingTemplate.


        :param public_submissions: The public_submissions of this PendingTemplate.  # noqa: E501
        :type: bool
        """

        self._public_submissions = public_submissions

    @property
    def slack_webhook_url(self):
        """Gets the slack_webhook_url of this PendingTemplate.  # noqa: E501


        :return: The slack_webhook_url of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._slack_webhook_url

    @slack_webhook_url.setter
    def slack_webhook_url(self, slack_webhook_url):
        """Sets the slack_webhook_url of this PendingTemplate.


        :param slack_webhook_url: The slack_webhook_url of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._slack_webhook_url = slack_webhook_url

    @property
    def path(self):
        """Gets the path of this PendingTemplate.  # noqa: E501


        :return: The path of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this PendingTemplate.


        :param path: The path of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._path = path

    @property
    def public_web_form(self):
        """Gets the public_web_form of this PendingTemplate.  # noqa: E501


        :return: The public_web_form of this PendingTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._public_web_form

    @public_web_form.setter
    def public_web_form(self, public_web_form):
        """Sets the public_web_form of this PendingTemplate.


        :param public_web_form: The public_web_form of this PendingTemplate.  # noqa: E501
        :type: bool
        """

        self._public_web_form = public_web_form

    @property
    def editable_submissions(self):
        """Gets the editable_submissions of this PendingTemplate.  # noqa: E501


        :return: The editable_submissions of this PendingTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._editable_submissions

    @editable_submissions.setter
    def editable_submissions(self, editable_submissions):
        """Sets the editable_submissions of this PendingTemplate.


        :param editable_submissions: The editable_submissions of this PendingTemplate.  # noqa: E501
        :type: bool
        """

        self._editable_submissions = editable_submissions

    @property
    def expire_submissions(self):
        """Gets the expire_submissions of this PendingTemplate.  # noqa: E501


        :return: The expire_submissions of this PendingTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._expire_submissions

    @expire_submissions.setter
    def expire_submissions(self, expire_submissions):
        """Sets the expire_submissions of this PendingTemplate.


        :param expire_submissions: The expire_submissions of this PendingTemplate.  # noqa: E501
        :type: bool
        """

        self._expire_submissions = expire_submissions

    @property
    def name(self):
        """Gets the name of this PendingTemplate.  # noqa: E501


        :return: The name of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this PendingTemplate.


        :param name: The name of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def template_type(self):
        """Gets the template_type of this PendingTemplate.  # noqa: E501


        :return: The template_type of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._template_type

    @template_type.setter
    def template_type(self, template_type):
        """Sets the template_type of this PendingTemplate.


        :param template_type: The template_type of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._template_type = template_type

    @property
    def id(self):
        """Gets the id of this PendingTemplate.  # noqa: E501


        :return: The id of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this PendingTemplate.


        :param id: The id of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def locked(self):
        """Gets the locked of this PendingTemplate.  # noqa: E501


        :return: The locked of this PendingTemplate.  # noqa: E501
        :rtype: bool
        """
        return self._locked

    @locked.setter
    def locked(self, locked):
        """Sets the locked of this PendingTemplate.


        :param locked: The locked of this PendingTemplate.  # noqa: E501
        :type: bool
        """

        self._locked = locked

    @property
    def redirect_url(self):
        """Gets the redirect_url of this PendingTemplate.  # noqa: E501


        :return: The redirect_url of this PendingTemplate.  # noqa: E501
        :rtype: str
        """
        return self._redirect_url

    @redirect_url.setter
    def redirect_url(self, redirect_url):
        """Sets the redirect_url of this PendingTemplate.


        :param redirect_url: The redirect_url of this PendingTemplate.  # noqa: E501
        :type: str
        """

        self._redirect_url = redirect_url

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
        if not isinstance(other, PendingTemplate):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
