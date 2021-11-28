import datetime
from functools import total_ordering

from legos.base.mixins.jsonable import JsonMixin


@total_ordering
class DateTimeData(JsonMixin):
    def __init__(self):
        self._data = str(datetime.datetime.now())

    def __str__(self):
        return str(self._data)

    def __eq__(self, o):
        return self._data == o.data

    def __lt__(self, o):
        return self.dataraw < o.dataraw

    def __hash__(self):
        return hash(self.data)

    @property
    def data(self):
        if not self._data:
            self._data = str(datetime.datetime.now())
        return self._data

    @property
    def dataraw(self):
        return datetime.datetime.fromisoformat(self.data)

    def pretty(self):
        return datetime.datetime.fromisoformat(self._data).ctime()


class TimeStampedObject(object):
    """Mixin which adds serializable timestamp to the subclass.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._timestamp = DateTimeData()

    @property
    def timestamp(self):
        return self._timestamp


__all__ = [DateTimeData.__name__, TimeStampedObject.__name__]
