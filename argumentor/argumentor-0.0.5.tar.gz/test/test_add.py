# -*- coding: utf-8 -*-

from argumentor import Arguments, ArgumentValueError, OperationExistsError, OptionExistsError, GroupExistsError, \
    GroupNotExistsError, InvalidOptionError, InvalidOperationError
from nose.tools import raises
import unittest


class TestOperationOnlyNoGroup(unittest.TestCase):

    def test_add_operation_bool_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool),
            None
        )

    @raises(OperationExistsError)
    def test_add_operation_bool_exists(self):
        parser = Arguments()
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool),
            None
        )

    def test_add_operation_int_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("--get", short_operation="-g", value_type=int),
            None
        )

    @raises(OperationExistsError)
    def test_add_operation_int_exists(self):
        parser = Arguments()
        parser.add_operation("--get", short_operation="-g", value_type=int)
        self.assertEqual(
            parser.add_operation("--get", short_operation="-g", value_type=int),
            None
        )

    def test_add_operation_str_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("--print", short_operation="-p", value_type=str),
            None
        )

    @raises(OperationExistsError)
    def test_add_operation_str_exists(self):
        parser = Arguments()
        parser.add_operation("--print", short_operation="-p", value_type=str)
        self.assertEqual(
            parser.add_operation("--print", short_operation="-p", value_type=str),
            None
        )

    @raises(ArgumentValueError)
    def test_add_operation_invalidvalue(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("-h", short_operation="-h", value_type=classmethod),
            None
        )

    @raises(InvalidOperationError)
    def test_add_sameasshort_operation_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("-h", short_operation="-h", value_type=bool),
            None
        )

    def test_add_nodashes_operation_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("help", short_operation="-h", value_type=bool),
            None
        )

    def test_add_nodashesshort_operation_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("help", short_operation="h", value_type=bool),
            None
        )

    @raises(InvalidOperationError)
    def test_add_invalidshort_operation_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("--help", short_operation="-hh", value_type=bool),
            None
        )


class TestOptionOnlyNoGroup(unittest.TestCase):

    def test_add_option_bool_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("--help", short_option="-h", value_type=bool),
            None
        )

    @raises(OptionExistsError)
    def test_add_option_bool_exists(self):
        parser = Arguments()
        parser.add_option("--help", short_option="-h", value_type=bool)
        self.assertEqual(
            parser.add_option("--help", short_option="-h", value_type=bool),
            None
        )

    def test_add_option_int_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("--get", short_option="-g", value_type=int),
            None
        )

    @raises(OptionExistsError)
    def test_add_option_int_exists(self):
        parser = Arguments()
        parser.add_option("--get", short_option="-g", value_type=int)
        self.assertEqual(
            parser.add_option("--get", short_option="-g", value_type=int),
            None
        )

    def test_add_operation_str_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("--print", short_option="-p", value_type=str),
            None
        )

    @raises(OptionExistsError)
    def test_add_option_str_exists(self):
        parser = Arguments()
        parser.add_option("--print", short_option="-p", value_type=str)
        self.assertEqual(
            parser.add_option("--print", short_option="-p", value_type=str),
            None
        )

    @raises(ArgumentValueError)
    def test_add_option_invalidvalue(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("-h", short_option="-h", value_type=classmethod),
            None
        )

    def test_add_operation_list_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("--print", short_option="-p", value_type=list),
            None
        )

    @raises(OptionExistsError)
    def test_add_option_list_exists(self):
        parser = Arguments()
        parser.add_option("--print", short_option="-p", value_type=list)
        self.assertEqual(
            parser.add_option("--print", short_option="-p", value_type=list),
            None
        )

    @raises(InvalidOptionError)
    def test_add_sameasshort_option_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("-h", short_option="-h", value_type=bool),
            None
        )

    @raises(InvalidOptionError)
    def test_add_nodashes_option_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("help", short_option="-h", value_type=bool),
            None
        )

    @raises(InvalidOptionError)
    def test_add_nodashesshort_option_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("--help", short_option="h", value_type=bool),
            None
        )

    @raises(InvalidOptionError)
    def test_add_invalidshort_option_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("--help", short_option="-hh", value_type=bool),
            None
        )


class TestOperationsOptions(unittest.TestCase):

    @raises(OperationExistsError)
    def test_add_operation_sameas_option(self):
        parser = Arguments()
        parser.add_operation("--help", value_type=bool, short_operation="-h")
        self.assertEqual(
            parser.add_option("--help", value_type=bool, short_option="-h"),
            None
        )

    @raises(OperationExistsError)
    def test_add_operation_long_sameas_option_long(self):
        parser = Arguments()
        parser.add_operation("--help", value_type=bool, short_operation="-h")
        self.assertEqual(
            parser.add_option("--help", value_type=bool, short_option="-H"),
            None
        )

    @raises(OperationExistsError)
    def test_add_operation_short_sameas_option_short(self):
        parser = Arguments()
        parser.add_operation("--help", value_type=bool, short_operation="-h")
        self.assertEqual(
            parser.add_option("--hello", value_type=bool, short_option="-h"),
            None
        )


class TestGroupsOnly(unittest.TestCase):

    def test_add_operation_group_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation_group("test"),
            None
        )

    @raises(GroupExistsError)
    def test_add_operation_group_exists(self):
        parser = Arguments()
        parser.add_operation_group("test"),
        self.assertEqual(
            parser.add_operation_group("test"),
            None
        )

    def test_add_option_group_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option_group("test"),
            None
        )

    @raises(GroupExistsError)
    def test_add_option_group_exists(self):
        parser = Arguments()
        parser.add_option_group("test")
        self.assertEqual(
            parser.add_option_group("test"),
            None
        )

    def test_add_operation_group_exists_option_group(self):
        parser = Arguments()
        parser.add_option_group("test")
        self.assertEqual(
            parser.add_operation_group("test"),
            None
        )

    def test_add_option_group_exists_operation_group(self):
        parser = Arguments()
        parser.add_operation_group("test")
        self.assertEqual(
            parser.add_option_group("test"),
            None
        )


class TestOperationsOnlyGroups(unittest.TestCase):

    def test_add_operation_bool_groupexists_noexists(self):
        parser = Arguments()
        parser.add_operation_group("test")
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool, group="test"),
            None
        )

    @raises(GroupNotExistsError)
    def test_add_operation_bool_groupnoexists_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool, group="test"),
            None
        )

    @raises(GroupNotExistsError)
    def test_add_operation_bool_groupoptionexists_noexists(self):
        parser = Arguments()
        parser.add_option_group("test")
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool, group="test"),
            None
        )

    @raises(OperationExistsError)
    def test_add_operation_bool_groupexists_exists_nogroup(self):
        parser = Arguments()
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool, group="test"),
            None
        )


class TestOptionsOnlyGroups(unittest.TestCase):

    def test_add_option_bool_groupexists_noexists(self):
        parser = Arguments()
        parser.add_option_group("test")
        self.assertEqual(
            parser.add_option("--help", short_option="-h", value_type=bool, group="test"),
            None
        )

    @raises(GroupNotExistsError)
    def test_add_option_bool_groupnoexists_noexists(self):
        parser = Arguments()
        self.assertEqual(
            parser.add_option("--help", short_option="-h", value_type=bool, group="test"),
            None
        )

    @raises(GroupNotExistsError)
    def test_add_option_bool_groupoperationexists_noexists(self):
        parser = Arguments()
        parser.add_operation_group("test")
        self.assertEqual(
            parser.add_option("--help", short_option="-h", value_type=bool, group="test"),
            None
        )

    @raises(OptionExistsError)
    def test_add_option_bool_groupexists_exists_nogroup(self):
        parser = Arguments()
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool)
        self.assertEqual(
            parser.add_option("--help", short_option="-h", value_type=bool, group="test"),
            None
        )


class TestOperationsOptionsParams(unittest.TestCase):

    @raises(ArgumentValueError)
    def test_add_operation_defaultvalue_wrongtype_exists(self):
        parser = Arguments(["--help"])
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool, default_value="this_default_text"),
            None
        )

    def test_add_operation_bool_defaultvalue_exists(self):
        parser = Arguments(["--help"])
        self.assertEqual(
            parser.add_operation("--help", short_operation="-h", value_type=bool, default_value=True),
            None
        )


if __name__ == '__main__':
    unittest.main()
