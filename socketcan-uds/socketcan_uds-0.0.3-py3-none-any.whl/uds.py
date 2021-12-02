"""
ISO 14229 UDS protocol
"""
import datetime
import struct
from enum import IntEnum
from queue import Queue, Empty
from threading import Thread
from typing import Optional

import socketcan as socketcan

import logging

LOGGER = logging.getLogger(__name__)


class DiagnosticSession(IntEnum):
    DefaultSession = 1
    ProgrammingSession = 2
    ExtendedDiagnosticSession = 3
    SafetySystemDiagnosticSession = 4


class ResetType(IntEnum):
    HardReset = 1
    KeyOffOnReset = 2
    SoftReset = 3
    EnableRapidPowerShutdown = 4
    DisableRapidPowerShutdown = 5


class ServiceId(IntEnum):
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
    BTW: See how BOSCH managed to fake the ISO numbering.
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


def parse_diagnostic_session_control_response(data: bytes) -> dict:
    """ parse function for specific response """
    values = list(struct.unpack(">BBHH", data))
    # scale both values to seconds
    values[2] = values[2] / 1000
    values[3] = values[3] / 100
    ret = dict(zip(["response_sid", "session", "p2_server_max", "p2*_server_max"], values))
    return ret


def parse_ecu_reset_response(data: bytes) -> dict:
    """ parse function for specific response """
    ret = dict(zip(["response_sid", "rtype", "power_down_time"], data))
    return ret


def parse_security_access_response(data: bytes) -> dict:
    values = list(struct.unpack("BB{0}s".format(len(data) - 2), data))
    keys = ["response_sid", "slevel"]
    if values[1] & 0x1:
        keys.append("seed")
    else:
        keys.append("key")
    ret = dict(zip(keys, values))
    return ret


def parse_read_data_by_id_response(data: bytes) -> dict:
    ret = dict(zip(["response_sid", "did", "data"], struct.unpack(">BH{0}s".format(len(data)-3), data[:3])))
    return ret


SERVICE_TO_PARSER_MAPPING = {ServiceId.DiagnosticSessionControl: parse_diagnostic_session_control_response,
                             ServiceId.EcuReset: parse_ecu_reset_response,
                             ServiceId.ReadDataByIdentifier: parse_read_data_by_id_response,
                             ServiceId.SecurityAccess: parse_security_access_response,
                             }


class Uds:
    """
    UDS Protocol class

    depends on socketcan
    therefore runs on linux only
    """

    def __init__(self,
                 socket: socketcan.CanIsoTpSocket,
                 timeout: int = 5,
                 ):
        """
        Constructor

        :param socket: A SocketCAN IsoTp socket.
        """
        self._s = socket
        self.timeout = timeout
        self.rx_queue = Queue()
        self.rx_handler = Thread(target=self._handle_rx)
        self.rx_handler.setDaemon(True)
        self.rx_handler.start()

    # basic functionality

    def _handle_rx(self) -> None:
        """
        Puts data from socket into a queue,
        where the requester (main thread) in self.recv()
        :return: Nothing.
        """
        while True:
            self.rx_queue.put(self._s.recv())

    def _send(self, data: bytes) -> int:
        """
        Sends data to the socket.
        :param data: The data to be sent.
        :return: The length of data that was sent.
        """
        return self._s.send(data=data)

    def _recv(self) -> Optional[bytes]:
        """
        Receives data from rx_queue in case it was filled by
        rx_handler.
        The underlying queue mechanism may raise an Empty Exception.
        :return: Data bytes.
        """
        return self.rx_queue.get(timeout=self.timeout)

    def request(self, req: bytes) -> Optional[dict]:
        """
        Service request function
        It handles transmission, reception and check if a negative response error should be raised
        :param req: The request as bytes.
        :return: The response as bytes.
        :raises: Subtypes of NegativeResponse, UdsTimeoutError, etc.
        """
        sid = ServiceId(req[0])
        bytes_sent = self._send(req)
        ts_request_sent = datetime.datetime.now()
        if bytes_sent != len(req):
            LOGGER.error("bytes_sent != len(data)")
        try:
            resp = self._recv()
        except Empty:
            raise UdsTimeoutError
        else:
            time_for_response = datetime.datetime.now() - ts_request_sent
            LOGGER.debug("Response received after timedelta {0}".format(time_for_response))
            is_positive_response = (resp[0] == (sid | 0x40))
            if not is_positive_response:
                response_code = ResponseCode(resp[0])
                LOGGER.error("Request {0} returned {1}".format(req.hex(), response_code.name))
                raise RESPONSECODE_TO_EXCEPTION_MAPPING.get(response_code)
            else:
                parser_function = SERVICE_TO_PARSER_MAPPING.get(sid)
                ret = {"raw": resp}
                if parser_function is not None and callable(parser_function):
                    ret.update(parser_function(resp))
                return ret

    # convenience functions for specific services

    def diagnostic_session_control(self,
                                   session: DiagnosticSession = DiagnosticSession.ExtendedDiagnosticSession) -> dict:
        """
        Basic uds service diagnostic session control.
        :param session: The requested diagnostic session.
        :return: The data that was returned.
        """
        assert session in DiagnosticSession

        req = struct.pack("BB", ServiceId.DiagnosticSessionControl, session)
        return self.request(req=req)

    def ecu_reset(self,
                  rtype: ResetType = ResetType.HardReset) -> dict:
        """
        Basic uds service ecu reset.
        :param rtype: The requested ResetType.
        :return: The data that was returned.
        """
        assert rtype in ResetType

        req = struct.pack("BB", ServiceId.EcuReset, rtype)
        return self.request(req=req)

    def security_access(self,
                        slevel: int,
                        seedkey: bytes,
                        ) -> dict:
        """
        Basic uds service security access.
        The method is called SEED&KEY and was defined in KWP2000(ISO14230).
        The idea is to have a secret needed to compute a key of a given seed.
        In reality the seed/key is 4 bytes big endian and the seed2key function is a simple function,
        e.g. adding some value, rotating the seed, xor it with a mask value etc.

        Each security level is a tuple of an uneven number to request a seed
        and the next (even) number to post a key.
        :param slevel: The security level. Uneven=SeedRequest, Even=KeyPost
        :param seedkey: The seed/key bytes.
        :return: The data that was returned.
        """
        if slevel not in range(0x100):
            raise ValueError("Value {0} is not in range 0-0xFF".format(slevel))

        req = bytearray(struct.pack("BB", ServiceId.EcuReset, slevel))
        if (slevel & 0x1) == 0:
            req.extend(seedkey)
        return self.request(req=req)

    def read_data_by_id(self,
                        did: int) -> dict:
        """
        Basic uds service read data by id.
        :param did: The diagnostic identifier to be read.
        :return: The data that was returned.
        :raises TimeoutError
        """
        if did not in range(0x10000):
            raise ValueError("Value {0} is not in range 0-0xFFFF".format(did))
        req = struct.pack(">BH", ServiceId.ReadDataByIdentifier, did)
        return self.request(req=req)


# Exceptions

class UdsProtocolException(Exception):
    pass


class UdsTimeoutError(UdsProtocolException):
    pass


class NegativeResponse(UdsProtocolException):
    pass


class GeneralReject(NegativeResponse):
    pass


class ServiceNotSupported(NegativeResponse):
    pass


class SubfunctionNotSupported(NegativeResponse):
    pass


class IncorrectMessageLengthOrInvalidFormat(NegativeResponse):
    pass


class ResponseTooLong(NegativeResponse):
    pass


class BusyRepeatRequest(NegativeResponse):
    pass


class ConditionsNotCorrect(NegativeResponse):
    pass


class RequestSequenceError(NegativeResponse):
    pass


class NoResponseFromSubnetComponent(NegativeResponse):
    pass


class FaultPreventsExecutionOfRequestedAction(NegativeResponse):
    pass


class RequestOutOfRange(NegativeResponse):
    pass


class SecurityAccessDenied(NegativeResponse):
    pass


class InvalidKey(NegativeResponse):
    pass


class ExceededNumberOfAttempts(NegativeResponse):
    pass


class RequiredTimeDelayNotExpired(NegativeResponse):
    pass


class UploadDownloadNotAccepted(NegativeResponse):
    pass


class TransferDataSuspended(NegativeResponse):
    pass


class GeneralProgrammingFailure(NegativeResponse):
    pass


class WrongBlockSequenceCounter(NegativeResponse):
    pass


class RequestCorrectlyReceivedButResponsePending(NegativeResponse):
    # This is actually not a Negative Response, see how we can handle this in program flow,
    # maybe base on Exception instead.
    pass


class SubFunctionNotSupportedInActiveSession(NegativeResponse):
    pass


class ServiceNotSupportedInActiveSession(NegativeResponse):
    pass


RESPONSECODE_TO_EXCEPTION_MAPPING = {
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
