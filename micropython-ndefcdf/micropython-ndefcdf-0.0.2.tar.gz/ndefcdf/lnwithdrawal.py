# Copyright (c) 2021 Petr Kracik

from ndef.record import Record
from .baserecord import CDFBaseRecord


class CDFLNWithdrawal(CDFBaseRecord):
    _type = 'cdf/lnw'

    def __str__(self):
        """Return an informal representation suitable for printing."""
        return ("NDEF CDFLNWithdrawal: '{} (Label: {})'").format(self.url, self.label)


Record.register_type(CDFLNWithdrawal)
