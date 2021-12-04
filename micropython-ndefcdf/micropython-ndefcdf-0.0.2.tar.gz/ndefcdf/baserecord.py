# Copyright (c) 2021 Petr Kracik

from ndef.record import Record, GlobalRecord
from io import BytesIO

class CDFBaseRecord(GlobalRecord):
    def __init__(self, value=None):
        self.label = value.split(";")[0] if ";" in value else None
        self.url = value.split(";")[1] if ";" in value else value


    def __str__(self):
        """Return an informal representation suitable for printing."""
        return ("NDEF CDFBaseRecord: '{} (Label: {})'").format(self.url, self.label)
    

    def __repr__(self):
        return self.__str__()


    def _encode_payload(self):
        if self.label is None:
            return self.url.encode()

        return "{}:{}".format(self.label, self.url).encode()


    @classmethod
    def _decode_payload(cls, octets, errors):
        stream = BytesIO(octets)
        data = stream.read()
        return cls(data.decode())
