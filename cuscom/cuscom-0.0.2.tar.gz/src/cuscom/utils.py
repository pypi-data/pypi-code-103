from typing import Any, Dict


def flatten_dict(nested_dict: Dict, sep=".") -> Dict[str, Any]:
    def items():
        for key, value in nested_dict.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value).items():
                    yield key + sep + subkey, subvalue
            else:
                yield key, value

    return dict(items())
