from functools import total_ordering

from .jsonable import JsonMixin
from .commentable import CommentMixin


@total_ordering
class Version(JsonMixin, CommentMixin):
    """Version class represents versioning data to track various versions of arbitrary
    instances.

    It maintains 'major', 'minor', 'patch' and 'comment' attributes to keep track
    of changes.
    """

    def __init__(self, major=0, minor=0, patch=0, comment=None, *args, **kwargs):
        super().__init__(comment=comment, *args, **kwargs)
        self.major = major
        self.minor = minor
        self.patch = patch

    def __repr__(self):
        return "{0}(major={1}, minor={2}, patch={3}, comment='{4}')".format(
            self.__class__.__name__,
            self.major,
            self.minor,
            self.patch,
            self.comment if self.comment else None,
        )

    def __eq__(self, o):
        if self is o:
            return True
        return (self.major, self.minor, self.patch, self.comment) == (
            o.major,
            o.minor,
            o.patch,
            o.comment,
        )

    def __le__(self, o):
        return (self.major, self.minor, self.patch) < (o.major, o.minor, o.patch)

    def __hash__(self):
        return hash((self.major, self.minor, self.patch, self.comment))

    def as_tuple(self):
        """Returns the major, minor and patch numeric values as a tuple of length
        3.
        """
        return (self.major, self.minor, self.patch)

    def as_str(self):
        """Returns the major, minor and patch values as string in following format
        major . minor . patch
        """
        return "{0}.{1}.{2}".format(self.major, self.minor, self.patch)

    def from_tuple(self, values):
        """Sets version major, minor and patch values from given tuple of
        length 3.
        """
        self.major, self.minor, self.patch = values

    def increment_major(self, inc=1):
        """Increments major value by the specified increment (defaults to 1)
        """
        self.major += inc

    def increment_minor(self, inc=1):
        """Increments minor value by the specified increment (defaults to 1)
        """
        self.minor += inc

    def increment_patch(self, inc=1):
        """Increments patch value by the specified increment (defaults to 1)
        """
        self.patch += inc


class VersionMixin(object):
    """VersionMixin class adds versioning capability to its subclasses.
    It adds '_version' attribtue of type Version to track various details.
    """

    def __init__(self, major=0, minor=0, patch=0, comment=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._version = Version(major=major, minor=minor, patch=patch, comment=comment)

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, ver):
        self._version = ver
