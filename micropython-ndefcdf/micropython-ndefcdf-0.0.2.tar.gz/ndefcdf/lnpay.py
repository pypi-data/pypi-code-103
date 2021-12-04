# Copyright (c) 2021 Petr Kracik

from ndef.record import Record
from .baserecord import CDFBaseRecord


class CDFLNPay(CDFBaseRecord):
    _type = "cdf/lnp"

    def __str__(self):
        """Return an informal representation suitable for printing."""
        return ("NDEF CDFLNPay: '{} (Label: {})'").format(self.url, self.label)


Record.register_type(CDFLNPay)
