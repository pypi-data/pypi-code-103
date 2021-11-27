# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_flatten.ipynb (unless otherwise specified).

__all__ = ['Flatten']

# Cell

from typing import List, Callable, Any, Dict
class Flatten:
    """
    Flatten a tree structure dictionary
    """
    def __init__(
        self, data,
        key_callback: Callable = None,
        key_connection: str = "_",
        ):
        self.data = data
        self.key_callback = key_callback
        self.key_connection = key_connection

    def flattening(
        self, data,
        result=None,
        upper_key=""
        ) -> Dict[str, str]:
        """
        Recursive flatten function
        """
        if result is None:
            result = {}
        for key, value in data.items():
            if self.key_callback is not None:
                key = self.key_callback(key)
            if isinstance(value, dict):
                self.flattening(value, result,
                upper_key=f"{key}{self.key_connection}")
            else:
                result[f"{upper_key}{key}"] = value
        return result

    def __call__(self) -> Dict[str, str]:
        return self.flattening(self.data)

