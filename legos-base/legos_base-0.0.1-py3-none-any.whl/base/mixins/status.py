from collections import OrderedDict

from .jsonable import JsonType, JsonMixin


class StatusType(JsonType):
    def __new__(cls, clsname, bases, clsdict):
        ncls = super().__new__(cls, clsname, bases, clsdict)
        if not hasattr(ncls, "_status_types"):
            ncls._status_types = OrderedDict()
        ncls._status_types[clsname] = ncls
        return ncls

    @property
    def status_types(cls):
        return cls._status_types

    @property
    def value(cls):
        """Returns the '_value' string of the status class.
        """
        return cls._value

    @property
    def color(cls):
        """Returns the '_color' tuple of the status class which can be used to
        color the display or log data specific to the statuses.
        """
        return cls._value


class Status(JsonMixin, metaclass=StatusType):
    _value = None
    _color = (0, 0, 0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "{0} <{1}>".format(self.__class__.__name__, self._value)

    @property
    def value(self):
        return self._value

    @property
    def color(self):
        return self._color


class TaskStatus(JsonMixin, metaclass=StatusType):
    _value = None
    _color = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "{0} <{1}>".format(self.__class__.__name__, self._value)

    @property
    def value(self):
        return self._value

    @property
    def color(self):
        return self._color


class NotStartedTask(TaskStatus):
    """Task has not been assigned and started yet.
    """

    _value = "NOTSTARTED"
    _color = (232, 232, 232)


class InProgressTask(TaskStatus):
    """Task has been assigned and is in progress.
    """

    _value = "INPROGRESS"
    _color = (254, 244, 69)


class ApprovedTask(TaskStatus):
    """Task has been approved but has not marked finished yet.
    """

    _value = "APPROVED"
    _color = (0, 255, 8)


class FinishedTask(TaskStatus):
    """Task has been approved and is now finished/delivered.
    """

    _value = "FINISHED"
    _color = (75, 168, 2)


class BlockerTask(TaskStatus):
    """Task is blocked due to unfinished dependencies or any technical issues.
    """

    _value = "BLOCKER"
    _color = (255, 0, 0)


class OmitTask(TaskStatus):
    """Task has been omitted and is no longer required. Stop all work immediately.
    """

    _value = "OMIT"
    _color = (128, 128, 128)


class AssetStatus(JsonMixin, metaclass=StatusType):
    _value = None
    _color = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return "{0} <{1}>".format(self.__class__.__name__, self._value)

    @property
    def value(self):
        return self._value

    @property
    def color(self):
        return self._color


class ApprovedAsset(AssetStatus):
    """Assets/Packages which have been approved.
    """

    _value = "APPROVED"
    _color = (0, 200, 0)


class CommitedAsset(AssetStatus):
    """Assets/Packages which have been committed to the database.
    """

    _value = "COMMITTED"
    _color = (0, 200, 0)


class DeclinedAsset(AssetStatus):
    """Assets/Packages which have been declined.
    """

    _value = "DECLINED"
    _color = (100, 0, 0)


class ReleasedAsset(AssetStatus):
    """Assets/Packages which have been released or commited to disk.
    """

    _value = "RELEASED"
    _color = (255, 255, 0)


class UnReleasedAsset(AssetStatus):
    """Assets/Packages which have not been released/cached to disk.
    This is the default status any Asset/Package are set to.
    """

    _value = "UNRELEASED"
    _color = (255, 200, 0)


class PublishedAsset(AssetStatus):
    """Assets/Packages which are published for other departments to be used.
    Any item which has this status, must mean its also been approved.
    """

    _value = "PUBLISHED"
    _color = (0, 255, 0)


__all__ = [
    StatusType.__name__,
    Status.__name__,
    AssetStatus.__name__,
    TaskStatus.__name__,
    ApprovedTask.__name__,
    FinishedTask.__name__,
    InProgressTask.__name__,
    NotStartedTask.__name__,
    OmitTask.__name__,
    BlockerTask.__name__,
    ApprovedAsset.__name__,
    DeclinedAsset.__name__,
    PublishedAsset.__name__,
    ReleasedAsset.__name__,
    UnReleasedAsset.__name__,
]
