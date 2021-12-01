from typing import Dict, Any


# FIXME (prod) this method should not exit - it is standard in python dict
def pop_param_when_available(kwargs: Dict = None, key: Any = None, default_value: Any = None):
    return kwargs.pop(key, default_value)
