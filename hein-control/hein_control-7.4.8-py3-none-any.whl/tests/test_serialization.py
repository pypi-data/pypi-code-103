"""basic tests for serialization of objects"""

import unittest

from hein_control.mixin.serialization import (DumpableState, DumpableList, is_jsonable, make_mapping_serializable,
                                              make_iterable_serializable)

class State(DumpableState):
    val = 1234

    def as_dict(self) -> dict:
        return {'test value': self.val}


class List(DumpableList):
    lst = [1, 2, 3, 4, 5, 6, 'asdf']

    def as_list(self) -> list:
        return self.lst


class TestDumpables(unittest.TestCase):

    def test_state(self):
        """tests DumpableState class"""
        inst = State()
        self.assertTrue(
            is_jsonable(inst.as_dict())
        )

    def test_list(self):
        """tests DumpableList class"""
        inst = List()
        self.assertTrue(
            is_jsonable(inst.as_list())
        )

    def test_casting(self):
        """tests casting function"""
        state_inst = State()
        list_inst = List()
        self.assertTrue(
            is_jsonable(make_iterable_serializable(list_inst))
        )
        self.assertTrue(
            is_jsonable(make_mapping_serializable(val=state_inst))
        )
