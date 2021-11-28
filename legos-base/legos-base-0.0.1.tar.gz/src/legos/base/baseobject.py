import os as _os
from collections import OrderedDict
from itertools import chain
from uuid import uuid4

from .baseuser import BaseUser
from .mixins.describable import DescriptionMixin
from .mixins.diskcacheable import DiskCacheable
from .mixins.jsonable import JsonMixin, JsonType
from .mixins.status import (
    ApprovedAsset,
    AssetStatus,
    PublishedAsset,
    ReleasedAsset,
    UnReleasedAsset,
)
from .mixins.timestampable import TimeStampedObject
from .mixins.versionable import Version, VersionMixin


class BaseObject(DescriptionMixin, VersionMixin):
    """BaseObject class is the base of all the object types which will be tracked.
    It provides a base set of attributes which will be required by any object in
    the legos framework.

    Any object which needs to be published, will basically be subclassed from
    PublishableObject class which will add the required disk caching capabilities
    to the subclass.
    """

    #  Removing path from the init arguments since, we have automated path creation
    #  logic. The assets will always be initialized with correct path. However, if
    #  we need to serialize any specific asset to an arbitrary location, we can do
    #  by supplying the path in the    "to_disk"  method.
    def __init__(self, name=None, uid=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._name = name
        self._path = None
        self._uid = uid if uid else uuid4().hex

    def __repr__(self):
        return '{0}(name="{1}", path="{2}", uid="{3}")'.format(
            self.__class__.__name__, self.name, self.path, self.uid
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, objname):
        self._name = objname

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path_str):
        self._path = path_str

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid_str):
        self._uid = uid_str

    @classmethod
    def from_uid(cls, uid_str):
        """Given a uid string value, this method will get the asset which is
        associated with it.
        """
        raise NotImplementedError()

    @property
    def version(self):
        """Returns the version instance which stores the version data for the specific
        object.
        """
        return self._version


class PublishableObject(BaseObject, DiskCacheable, TimeStampedObject):
    """A PublishableObject can be cached to disk.

    However,it should be noted that on its own, PublishableObject class can not be
    cached to disk since it also requires encode/decode methods which are supplied by
    the JsonMixin.

    All the Asset and Package classes are subclassed from PublishableObject and also
    JsonMixin which enables the instances to serialize the data into json and write the
    data to disk.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #  Kind tag is houdini pdg styled tagging mechanism primarily for houdini
        # integration. However, these can be leveraged into pipeline tooling too.
        self.kindtag = ""
        self._status = UnReleasedAsset()
        self._user = None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if isinstance(value, AssetStatus):
            self._status = value
            return
        raise TypeError(
            "status property expects a value of type '{0}', got '{1}' instead.".format(
                AssetStatus, type(value)
            )
        )

    @property
    def is_released(self):
        return isinstance(self._status, ReleasedAsset)

    @property
    def is_published(self):
        """Returns whether a PublishableObject or its subclass's instance is publised
        or not.
        """
        return isinstance(self._status, PublishedAsset)

    def publish(self, *args, **kwargs):
        """Publishes a PublishableObject or its subclass's instance so its available to
        other departments.
        """
        raise NotImplementedError()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, usr):
        """Sets the specified usr value as the User associated with the publishable object.
        """
        if isinstance(usr, BaseUser):
            self._user = usr
            return
        raise TypeError(
            f"User property expects a value of type {BaseUser.__qualname__}, got {type(usr)} instead."
        )


class PackedObjectType(JsonType):
    """PackedObjectType metaclass is responsible for defining creation all the
    Packed Object classes. It also handles asset type registration mechanisms
    by auto registering any of the classes derived from Asset classes.
    """

    def __new__(cls, clsname, bases, clsdict):
        ncls = super().__new__(cls, clsname, bases, clsdict)
        if not hasattr(ncls, "_packed_object_types"):
            ncls._packed_object_types = OrderedDict()
        ncls._packed_object_types[clsname] = ncls
        return ncls

    @property
    def packed_object_types(cls):
        """Returns all the Packed Object types registered.
        """
        return cls._packed_object_types


class PackedObject(JsonMixin, metaclass=PackedObjectType):
    """PackedObject class represents a deferred loaded (or a proxy) object
    which only tracks the bare minimum information about the object needed to load the
    object in memory.

    This is the base class for all the PackedAsset and PackedPackage classes.

    It provides method 'unpack' which can be used to access the object data
    serialized on disk and return a complete asset.

    The subclass must define the 'object_attributes' class attribute to define
    which attributes the packed object will expose on the packed objects.
    """

    #  Lets define the attributes and their default value in this dict.
    #  This dict is used to initialize the attributes and also copy the attributes
    # from the asset.

    # This list of attributes will be common for all implementations.
    _base_object_attributes = {"_name", "_path", "_uid"}

    # This list must be set when subclassing if there are attributes which need
    # to be exposed to the Packed object
    object_attributes = {}

    def __init__(self, name=None, path=None, uid=None):
        input_vals = {"_name": name, "_path": path, "_uid": uid}
        init_vals = {k: None for k in self.__class__.object_attributes}
        init_vals.update(input_vals)
        for attr, value in init_vals.items():
            setattr(self, attr, value)
        #  Type of Object which is packed (either an Asset or a Package).
        self.type = None
        self._version = None

    def _init_from_object(self, obj):
        for attr_name in chain(self._base_object_attributes, self.object_attributes):
            val = getattr(obj, attr_name)
            setattr(self, attr_name, val)
        self.version = obj.version
        self.type = type(obj).__name__

    def __eq__(self, o):
        if self is o:
            return True
        return (
            self._name == o._name
            and self._path == o._path
            and self._uid == o._uid
            and self.version == o.version
        )

    def __ne__(self, o):
        return not self == o

    def __hash__(self):
        # NOTE:
        # Make sure the tuple entries for hashing is same (including the order inside tuple)
        # as that of Object.
        # This enables PackedObject and respective Object instances to be used in a set
        # and remove any duplicate instances.
        raise NotImplementedError()

    def __repr__(self):
        return '{0} <type: {1}, name: "{2}", path: "{3}", uid: "{4}">'.format(
            self.__class__.__name__, self.type, self.name, self.path, self.uid
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if isinstance(value, (Version, type(None))):
            self._version = value
            return
        raise TypeError(
            f"arg 'value' expected a value of type {Version}, got {type(value)} instead."
        )

    @property
    def is_valid(self):
        """Returns True if the PackedAsset represents an Asset which is cached on
        disk and False otherwise.
        """
        return _os.path.isfile(self._path)

    def unpack(self):
        """If the object represented by the PackedObject instance is found on disk,
        returns an Asset instance using the data on disk.
        Else returns self ie. a PackedAsset if the asset is not found on disk.
        """
        raise NotImplementedError()

    @classmethod
    def from_object(cls, obj):
        """Creates a PackedObject instance from a specified legos object.
        Provides a default implementation.
        """
        res = cls()
        res._init_from_object(obj)
        return res

    @classmethod
    def from_disk(cls, apath):
        """Creates a PackedObject instance by loading the data from disk.
        """
        raise NotImplementedError()

    def pack(self):
        """If pack is called on self, return self.
        """
        # This is required since PackedContents uses this functionality to pack
        # objects while setting and unpack while fetching. This call to pack and
        # unpack is delegated to the object instances themselves to better resolve
        # the return type (Whether the result is an Asset, PackedAsset, Package,
        # or PackedPackage)
        return self


class PackedContents(object):
    """Descriptor class used to manage packing and unpacking of Assets while adding
    to a package.

    An asset class will serialize contained Asset instances as PackedAsset instances which is
    a light weight asset representation.

    This is a slightly different implementation than the PackedContents in the Package module.
    (Since assets can only contain other assets, we dont have to factor in Package instances)
    """

    def __init__(self, fname):
        self.name = fname

    def __get__(self, instance, cls):
        # When accessing the attribute, unpack all the PackedAsset instances
        #  If a Package instance is encountered, it is passed through untouched.
        if instance is None:
            return self
        packed_objs = [
            pkd_asset.unpack()
            for pkd_asset in instance.__dict__[self.name]
            if isinstance(pkd_asset, PackedObject)
        ]
        return [i for i in packed_objs]

    def __set__(self, instance, value):
        # When a collection of assets and/or packages is passed, create PackedAsset
        # PackedPackage instances per object type respectively.
        packed_objs = list(
            {
                i.pack()
                for i in value
                if isinstance(i, (PublishableObject, PackedObject))
            }
        )
        packed_objs.sort(key=lambda an_obj: (an_obj.__class__.__name__, an_obj.name))
        instance.__dict__[self.name] = tuple(packed_objs)


__all__ = [
    BaseObject.__name__,
    PublishableObject.__name__,
    PackedObject.__name__,
    PackedContents.__name__,
]
