# Copyright (c) 2021 Phoenix Contact. All rights reserved.
# Licensed under the MIT. See LICENSE file in the project root for full license information.
import errno
import socket
import ssl
import struct
import weakref
from abc import ABCMeta, abstractmethod

from PyPlcnextRsc.common.exceptions import CommonRemotingException, ErrType

DEBUG = True

__all__ = ["CreateSockWrapper"]


class _PrimitivesConvert:
    class _BinaryConverter:
        def __init__(self, fmt):
            self._fmt = fmt
            st = struct.Struct(fmt.format(1))
            self.size = st.size
            self.format = st.format

        def pack(self, data):
            return struct.pack(self.format, data)

        def unpack(self, data):
            return struct.unpack(self.format, data)[0]

    SByte = _BinaryConverter("<{:d}b")
    Int16 = _BinaryConverter("<{:d}h")
    Int32 = _BinaryConverter("<{:d}i")
    Int64 = _BinaryConverter("<{:d}q")
    Byte = _BinaryConverter("<{:d}B")
    Char = Byte
    UInt16 = _BinaryConverter("<{:d}H")
    UInt32 = _BinaryConverter("<{:d}I")
    UInt64 = _BinaryConverter("<{:d}Q")
    Boolean = _BinaryConverter("<{:d}?")
    Double = _BinaryConverter("<{:d}d")
    Float = _BinaryConverter("<{:d}f")


class BinaryReader:
    def __init__(self, socket_wrapper):
        self.socket_wrapper = weakref.proxy(socket_wrapper)
        self.getDouble = lambda: self._read_and_unpack(_PrimitivesConvert.Double)
        self.getFloat = lambda: self._read_and_unpack(_PrimitivesConvert.Float)
        self.getUnsignedLong = lambda: self._read_and_unpack(_PrimitivesConvert.UInt64)
        self.getSignedLong = lambda: self._read_and_unpack(_PrimitivesConvert.Int64)
        self.getUnsignedInteger = lambda: self._read_and_unpack(_PrimitivesConvert.UInt32)
        self.getSignedInteger = lambda: self._read_and_unpack(_PrimitivesConvert.Int32)
        self.getUnsignedShort = lambda: self._read_and_unpack(_PrimitivesConvert.UInt16)
        self.getSignedShort = lambda: self._read_and_unpack(_PrimitivesConvert.Int16)
        self.getUnsignedByte = lambda: self._read_and_unpack(_PrimitivesConvert.Byte)
        self.getSignedByte = lambda: self._read_and_unpack(_PrimitivesConvert.SByte)
        self.getBoolean = lambda: self._read_and_unpack(_PrimitivesConvert.Boolean)

    def getString(self, size: int, encoding: str, isChars=False) -> str:
        # if isChars:
        #     buff = self.getByteBuffer(size)
        # else:
        buff = self.getByteBuffer(size)[:-1]
        return buff.decode(encoding)

    def getChar(self, encoding: str) -> str:
        buff = self.getByteBuffer(1)
        return buff.decode(encoding)

    def getByteBuffer(self, length) -> bytes:
        return self.socket_wrapper.read(length)

    def _read_and_unpack(self, converter):
        return converter.unpack(self.getByteBuffer(converter.size))


class BinaryWriter:
    def __init__(self, socket_wrapper):
        self.socket_wrapper = socket_wrapper
        self.setDouble = lambda value: self._pack_and_write(_PrimitivesConvert.Double, value)
        self.setFloat = lambda value: self._pack_and_write(_PrimitivesConvert.Float, value)
        self.setUnsignedLong = lambda value: self._pack_and_write(_PrimitivesConvert.UInt64, value)
        self.setSignedLong = lambda value: self._pack_and_write(_PrimitivesConvert.Int64, value)
        self.setUnsignedInteger = lambda value: self._pack_and_write(_PrimitivesConvert.UInt32, value)
        self.setSignedInteger = lambda value: self._pack_and_write(_PrimitivesConvert.Int32, value)
        self.setUnsignedShort = lambda value: self._pack_and_write(_PrimitivesConvert.UInt16, value)
        self.setSignedShort = lambda value: self._pack_and_write(_PrimitivesConvert.Int16, value)
        self.setUnsignedByte = lambda value: self._pack_and_write(_PrimitivesConvert.Byte, value)
        self.setSignedByte = lambda value: self._pack_and_write(_PrimitivesConvert.SByte, value)
        self.setBoolean = lambda value: self._pack_and_write(_PrimitivesConvert.Boolean, value)

    def setString(self, string: str, encoding: str, isChars=False):
        string = string + '\0'
        data = string.encode(encoding)
        self.setByteBuffer(data)

    def setChar(self, char: str, encoding: str):
        if len(char) > 1:
            raise ValueError("char should only contain 1 character")
        data = char.encode(encoding)
        self.setByteBuffer(data)

    def setByteBuffer(self, data: bytes):
        self.socket_wrapper.Write(data)

    def _pack_and_write(self, converter, value):
        self.setByteBuffer(converter.pack(value))


class plcNextWrapperBase(metaclass=ABCMeta):
    def __init__(self, info, config):
        self.info = weakref.proxy(info)
        self.config = weakref.proxy(config)
        self.binaryReader = BinaryReader(self)
        self.binaryWriter = BinaryWriter(self)

    @abstractmethod
    def isConnected(self):
        ...

    @abstractmethod
    def connect(self):
        ...

    @abstractmethod
    def disconnect(self):
        ...

    @abstractmethod
    def read(self, size) -> bytes: ...

    @abstractmethod
    def recv_into(self, buffer, size) -> int:
        ...

    @abstractmethod
    def Write(self, data: bytes): ...

    @abstractmethod
    def flush(self): ...

    @abstractmethod
    def rollback(self): ...


class PySocket(plcNextWrapperBase):
    def __init__(self, info, config):
        super().__init__(info, config)
        self._socket = self.prepareSocket()
        self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.data = bytearray()
        self._connected = False

    @abstractmethod
    def prepareSocket(self):
        ...

    @abstractmethod
    def beforeConnect(self):
        ...

    @abstractmethod
    def afterConnect(self):
        ...

    def isConnected(self):
        return self._connected

    def connect(self):
        try:
            self._socket.settimeout(self.config.timeout)
        except:
            pass
        self.beforeConnect()
        while True:
            try:
                self._socket.connect(self.info.getAddr())
                break
            except socket.error as e:
                if isinstance(e, socket.timeout) or e.errno in (errno.ECONNREFUSED, errno.EHOSTUNREACH):
                    raise CommonRemotingException(message="Can not connect to device", cause=e, err=ErrType.SOCKET_TIMEOUT)
                if e.errno != errno.EINTR:
                    raise CommonRemotingException(message="Can not connect to device", cause=e, err=ErrType.SOCKET_UNSPECIFIED)

        self.afterConnect()
        self._connected = True

    def disconnect(self):
        self._socket.close()
        self._connected = False

    def read(self, size) -> bytes:
        remain = size
        ret = bytearray()
        try:
            while remain:
                data = self._socket.recv(remain)
                if len(data) == 0:
                    raise
                ret.extend(data)
                remain -= len(data)
            # if DEBUG:
            #     import inspect
            #     stacks = inspect.stack()
            #     stacks = stacks[1:6]
            #     infos = []
            #     for stack in stacks:
            #         fileName = os.path.split(stack.filename)[-1]
            #         infos.append((fileName, stack.lineno, stack.function))
            #     print("_READ_")
            #     print(str(infos))
            #     print(data)
            #     print("--------------------------\n\n")
            return ret
        except socket.error as e:
            self._connected = False
            if e.errno in (errno.ECONNABORTED,):
                raise CommonRemotingException(message="Can not read from device", cause=e, err=ErrType.SOCKET_ABORTED)
            elif e.errno == errno.ETIMEDOUT or isinstance(e, socket.timeout):
                raise CommonRemotingException(message="Can not read from device", cause=e, err=ErrType.SOCKET_TIMEOUT)
            else:
                raise CommonRemotingException(message="Can not read from device", cause=e, err=ErrType.SOCKET_UNSPECIFIED)

    def recv_into(self, buffer, size):
        try:
            sck = self._socket
            view = memoryview(buffer)
            while size > 0:
                nbytes = sck.recv_into(view, size)
                if nbytes == 0:
                    raise
                view = view[nbytes:]
                size -= nbytes
        except Exception as e:
            self._connected = False
            raise CommonRemotingException(message="Can not read from device", cause=e, err=ErrType.SOCKET_UNSPECIFIED)

    def Write(self, data):
        # if DEBUG:
        #     import inspect
        #     stacks = inspect.stack()
        #     stacks = stacks[1:6]
        #     infos = []
        #     for stack in stacks:
        #         fileName = os.path.split(stack.filename)[-1]
        #         infos.append((fileName, stack.lineno, stack.function))
        #     print('\t' * 10 + "_WRITE_")
        #     print('\t' * 10 + str(infos))
        #     print('\t' * 10 + str(data))
        #     print("--------------------------\n\n")
        self.data.extend(data)

    def flush(self):
        try:
            buff = self.data
            self._socket.sendall(buff)
            buff.clear()
        except Exception as e:
            self._connected = False
            raise CommonRemotingException(message="Can not read from device", cause=e, err=ErrType.SOCKET_UNSPECIFIED)

    def rollback(self):
        self.data.clear()
        skt = self._socket
        skt.setblocking(False)
        for i in range(1024):
            try:
                skt.recvfrom(2048)
            except:
                break
        skt.setblocking(True)


class PySSLSocket(PySocket):
    def prepareSocket(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE
        context.check_hostname = False
        return context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    def beforeConnect(self):
        ...

    def afterConnect(self):
        ...


class PyNormalSocket(PySocket):
    def prepareSocket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def beforeConnect(self):
        ...

    def afterConnect(self):
        ...


def CreateSockWrapper(info, config) -> plcNextWrapperBase:
    if config.useTls:
        return PySSLSocket(info, config)
    else:
        return PyNormalSocket(info, config)
