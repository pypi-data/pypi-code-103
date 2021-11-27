# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""Exceptions.
"""


class UnknownDataType(Exception):
    """An exception for when the type specified for a request is not registered.
    """

    def __init__(self, data_type: str, message: str = None):
        """Initialize the exception.

        :param str data_type: The data type.
        :param str message: (Optional.) An informational message.
        """
        self.data_type = data_type
        self.message = message


class NotFound(Exception):
    """An exception for when a requested object is not found on the server.
    """

    def __init__(self, url: str, message: str = None):
        """Initialize the exception.

        :param str url: The URL that returned the response.
        :param str message: (Optional.) An informational message.
        """
        self.url = url
        self.message = message


class UnexpectedResponse(Exception):
    """An exception for when the server responds in an unexpected way, such as 5xx-type errors, etc.
    """

    def __init__(self, url: str, code: int, text: str):
        """Initialize the exception.

        :param str url: The URL that returned the response.
        :param int code: The HTTP response code
        :param str text: The body text of the response.
        """
        self.url = url
        self.code = code
        self.text = text


class InvalidResponseData(Exception):
    """An exception for when the server's response has unexpected or invalid data.
    """

    def __init__(self, url: str, name: str, value: str, message: str = None):
        """Initialize the exception.

        :param str url: The URL that returned the response.
        :param str name: The type or name of the value triggering the exception.
        :param str value: The value in question.
        :param str message: (Optional.) An informational message.
        """
        self.url = url
        self.name = name
        self.value = value
        self.message = message
