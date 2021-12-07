# -*- coding: utf-8 -*-
# Author: Orlando Chen
# Create: 15 Aug, 2017
# Modified: 13 Sep, 2018

class ArrayIndexOutOfBoundsException(Exception):
    def __init__(self, message):
        super(ArrayIndexOutOfBoundsException, self).__init__(message)


class CannotParseException(Exception):
    def __init__(self, message):
        super(CannotParseException, self).__init__(message)


class EmptyCollectionElementException(Exception):
    def __init__(self, message):
        super(EmptyCollectionElementException, self).__init__(message)


class InvalidArithException(Exception):
    def __init__(self, message):
        super(InvalidArithException, self).__init__(message)


class InvalidParamException(Exception):
    def __init__(self, message):
        super(InvalidParamException, self).__init__(message)


class NoAvailableResourcesFoundException(Exception):
    def __init__(self, message):
        super(NoAvailableResourcesFoundException, self).__init__(message)


class NullPointerException(Exception):
    def __init__(self, message):
        super(NullPointerException, self).__init__(message)

class NotImplementedException(Exception):
    def __init__(self, message):
        super(NotImplementedException, self).__init__(message)

class TcpConnectionException(Exception):
    def __init__(self, message):
        super(TcpConnectionException, self).__init__(message)


class UdpConnectionException(Exception):
    def __init__(self, message):
        super(UdpConnectionException, self).__init__(message)


class SQLInjectionException(Exception):
    def __init__(self, message):
        super(SQLInjectionException, self).__init__(message)


class SQLConnectionException(Exception):
    def __init__(self, message):
        super(SQLConnectionException, self).__init__(message)

class RedisConnectionException(Exception):
    def __init__(self, message):
        super(RedisConnectionException, self).__init__(message)
