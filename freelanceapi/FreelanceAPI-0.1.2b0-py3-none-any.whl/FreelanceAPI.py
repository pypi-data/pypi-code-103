from .hwm.HwmDict import Hw2BlobDict, HwmDict
from .hwm.HwmStr import Hw2BlobStr, HwmStr
from .msr.MsrDict import (
    EamRecordDict, GwyDict, MsrDict, MsrRecordDict, MsrRefDict, ParaDataDict, ParaRefDict, PbvObjpathDict, UidAccDict
    )
from .msr.MsrStr import (
    EamRecordStr, GwyStr, MsrRecordStr, MsrRefStr, MsrStr, ParaDataStr, ParaRefStr, PbvObjpathStr, UidAccStr
    )
from .project.ProjectDict import PbNodeDict
from .project.ProjectStr import PbNodeStr


class ExportedFreelanceFactories:
    _msr_factories = {
        "[PARA:PARADATA]": (ParaDataDict, ParaDataStr),
        "[UID:ACCMSR]'": (UidAccDict, UidAccStr),
        "[GWY:ACCEAM]": (GwyDict, GwyStr),
        "[GWY:ACCMSR]": (GwyDict, GwyStr),
        "[MSR:RECORD]": (MsrRecordDict, MsrRecordStr),
        "[LAD:MSR_REF]": (MsrRefDict, MsrRefStr),
        "[LAD:PARA_REF]": (ParaRefDict, ParaRefStr),
        "[EAM:RECORD]": (EamRecordDict, EamRecordStr),
        "[PBV:OBJPATH]": (PbvObjpathDict, PbvObjpathStr),
        "[HW2_BLOB]": (Hw2BlobDict, Hw2BlobStr),
        "[PB:NODE]": (PbNodeDict, PbNodeStr)
        }

    def __getitem__(self, key):
        return self._msr_factories[key]

    def __repr__(self):
        return repr(self._msr_factories)

    def __len__(self):
        return len(self._msr_factories)

    def copy(self):
        return self._msr_factories.copy()

    def keys(self):
        return self._msr_factories.keys()

    def values(self):
        return self._msr_factories.values()


def read_freelance_row(listed_data: str, sep: str = ";") -> tuple:
    """
    read_msr_row Matching instances to the key word are searched for and returned accordingly.

    Args:
        listed_data (str): An exported row of freelance is required. These must contain a key word. Key words are predefined.
        sep (str, optional): Seperator for the string must be set. Defaults to ";".


    Raises:
        KeyError: If the keyword in the string does not match the expected string, the error is returned.

    Returns:
        tuple: a tuple with an instance to convert to a dict and to convert to string
    """
    key_word, *_ = listed_data.split(sep)
    find_msr_factory_tuple = ExportedFreelanceFactories()
    if key_word not in find_msr_factory_tuple.keys():
        raise KeyError(f"unknown keyword in line: {key_word}.")
    (dict_class, string_class) = find_msr_factory_tuple[key_word]
    return (dict_class(), string_class())
