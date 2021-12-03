from pyrasgo.api.connection import Connection
from pyrasgo.schemas import dataset as schema


class Dataset(Connection):
    """
    Stores a Rasgo Dataset
    """
    def __init__(self, api_object, **kwargs):
        super().__init__(**kwargs)
        self._fields = schema.Dataset(**api_object)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Dataset(id={self.id}, name={self.name})"

    def __getattr__(self, item):
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            self.refresh()
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            raise AttributeError(f"No attribute named {item}")

# --------
# Methods
# --------

    def transform(self, operation: 'Operation') -> None:
        """
        Adds an opertation to the definition of this dataset. These operations 
        can reference other datasets, or previously added operations
        """
        raise NotImplementedError
