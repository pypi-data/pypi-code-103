import unittest
from typing import Any

from monomorphic import monomorph


class DataClass:
    def __init__(self, v: Any) -> None:
        self.v = v


class IntWithPrecision(int):
    def __init__(self, _) -> None:
        self.precision = 2

    @property
    def precision(self) -> int:
        return self._precision

    @precision.setter
    def precision(self, v: int) -> None:
        self._precision = v


class FloatWithPrecision(float):
    def __init__(self, _) -> None:
        self.precision = 3

    @property
    def precision(self) -> int:
        return self._precision

    @precision.setter
    def precision(self, v: int) -> None:
        self._precision = v


class MonomorphOptionsTestCase(unittest.TestCase):
    def test_class_adjustment(self):
        """ Test class conversions """
        t = DataClass(DataClass(IntWithPrecision(5)))
        t2 = monomorph(t)
        self.assertTrue(type(t2) is DataClass)
        self.assertTrue(type(t2.v) is DataClass)
        self.assertFalse(t2 is t, "Type changed, class should have been copied")
        self.assertFalse(t2.v is t.v, "Inner type changed, class should have been copied")
        self.assertTrue(type(t2.v.v) is int, "IntWithPrecision should have been converted to int")
        self.assertEqual(t.v.v, 5)
        self.assertEqual(t2.v.v, 5)

    def test_deep_copy(self):
        """ Test deep copy option """
        t = DataClass(DataClass(17))
        t2 = monomorph(t)
        self.assertIs(t2, t, "No change should occur here")
        t2 = monomorph(t, full_copy=True)
        self.assertFalse(t2 is t, "Full copy should force override")

    def test_alternate_list(self):
        """ Test an alternate list conversion """
        t = DataClass([DataClass(FloatWithPrecision(11.1)), DataClass(IntWithPrecision(-117))])
        self.assertTrue(isinstance(t.v[0], DataClass))
        self.assertIs(type(t.v[0].v), FloatWithPrecision)
        self.assertEqual(t.v[0].v, 11.1)
        self.assertIs(type(t.v[1].v), IntWithPrecision)
        self.assertEqual(t.v[1].v, -117)

        t2 = monomorph(t)
        self.assertTrue(isinstance(t2.v[0], DataClass))
        self.assertIs(type(t2.v[0].v), float)
        self.assertEqual(t2.v[0].v, 11.1)
        self.assertIs(type(t2.v[1].v), int)
        self.assertEqual(t2.v[1].v, -117)

        t3 = monomorph(t, convert_types=[int, list])
        self.assertTrue(isinstance(t3.v[0], DataClass))
        self.assertIs(type(t3.v[0].v), FloatWithPrecision)
        self.assertEqual(t2.v[0].v, 11.1)
        self.assertIs(type(t2.v[1].v), int)
        self.assertEqual(t2.v[1].v, -117)

    def test_basic_types(self):
        """ Test the set/list/dict options """
        s = "abc"

        def check_iterable(t):
            self.assertIs(type(t[0]), int)
            self.assertIs(type(t[1]), float)
            self.assertIs(t[2], s)

        # list
        t1 = monomorph([IntWithPrecision(10), FloatWithPrecision(20), s])
        check_iterable(t1)

        # tuple
        t2 = monomorph((IntWithPrecision(10), FloatWithPrecision(20), s))
        check_iterable(t2)

        # set
        t3 = monomorph({IntWithPrecision(10), FloatWithPrecision(20), s})
        self.assertEqual(t3, {10, float(20), s})
        self.assertEqual({type(v) for v in t3}, {int, float, str})

        # dict
        t4 = monomorph({"a": IntWithPrecision(10),
                        "b": FloatWithPrecision(20),
                        "c": s})
        self.assertIs(type(t4["a"]), int)
        self.assertIs(type(t4["b"]), float)
        self.assertIs(t4["c"], s)


if __name__ == '__main__':
    unittest.main()
