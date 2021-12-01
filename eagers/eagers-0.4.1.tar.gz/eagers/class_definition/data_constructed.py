"""Defines class DataConstructed, which provides a versatile constructor
method: from_data().

Classes:
DataConstructed
"""



class DataConstructed:
    @classmethod
    def from_data(cls, data, as_list=False):
        """Returns an instance from a given instance, dict, str, list,
        or NoneType. If optional argument as_list is specified as True,
        the returned value will be a list of class instances or an empty
        list in the case of a NoneType.
        """
        if isinstance(data, cls):
            instance = data
        elif isinstance(data, dict):
            # Handle special field _type if present.
            try:
                subcls_name = data.pop('_type')
            except KeyError:
                subcls_name = None
            subcls = (
                cls if subcls_name is None
                else cls._class_from_name(subcls_name)
            )
            return subcls(**data)
        elif isinstance(data, str):
                instance = cls.from_file(data)
        elif isinstance(data, list):
            return [cls.from_data(x) for x in data]
        elif data is None:
            if as_list:
                return []
            else:
                return cls()
        else:
            raise TypeError(f"Unexpected type {type(data)!r}")
        # Ensure return type of list if that was specified.
        if as_list:
            return [instance]
        return instance
