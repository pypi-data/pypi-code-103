from collections import OrderedDict


class RegisteredType(type):
    """RegisteredType metaclass handles class registry for the class type which uses
    this as its metaclass.
    """

    def __new__(cls, clsname, bases, clsdict):
        new_cls = super().__new__(cls, clsname, bases, clsdict)
        if not hasattr(new_cls, "_registered_types"):
            new_cls._registered_types = OrderedDict()
        new_cls._registered_types[clsname] = new_cls
        return new_cls

    @property
    def registered_types(cls):
        """Returns all the derived classes registered to the class type.
        """
        return cls._registered_types
