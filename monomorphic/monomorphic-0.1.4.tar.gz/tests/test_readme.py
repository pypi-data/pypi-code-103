import unittest
from typing import Union, Any


def nice_library_function(v: Any) -> str:
    if isinstance(v, str):
        return f"STRING: {v}"
    elif isinstance(v, int):
        return f"INT: {v}"
    elif isinstance(v, dict):
        return str({k: nice_library_function(v2) for k, v2 in v.items()})
    elif isinstance(v, list):
        return str([nice_library_function(v2) for v2 in v])
    elif isinstance(v, set):
        return str({nice_library_function(v2) for v2 in v})
    else:
        raise ValueError(f"I don't understand type {type(v)}")


def brittle_library_function(v: Union[int, str]) -> Union[str, int, dict, list, set]:
    v_type = type(v)

    if v_type is str:
        return f"STRING: {v}"
    elif v_type is int:
        return f"INT: {v}"
    elif isinstance(v, dict):
        return str({k: brittle_library_function(v2) for k, v2 in v.items()})
    elif isinstance(v, list):
        return str([brittle_library_function(v2) for v2 in v])
    elif isinstance(v, set):
        return str({brittle_library_function(v2) for v2 in v})
    else:
        raise ValueError(f"I don't understand type {type(v)}")


class Rope(str):
    """ Subclass of the builtin python str class """
    def __init__(self, v: Any) -> None:
        self._ntwines = 1
        super().__init__()

    @property
    def twines(self) -> int:
        return self._ntwines

    @twines.setter
    def twines(self, v: int) -> None:
        self._ntwines = v


class ReadMeTestCase(unittest.TestCase):
    def test_nice_library_function(self):
        self.assertEqual("STRING: Hi there", nice_library_function("Hi there"))
        self.assertEqual("STRING: 17 feet", nice_library_function(Rope("17 feet")))
        self.assertEqual("['STRING: e1', 'INT: 42', 'STRING: One yard']",
                         nice_library_function(["e1", 42, Rope("One yard")]))

    def test_brittle_function(self):
        self.assertEqual("STRING: Hi there", brittle_library_function("Hi there"))
        with self.assertRaises(ValueError) as e:
            brittle_library_function(Rope("17 feet"))
        self.assertEqual("I don't understand type <class 'test_readme.Rope'>", str(e.exception).replace('tests.', ''))


if __name__ == '__main__':
    unittest.main()
