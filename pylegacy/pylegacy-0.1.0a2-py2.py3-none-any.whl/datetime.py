"""Legacy :mod:`datetime` module."""
from __future__ import absolute_import

# Add temporary imports.
import sys as __sys

# Import `datetime` members.
from datetime import *
from datetime import __doc__
__all__ = sorted(__k for __k in globals().keys()
                 if not (__k.startswith("__") or __k.endswith("__")))

# Start with backports.
if __sys.version_info[:2] < (3, 2):

    from datetime import datetime
    from datetime import timedelta
    from datetime import tzinfo

    # Backport info:
    # - Python 3.2: first appeareance.
    # pylint: disable=invalid-name,protected-access
    class timezone(tzinfo):
        """Fixed offset from UTC implementation of tzinfo."""

        __slots__ = ("_offset", "_name")

        # Sentinel value to disallow None
        _Omitted = object()
        def __new__(cls, offset, name=_Omitted):
            if not isinstance(offset, timedelta):
                raise TypeError("offset must be a timedelta")
            if name is cls._Omitted:
                if not offset:
                    return cls.utc
                name = None
            elif not isinstance(name, str):
                raise TypeError("name must be a string")
            if not cls._minoffset <= offset <= cls._maxoffset:
                raise ValueError("offset must be a timedelta "
                                 "strictly between -timedelta(hours=24) and "
                                 "timedelta(hours=24).")
            if (offset.microseconds != 0 or offset.seconds % 60 != 0):
                raise ValueError("offset must be a timedelta "
                                 "representing a whole number of minutes")
            return cls._create(offset, name)

        @classmethod
        def _create(cls, offset, name=None):
            self = tzinfo.__new__(cls)
            self._offset = offset
            self._name = name
            return self

        def __getinitargs__(self):
            """pickle support"""
            if self._name is None:
                return (self._offset,)
            return (self._offset, self._name)

        def __eq__(self, other):
            if not isinstance(other, timezone):
                return False
            return self._offset == other._offset

        def __hash__(self):
            return hash(self._offset)

        def __repr__(self):
            """Convert to formal string, for repr().

            >>> tz = timezone.utc
            >>> repr(tz)
            'datetime.timezone.utc'
            >>> tz = timezone(timedelta(hours=-5), 'EST')
            >>> repr(tz)
            "datetime.timezone(datetime.timedelta(-1, 68400), 'EST')"
            """
            if self is self.utc:
                return "datetime.timezone.utc"
            if self._name is None:
                return "%s(%r)" % ("datetime." + self.__class__.__name__,
                                   self._offset)
            return "%s(%r, %r)" % ("datetime." + self.__class__.__name__,
                                   self._offset, self._name)

        def __str__(self):
            return self.tzname(None)

        def utcoffset(self, dt):
            if isinstance(dt, datetime) or dt is None:
                return self._offset
            raise TypeError("utcoffset() argument must be a datetime instance "
                            "or None")

        def tzname(self, dt):
            if isinstance(dt, datetime) or dt is None:
                if self._name is None:
                    return self._name_from_offset(self._offset)
                return self._name
            raise TypeError("tzname() argument must be a datetime instance "
                            "or None")

        def dst(self, dt):
            if isinstance(dt, datetime) or dt is None:
                return None
            raise TypeError("dst() argument must be a datetime instance "
                            "or None")

        def fromutc(self, dt):
            if isinstance(dt, datetime):
                if dt.tzinfo is not self:
                    raise ValueError("fromutc: dt.tzinfo is not self")
                return dt + self._offset
            raise TypeError("fromutc() argument must be a datetime instance"
                            " or None")

        _maxoffset = timedelta(hours=23, minutes=59)
        _minoffset = -_maxoffset

        @staticmethod
        def _name_from_offset(delta):
            if delta < timedelta(0):
                sign = "-"
                delta = -delta
            else:
                sign = "+"
            total = int(delta.days * 86400 + delta.seconds +
                        delta.microseconds * 1E-6)
            hours, minutes = total // 3600, (total % 3600) // 60
            return "UTC{0}{1:02d}:{2:02d}".format(sign, hours, minutes)

    timezone.utc = timezone._create(timedelta(0))
    timezone.min = timezone._create(timezone._minoffset)
    timezone.max = timezone._create(timezone._maxoffset)

    if "timezone" not in __all__:
        __all__.append("timezone")

# Remove temporary imports.
del __sys
