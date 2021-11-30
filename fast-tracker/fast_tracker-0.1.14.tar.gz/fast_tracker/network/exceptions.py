# -*- coding: utf-8 -*-


class NetworkInterfaceException(Exception):
    pass


class ForceAgentRestart(NetworkInterfaceException):
    pass


class ForceAgentDisconnect(NetworkInterfaceException):
    pass


class DiscardDataForRequest(NetworkInterfaceException):
    pass


class RetryDataForRequest(NetworkInterfaceException):
    pass
