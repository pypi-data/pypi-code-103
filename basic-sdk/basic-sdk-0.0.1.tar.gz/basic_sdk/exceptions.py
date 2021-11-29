# -*- coding: utf-8 -*-
# @File    : exceptions.py
# @Time    : 2021/11/26 3:49 下午


class BasicException(Exception):
    """
    Service exception base class
    """

    status_code = None
    code = None
    error = None

    def __init__(self, error=""):
        self.error = error or self.error

    @classmethod
    def name(cls) -> str:
        """
        Return class name
        :return: obj name
        """
        return cls.__name__

    def __str__(self):
        return f"{self.name()}({self.error})"


class ServerException(BasicException):
    """
    Internal server exception class
    """

    status_code = 500
    code = 500500
    error = "Internal Server Error"


class InvalidRequest(BasicException):
    """
    Invalid request exception class
    """

    status_code = 422
    code = 422422
    error = "Invalid Request"


class ObjectNotFound(BasicException):
    """
    Object is not exist exception class
    """

    status_code = 404
    code = 404400
    error = "Object Not Found"


class ObjectAlreadyDeleted(ObjectNotFound):
    code = 404401
    error = "Object Already Deleted"


class SchemaError(InvalidRequest):
    """
    Schema Error exception class
    """

    code = 400400
    error = "Schema Error"


class PermissionDenied(InvalidRequest):
    status_code = 403
    code = 403000
    error = "你没有权限访问"
