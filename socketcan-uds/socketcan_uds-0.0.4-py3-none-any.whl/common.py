""" module:: uds.common
    :platform: Posix
    :synopsis: An abstraction of ISO 14229 UDS protocol
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: GPL v3
"""

import struct
from enum import IntEnum

import logging

LOGGER = logging.getLogger(__name__)


class DiagnosticSession(IntEnum):
    """
    Diagnostic session enum
    """
    DefaultSession = 1
    ProgrammingSession = 2
    ExtendedDiagnosticSession = 3
    SafetySystemDiagnosticSession = 4


class ResetType(IntEnum):
    """
    Reset type enum
    """
    HardReset = 1
    KeyOffOnReset = 2
    SoftReset = 3
    EnableRapidPowerShutdown = 4
    DisableRapidPowerShutdown = 5


class ServiceId(IntEnum):
    """
    Service id enum
    """
    # Diagnostic and Communication Management
    DiagnosticSessionControl = 0x10
    EcuReset = 0x11
    SecurityAccess = 0x27
    CommunicationControl = 0x28
    TesterPresent = 0x3E
    AccessTimingParameter = 0x83
    SecuredDataTransmission = 0x84
    ControlDtcSettings = 0x85
    ResponseOnEvent = 0x86
    LinkControl = 0x87

    # Data Transmission
    ReadDataByIdentifier = 0x22
    ReadMemoryByAddress = 0x23
    ReadScalingDataByIdentifier = 0x24
    ReadDataByPeriodicIdentifier = 0x2A
    DynamicallyDefineDataIdentifier = 0x2C
    WriteDataByIdentifier = 0x2E
    WriteMemoryByAddress = 0x3D

    # Stored Data Transmission
    ClearDiagnosticInformation = 0x14
    ReadDtcInformation = 0x19

    # Input / Output Control
    InputOutputByIdentifier = 0x2F

    # Remote Activation of Routine
    RoutineControl = 0x31

    # Upload / Download
    RequestDownload = 0x34
    RequestUpload = 0x35
    DataTransfer = 0x36
    RequestTransferExit = 0x37


class ResponseCode(IntEnum):
    """
    UDS Negative Response Codes

    Some Explanation, when ISO14229 (UDS) was made,
    it had to be compatible with the preceding ISO14230 (KWP2000)
    so everything up to the 0x40 range is nearly identical.
    BTW: See how BOSCH managed to fake the ISO numbering?
    There are some unofficial ranges for different topics
    0x10-0x1F, 0x20-0x2F and so on.
    """
    # tester side error
    GeneralReject = 0x10
    ServiceNotSupported = 0x11
    SubFunctionNotSupported = 0x12
    IncorrectMessageLengthOrInvalidFormat = 0x13
    ResponseTooLong = 0x14

    # device side error
    BusyRepeatRequest = 0x21
    ConditionsNotCorrect = 0x22
    RequestSequenceError = 0x24
    NoResponseFromSubnetComponent = 0x25
    FaultPreventsExecutionOfRequestedAction = 0x26

    # function side error
    RequestOutOfRange = 0x31
    SecurityAccessDenied = 0x33
    InvalidKey = 0x35
    ExceededNumberOfAttempts = 0x36
    RequiredTimeDelayNotExpired = 0x37

    # 0x38-0x4F Reserved by Extended Data Link Security Document

    UploadDownloadNotAccepted = 0x70
    TransferDataSuspended = 0x71
    GeneralProgrammingFailure = 0x72
    WrongBlockSequenceCounter = 0x73

    RequestCorrectlyReceivedButResponsePending = 0x78
    # This is essentially not an Error, it is just a delay information.
    # This Response Code is due to the fact that standard autosar modules do not necessarily run on the same time disc
    # and no IPC method has every been defined for Autosar.

    SubFunctionNotSupportedInActiveSession = 0x7E
    ServiceNotSupportedInActiveSession = 0x7F


def parse_diagnostic_session_control_response(resp: bytes) -> dict:
    """
    Parse diagnostic session control response
    :param resp: The response message in bytes.
    :return: A dictionary with response specific values.
    """
    values = list(struct.unpack(">BBHH", resp))
    # scale both values to seconds
    values[2] = values[2] / 1000
    values[3] = values[3] / 100
    ret = dict(zip(["response_sid", "session", "p2_server_max", "p2*_server_max"], values))
    return ret


def parse_ecu_reset_response(resp: bytes) -> dict:
    """
    Parse ecu reset response
    :param resp: The response message in bytes.
    :return: A dictionary with response specific values.
    """
    ret = dict(zip(["response_sid", "rtype", "power_down_time"], resp))
    return ret


def parse_security_access_response(resp: bytes) -> dict:
    """
    Parse security access response
    :param resp: The response message in bytes.
    :return: A dictionary with response specific values.
    """
    values = list(struct.unpack("BB{0}s".format(len(resp) - 2), resp))
    keys = ["response_sid", "slevel"]
    if values[1] & 0x1:
        keys.append("seed")
    else:
        keys.append("key")
    ret = dict(zip(keys, values))
    return ret


def parse_read_data_by_id_response(resp: bytes) -> dict:
    """
    Parse read data by id response
    :param resp: The response message in bytes.
    :return: A dictionary with response specific values.
    """
    ret = dict(zip(["response_sid", "did", "data"], struct.unpack(">BH{0}s".format(len(resp) - 3), resp)))
    return ret


SERVICE_TO_PARSER_MAPPING = {ServiceId.DiagnosticSessionControl: parse_diagnostic_session_control_response,
                             ServiceId.EcuReset: parse_ecu_reset_response,
                             ServiceId.ReadDataByIdentifier: parse_read_data_by_id_response,
                             ServiceId.SecurityAccess: parse_security_access_response,
                             }


def parse_response(req: bytes,
                   resp: bytes) -> dict:
    """
    A generic function to parse a service response.
    In case of negative response, it raises the appropriate protocol exceptions.
    Otherwise it calls a service specific parser and returns a dictionary with the contents.
    The UDS protocol was not designed properly, so the request is also needed to process the response.
    :param req: The request bytes.
    :param resp: The response bytes.
    :return: A dictionary with response specific values.
    """
    raise_for_exception(req=req,
                        resp=resp)
    sid = ServiceId(req[0])
    parser_function = SERVICE_TO_PARSER_MAPPING.get(sid)
    ret = {"raw": resp}
    if parser_function is not None and callable(parser_function):
        ret.update(parser_function(resp))
    return ret


def raise_for_exception(req: bytes,
                        resp: bytes) -> None:
    """
    In case of negative response, raise the appropriate protocol exceptions.
    :param req: The request bytes.
    :param resp: The response bytes.
    :return: Nothing.
    """
    sid = ServiceId(req[0])
    is_positive_response = (resp[0] == (sid | 0x40))
    if not is_positive_response:
        response_code = ResponseCode(resp[0])
        LOGGER.error("Request {0} returned {1}".format(req.hex(), response_code.name))
        raise RESPONSE_CODE_TO_EXCEPTION_MAPPING.get(response_code)


# Exceptions from client perspective

class UdsProtocolException(Exception):
    """
    The base exception for UDS
    """
    pass


class UdsTimeoutError(UdsProtocolException):
    """
    A (socket/message/protocol) timeout
    """
    pass


class NegativeResponse(UdsProtocolException):
    """
    The base negative response exception
    """
    pass


class GeneralReject(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class ServiceNotSupported(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class SubfunctionNotSupported(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class IncorrectMessageLengthOrInvalidFormat(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class ResponseTooLong(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class BusyRepeatRequest(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class ConditionsNotCorrect(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class RequestSequenceError(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class NoResponseFromSubnetComponent(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class FaultPreventsExecutionOfRequestedAction(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class RequestOutOfRange(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class SecurityAccessDenied(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class InvalidKey(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class ExceededNumberOfAttempts(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class RequiredTimeDelayNotExpired(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class UploadDownloadNotAccepted(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class TransferDataSuspended(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class GeneralProgrammingFailure(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class WrongBlockSequenceCounter(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class RequestCorrectlyReceivedButResponsePending(NegativeResponse):
    # This is actually not a Negative Response, see how we can handle this in program flow,
    # maybe base on Exception instead.
    """
    Protocol specific exception
    """
    pass


class SubFunctionNotSupportedInActiveSession(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


class ServiceNotSupportedInActiveSession(NegativeResponse):
    """
    Protocol specific exception
    """
    pass


RESPONSE_CODE_TO_EXCEPTION_MAPPING = {
    ResponseCode.GeneralReject: GeneralReject,
    ResponseCode.ServiceNotSupported: ServiceNotSupported,
    ResponseCode.SubFunctionNotSupported: SubfunctionNotSupported,
    ResponseCode.IncorrectMessageLengthOrInvalidFormat: IncorrectMessageLengthOrInvalidFormat,
    ResponseCode.ResponseTooLong: ResponseTooLong,
    ResponseCode.BusyRepeatRequest: BusyRepeatRequest,
    ResponseCode.ConditionsNotCorrect: ConditionsNotCorrect,
    ResponseCode.RequestSequenceError: RequestSequenceError,
    ResponseCode.NoResponseFromSubnetComponent: NoResponseFromSubnetComponent,
    ResponseCode.FaultPreventsExecutionOfRequestedAction: FaultPreventsExecutionOfRequestedAction,
    ResponseCode.RequestOutOfRange: RequestOutOfRange,
    ResponseCode.SecurityAccessDenied: SecurityAccessDenied,
    ResponseCode.InvalidKey: InvalidKey,
    ResponseCode.ExceededNumberOfAttempts: ExceededNumberOfAttempts,
    ResponseCode.RequiredTimeDelayNotExpired: RequiredTimeDelayNotExpired,
    ResponseCode.UploadDownloadNotAccepted: UploadDownloadNotAccepted,
    ResponseCode.TransferDataSuspended: TransferDataSuspended,
    ResponseCode.GeneralProgrammingFailure: GeneralProgrammingFailure,
    ResponseCode.WrongBlockSequenceCounter: WrongBlockSequenceCounter,
    ResponseCode.RequestCorrectlyReceivedButResponsePending: RequestCorrectlyReceivedButResponsePending,
    ResponseCode.SubFunctionNotSupportedInActiveSession: SubFunctionNotSupportedInActiveSession,
    ResponseCode.ServiceNotSupportedInActiveSession: ServiceNotSupportedInActiveSession,
}
