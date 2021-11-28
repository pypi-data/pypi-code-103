from enum import Enum


class BlockerType(Enum):
    ACTIVATOR = 0
    FX_DEVICE = 1
    PDC_PHASE = 2
    RESERVED_TYPE = 3
    PROCESSOR = 4
    OTHER = 5
    PEP_PRE_VETO = 6
    SOC_SUBSYSTEM = 7
