from abc import ABC, abstractproperty


class MsrMetaData(ABC):

    @abstractproperty
    def get_keys(self):
        pass

    @abstractproperty
    def get_expected_key(self):
        pass


class MsrRecord(MsrMetaData):
    keys: list[str] = ["KW", "LEN", "MN", "LIB", "BT", "KT", "LT", "?0", "PA", "ST", "?1", "?2", "?3", 'END']
    expected_key = "[MSR:RECORD]"

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key


class EamRecord(MsrMetaData):
    keys: list[str] = ["KW", "LEN", "VN", "?0", "DT", "VT", "PI", 'EX']
    expected_key: str = "[EAM:RECORD]"

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key


class PbvObjpath(MsrMetaData):
    keys: list[str] = ["KW", "LEN", "LB", "FN"]
    expected_key = "[PBV:OBJPATH]"

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key


class MsrRef(MsrMetaData):
    keys: list[str] = ["KW", "MN"]
    expected_key = "[LAD:MSR_REF]"

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key


class ParaRef(MsrMetaData):
    keys: list[str] = ["KW", "VN", "DT", "?0", "PI", "END"]
    expected_key = "[LAD:PARA_REF]"

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key


class ParaData(MsrMetaData):
    expected_key: str = "[PARA:PARADATA]"
    keys: list[str] = ["KN", "L1", "K1", "L2", "K2"]
    secondary_dict_len: int = 5

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key

    @property
    def get_len(self) -> int:
        return self.secondary_dict_len


class UidAcc(MsrMetaData):
    expected_key = "[UID:ACCMSR]"
    keys: list[str] = ["USER", "ACC"]
    secondary_dict_len: int = 2

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key

    @property
    def get_len(self) -> int:
        return self.secondary_dict_len


class Gwy(MsrMetaData):
    expected_key = ["[GWY:ACCEAM]", "[GWY:ACCMSR]"]
    keys: list[str] = ["GN", "G1", "G2"]
    secondary_dict_len: int = 3

    @property
    def get_keys(self) -> list[list]:
        return self.keys

    @property
    def get_expected_key(self) -> str:
        return self.expected_key

    @property
    def get_len(self) -> int:
        return self.secondary_dict_len
