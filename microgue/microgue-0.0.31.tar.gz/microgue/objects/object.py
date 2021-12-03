class Null:
    """
    Null: attribute's value is None
    None: attribute's value is not set
    """
    pass


class Object:
    """
    attributes: defines the attributes of the Object

    protected_attributes: attributes that should not be included when calling Object.serialize()
        Can be included by passing in hide_protected_attributes=False
    """
    attributes = []
    protected_attributes = []

    def __init__(self, attributes={}, raise_errors=True, *args, **kwargs):
        # add all attributes to the object
        for key in self.attributes:
            self.__dict__[key] = None

        # load object with attributes received
        self.deserialize(
            attributes=attributes,
            raise_errors=raise_errors
        )

        super().__init__(*args, **kwargs)

    def __getattribute__(self, key):
        value = super().__getattribute__(key)
        if value is Null:
            return None
        else:
            return value

    def __setattr__(self, key, value):
        if key not in self.attributes:
            raise AttributeError("{} object does not have {} attribute to set".format(self.__class__.__name__, key))
        if value is None:
            self.__dict__[key] = Null
        else:
            self.__dict__[key] = value

    def copy(self):
        return self.__class__(self.serialize(hide_protected_attributes=False))

    def serialize(self, hide_protected_attributes=True):
        attributes = dict()
        for key, value in self.__dict__.items():
            if value is not None:
                if value is Null:
                    attributes[key] = None
                else:
                    attributes[key] = value
        if hide_protected_attributes:
            for key in self.protected_attributes:
                attributes.pop(key, None)

        return attributes

    def deserialize(self, attributes={}, raise_errors=True):
        for key, value in attributes.items():
            try:
                self.__setattr__(key, value)
            except:  # noqa
                if raise_errors:
                    raise

    @classmethod
    def bulk_serialize(cls, objects):
        dicts = []
        for obj in objects:
            dicts.append(obj.serialize())
        return dicts

    @classmethod
    def bulk_deserialize(cls, dicts):
        objects = []
        for dic in dicts:
            objects.append(cls(dic))
        return objects
