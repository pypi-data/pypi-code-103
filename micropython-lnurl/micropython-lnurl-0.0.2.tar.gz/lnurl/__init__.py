from bech32 import bech32_decode, bech32_encode, convertbits


__author__ = "Petr Kracik"
__version__ = "0.0.2"
__license__ = "MIT"


class LNURLException(Exception):
    pass


class LNURL():
    def __init__(self, value=None):
        self._callback = None
        self._url = None
        self._lnurl = None
        if value:
            if value[0:4].lower() == "http":
                self.url = value
            elif value[0:6].lower() == "lnurl1":
                self.lnurl = value
            elif value[0:10].lower() == "lightning:":
                self.lnurl = value[10:]
            else:
                raise ValueError("Unknown URI string")


    def __str__(self):
        """Return an informal representation suitable for printing."""
        return ("{}: '{}' ({})").format(type(self).__name__, self.lnurl, self.url)


    def __repr__(self):
        return self.__str__()


    @property
    def lnurl(self):
        return self._lnurl


    @lnurl.setter
    def lnurl(self, lnurl):
        self._lnurl = lnurl
        parsed = bech32_decode(self._lnurl)[1]
        decoded = convertbits(parsed, 5, 8, False)
        self._url = bytes(decoded).decode()


    @property
    def url(self):
        return self._url


    @url.setter
    def url(self, url):
        self._url = url
        conv = convertbits(url.encode(), 8, 5)
        encoded = bech32_encode("lnurl", conv).upper()
        self._lnurl = encoded


    @classmethod
    def from_url(cls, url):
        print("DEPRECATED: Use constructor instead")
        return cls(url)


    @classmethod
    def from_lnurl(cls, lnurl):
        return cls.from_url(lnurl)
