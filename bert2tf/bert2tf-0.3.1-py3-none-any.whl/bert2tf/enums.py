from enum import IntEnum, EnumMeta

from .baml import BAMLCompatibleType


class EnumType(BAMLCompatibleType, EnumMeta):
    pass


class BetterEnum(IntEnum, metaclass=EnumType):
    def __str__(self):
        return self.name

    @classmethod
    def from_string(cls, s: str):
        """Parse the enum from a string"""
        try:
            return cls[s.upper()]
        except KeyError:
            raise ValueError(f'{s.upper()} is not a valid enum for {cls}')


class SocketType(BetterEnum):
    """Enums for representing the socket type in a pea """
    PULL_BIND = 0
    PULL_CONNECT = 1
    PUSH_BIND = 2
    PUSH_CONNECT = 3
    SUB_BIND = 4
    SUB_CONNECT = 5
    PUB_BIND = 6
    PUB_CONNECT = 7
    PAIR_BIND = 8
    PAIR_CONNECT = 9
    ROUTER_BIND = 10
    DEALER_CONNECT = 11

    @property
    def is_bind(self) -> bool:
        """

        :return: if this socket is using `bind` protocol
        """
        return self.value % 2 == 0

    @property
    def paired(self) -> 'SocketType':
        """

        :return: a paired
        """
        return {
            SocketType.PULL_BIND: SocketType.PUSH_CONNECT,
            SocketType.PULL_CONNECT: SocketType.PUSH_BIND,
            SocketType.SUB_BIND: SocketType.PUB_CONNECT,
            SocketType.SUB_CONNECT: SocketType.PUB_BIND,
            SocketType.PAIR_BIND: SocketType.PAIR_CONNECT,
            SocketType.PUSH_CONNECT: SocketType.PULL_BIND,
            SocketType.PUSH_BIND: SocketType.PULL_CONNECT,
            SocketType.PUB_CONNECT: SocketType.SUB_BIND,
            SocketType.PUB_BIND: SocketType.SUB_CONNECT,
            SocketType.PAIR_CONNECT: SocketType.PAIR_BIND
        }[self]


class LogVerbosity(BetterEnum):
    """Verbosity level of the logger """
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class PeaRoleType(BetterEnum):
    """ The enum of a Pea role

    """
    REPLICA = 0
    HEAD = 1
    TAIL = 2
    SINGLETON = 3


class RuntimeBackendType(BetterEnum):
    """Type of backend."""

    THREAD = 0
    PROCESS = 1
