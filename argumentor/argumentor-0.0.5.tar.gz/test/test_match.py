# -*- coding: utf-8 -*-

from argumentor import Arguments
from nose.tools import raises
import unittest


class TestOperationOnlyNoGroup(unittest.TestCase):
    """
    Test to match all kinds of situation with only one operation and no groups
    """

    def test_match_operation_long_bool_exists(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_short_bool_exists(self):
        parser = Arguments(["-h"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_long_str_exists(self):
        parser = Arguments(["--print", "string"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            "string"
        )

    def test_match_operation_short_str_exists(self):
        parser = Arguments(["-p", "string"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            "string"
        )

    def test_match_operation_long_int_exists(self):
        parser = Arguments(["--get", "1312"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--get"],
            1312
        )

    def test_match_operation_short_int_exists(self):
        parser = Arguments(["-g", "1312"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--get"],
            1312
        )

    def test_match_operation_long_list_exists(self):
        parser = Arguments(["--print", "a", "list"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            ["a", "list"]
        )

    def test_match_operation_short_list_exists(self):
        parser = Arguments(["-p", "a", "list"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            ["a", "list"]
        )

    @raises(SystemExit)
    def test_match_operation_long_noexists(self):
        parser = Arguments(["--acab"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_noexists(self):
        parser = Arguments(["-a"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_nooperation(self):
        parser = Arguments(["this", "is", "a", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(KeyError)
    def test_match_operation_getanother(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--version"],
            None
        )

    @raises(KeyError)
    def test_match_operation_long_getshort(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["-h"],
            None
        )

    @raises(KeyError)
    def test_match_operation_short_getshort(self):
        parser = Arguments(["-h"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["-h"],
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_int_novalue(self):
        parser = Arguments(["--get"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_int_novalue(self):
        parser = Arguments(["-g"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_int_wrongvalue(self):
        parser = Arguments(["--get", "string"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_int_wrongvalue(self):
        parser = Arguments(["-g", "string"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_int_overvalue(self):
        parser = Arguments(["--get", "4", "5"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_int_overvalue(self):
        parser = Arguments(["-g", "4", "5"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_str_novalue(self):
        parser = Arguments(["--print"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_str_novalue(self):
        parser = Arguments(["-p"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_str_overvalue(self):
        parser = Arguments(["--print", "this", "should", "fail"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_str_overvalue(self):
        parser = Arguments(["-p", "this", "should", "fail"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_list_novalue(self):
        parser = Arguments(["--print"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_list_novalue(self):
        parser = Arguments(["-p"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        self.assertEqual(
            parser.parse(),
            None
        )


class TestOptionOnlyNoGroup(unittest.TestCase):
    """
    Test to match all kinds of situation with only one option and no groups
    """

    @raises(SystemExit)
    def test_match_option_nooperation_fail(self):
        parser = Arguments(["--help"])
        parser.add_option("--help", short_option="-h", value_type=bool)
        self.assertEqual(
            parser.parse(),
            None
        )

    def test_match_option_long_bool_exists(self):
        parser = Arguments(["--help"], one_operation_required=False)
        parser.add_option("--help", short_option="-h", value_type=bool)
        options = parser.parse()[1]
        self.assertEqual(
            options["--help"],
            True
        )

    def test_match_option_short_bool_exists(self):
        parser = Arguments(["-h"], one_operation_required=False)
        parser.add_option("--help", short_option="-h", value_type=bool)
        options = parser.parse()[1]
        self.assertEqual(
            options["--help"],
            True
        )

    def test_match_option_long_str_exists(self):
        parser = Arguments(["--print", "string"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=str)
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            "string"
        )

    def test_match_option_short_str_exists(self):
        parser = Arguments(["-p", "string"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=str)
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            "string"
        )

    def test_match_option_long_int_exists(self):
        parser = Arguments(["--get", "1312"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        options = parser.parse()[1]
        self.assertEqual(
            options["--get"],
            1312
        )

    def test_match_option_short_int_exists(self):
        parser = Arguments(["-g", "1312"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        options = parser.parse()[1]
        self.assertEqual(
            options["--get"],
            1312
        )

    def test_match_option_long_list_exists(self):
        parser = Arguments(["--print", "a", "list"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=list)
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            ["a", "list"]
        )

    def test_match_option_short_list_exists(self):
        parser = Arguments(["-p", "a", "list"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=list)
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            ["a", "list"]
        )

    @raises(SystemExit)
    def test_match_option_long_noexists(self):
        parser = Arguments(["--acab"], one_operation_required=False)
        parser.add_option("--help", short_option="-h", value_type=bool)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_noexists(self):
        parser = Arguments(["-a"], one_operation_required=False)
        parser.add_option("--help", short_option="-h", value_type=bool)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(KeyError)
    def test_match_option_getanother(self):
        parser = Arguments(["--help"], one_operation_required=False)
        parser.add_option("--help", short_option="-h", value_type=bool)
        options = parser.parse()[0]
        self.assertEqual(
            options["--version"],
            None
        )

    @raises(KeyError)
    def test_match_option_long_getshort(self):
        parser = Arguments(["--help"], one_operation_required=False)
        parser.add_option("--help", short_option="-h", value_type=bool)
        options = parser.parse()[1]
        self.assertEqual(
            options["-h"],
            None
        )

    @raises(KeyError)
    def test_match_option_short_getshort(self):
        parser = Arguments(["-h"], one_operation_required=False)
        parser.add_option("--help", short_option="-h", value_type=bool)
        options = parser.parse()[1]
        self.assertEqual(
            options["-h"],
            None
        )

    @raises(SystemExit)
    def test_match_option_long_int_novalue(self):
        parser = Arguments(["--get"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_int_novalue(self):
        parser = Arguments(["-g"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_int_wrongvalue(self):
        parser = Arguments(["--get", "string"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_int_wrongvalue(self):
        parser = Arguments(["-g", "string"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_int_overvalue(self):
        parser = Arguments(["--get", "4", "5"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_int_overvalue(self):
        parser = Arguments(["-g", "4", "5"], one_operation_required=False)
        parser.add_option("--get", short_option="-g", value_type=int)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_str_novalue(self):
        parser = Arguments(["--print"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_str_novalue(self):
        parser = Arguments(["-p"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_str_overvalue(self):
        parser = Arguments(["--print", "this", "should", "fail"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_str_overvalue(self):
        parser = Arguments(["-p", "this", "should", "fail"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=str)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_list_novalue(self):
        parser = Arguments(["--print"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=list)
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_list_novalue(self):
        parser = Arguments(["-p"], one_operation_required=False)
        parser.add_option("--print", short_option="-p", value_type=list)
        self.assertEqual(
            parser.parse(),
            None
        )


class TestOperationOnlyGroup(unittest.TestCase):
    """
    Test to match all kinds of situation with only one operation and an unique group
    """

    def test_match_operation_long_bool_exists(self):
        parser = Arguments(["--help"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_short_bool_exists(self):
        parser = Arguments(["-h"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_long_str_exists(self):
        parser = Arguments(["--print", "string"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=str, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            "string"
        )

    def test_match_operation_short_str_exists(self):
        parser = Arguments(["-p", "string"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=str, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            "string"
        )

    def test_match_operation_long_int_exists(self):
        parser = Arguments(["--get", "1312"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--get"],
            1312
        )

    def test_match_operation_short_int_exists(self):
        parser = Arguments(["-g", "1312"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--get"],
            1312
        )

    def test_match_operation_long_list_exists(self):
        parser = Arguments(["--print", "a", "list"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=list, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            ["a", "list"]
        )

    def test_match_operation_short_list_exists(self):
        parser = Arguments(["-p", "a", "list"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=list, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            ["a", "list"]
        )

    @raises(SystemExit)
    def test_match_operation_long_noexists(self):
        parser = Arguments(["--acab"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_noexists(self):
        parser = Arguments(["-a"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_nooperation(self):
        parser = Arguments(["this", "is", "a", "test"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(KeyError)
    def test_match_operation_getanother(self):
        parser = Arguments(["--help"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--version"],
            None
        )

    @raises(KeyError)
    def test_match_operation_long_getshort(self):
        parser = Arguments(["--help"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["-h"],
            None
        )

    @raises(KeyError)
    def test_match_operation_short_getshort(self):
        parser = Arguments(["-h"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["-h"],
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_int_novalue(self):
        parser = Arguments(["--get"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_int_novalue(self):
        parser = Arguments(["-g"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_int_wrongvalue(self):
        parser = Arguments(["--get", "string"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_int_wrongvalue(self):
        parser = Arguments(["-g", "string"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_int_overvalue(self):
        parser = Arguments(["--get", "4", "5"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_int_overvalue(self):
        parser = Arguments(["-g", "4", "5"])
        parser.add_operation_group("test")
        parser.add_operation("--get", short_operation="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_str_novalue(self):
        parser = Arguments(["--print"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_str_novalue(self):
        parser = Arguments(["-p"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_str_overvalue(self):
        parser = Arguments(["--print", "this", "should", "fail"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_str_overvalue(self):
        parser = Arguments(["-p", "this", "should", "fail"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_list_novalue(self):
        parser = Arguments(["--print"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=list, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_list_novalue(self):
        parser = Arguments(["-p"])
        parser.add_operation_group("test")
        parser.add_operation("--print", short_operation="-p", value_type=list, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )


class TestOptionOnlyGroup(unittest.TestCase):
    """
    Test to match all kinds of situation with only one option and one unique group
    """

    @raises(SystemExit)
    def test_match_option_nooperation_fail(self):
        parser = Arguments(["--help"])
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    def test_match_option_long_bool_exists(self):
        parser = Arguments(["--help"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--help"],
            True
        )

    def test_match_option_short_bool_exists(self):
        parser = Arguments(["-h"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--help"],
            True
        )

    def test_match_option_long_str_exists(self):
        parser = Arguments(["--print", "string"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=str, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            "string"
        )

    def test_match_option_short_str_exists(self):
        parser = Arguments(["-p", "string"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=str, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            "string"
        )

    def test_match_option_long_int_exists(self):
        parser = Arguments(["--get", "1312"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--get"],
            1312
        )

    def test_match_option_short_int_exists(self):
        parser = Arguments(["-g", "1312"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--get"],
            1312
        )

    def test_match_option_long_list_exists(self):
        parser = Arguments(["--print", "a", "list"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=list, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            ["a", "list"]
        )

    def test_match_option_short_list_exists(self):
        parser = Arguments(["-p", "a", "list"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=list, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["--print"],
            ["a", "list"]
        )

    @raises(SystemExit)
    def test_match_option_long_noexists(self):
        parser = Arguments(["--acab"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_noexists(self):
        parser = Arguments(["-a"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(KeyError)
    def test_match_option_getanother(self):
        parser = Arguments(["--help"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        options = parser.parse()[0]
        self.assertEqual(
            options["--version"],
            None
        )

    @raises(KeyError)
    def test_match_option_long_getshort(self):
        parser = Arguments(["--help"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["-h"],
            None
        )

    @raises(KeyError)
    def test_match_option_short_getshort(self):
        parser = Arguments(["-h"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--help", short_option="-h", value_type=bool, group="test")
        options = parser.parse()[1]
        self.assertEqual(
            options["-h"],
            None
        )

    @raises(SystemExit)
    def test_match_option_long_int_novalue(self):
        parser = Arguments(["--get"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_int_novalue(self):
        parser = Arguments(["-g"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_int_wrongvalue(self):
        parser = Arguments(["--get", "string"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_int_wrongvalue(self):
        parser = Arguments(["-g", "string"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_int_overvalue(self):
        parser = Arguments(["--get", "4", "5"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_int_overvalue(self):
        parser = Arguments(["-g", "4", "5"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--get", short_option="-g", value_type=int, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_str_novalue(self):
        parser = Arguments(["--print"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_short_str_novalue(self):
        parser = Arguments(["-p"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_option_long_str_overvalue(self):
        parser = Arguments(["--print", "this", "should", "fail"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_str_overvalue(self):
        parser = Arguments(["-p", "this", "should", "fail"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=str, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_long_list_novalue(self):
        parser = Arguments(["--print"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=list, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )

    @raises(SystemExit)
    def test_match_operation_short_list_novalue(self):
        parser = Arguments(["-p"], one_operation_required=False)
        parser.add_option_group("test")
        parser.add_option("--print", short_option="-p", value_type=list, group="test")
        self.assertEqual(
            parser.parse(),
            None
        )


class TestOperationOptionNoGroup(unittest.TestCase):
    """
    Test to match all kinds of situation with only one operation and no groups
    """

    # bool + bool

    def test_match_operation_long_bool_exists_option_long_bool_exists(self):
        parser = Arguments(["--help", "--force"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--force"]),
            (True, True)
        )

    def test_match_operation_long_bool_exists_option_short_bool_exists(self):
        parser = Arguments(["--help", "-f"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--force"]),
            (True, True)
        )

    def test_match_operation_short_bool_exists_option_short_bool_exists(self):
        parser = Arguments(["-h", "-f"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--force"]),
            (True, True)
        )

    def test_match_operation_short_bool_exists_option_long_bool_exists(self):
        parser = Arguments(["-h", "--force"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--force"]),
            (True, True)
        )

    # bool + str

    def test_match_operation_long_bool_exists_option_long_str_exists(self):
        parser = Arguments(["--help", "--message", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--message"]),
            (True, "test")
        )

    def test_match_operation_long_bool_exists_option_short_str_exists(self):
        parser = Arguments(["--help", "-m", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--message"]),
            (True, "test")
        )

    def test_match_operation_short_bool_exists_option_short_str_exists(self):
        parser = Arguments(["-h", "-m", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--message"]),
            (True, "test")
        )

    def test_match_operation_short_bool_exists_option_long_str_exists(self):
        parser = Arguments(["-h", "--message", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--message"]),
            (True, "test")
        )

    # bool + int

    def test_match_operation_long_bool_exists_option_long_int_exists(self):
        parser = Arguments(["--help", "--level", "1312"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 1312)
        )

    def test_match_operation_long_bool_exists_option_short_int_exists(self):
        parser = Arguments(["--help", "-l", "1312"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 1312)
        )

    def test_match_operation_short_bool_exists_option_short_int_exists(self):
        parser = Arguments(["-h", "-l", "1312"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 1312)
        )

    def test_match_operation_short_bool_exists_option_long_int_exists(self):
        parser = Arguments(["-h", "--level", "1312"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 1312)
        )

    # bool + list

    def test_match_operation_long_bool_exists_option_long_list_exists(self):
        parser = Arguments(["--help", "--args", "this", "is", "a", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--args"]),
            (True, ["this", "is", "a", "test"])
        )

    def test_match_operation_long_bool_exists_option_short_list_exists(self):
        parser = Arguments(["--help", "-a", "this", "is", "a", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--args"]),
            (True, ["this", "is", "a", "test"])
        )

    def test_match_operation_short_bool_exists_option_short_list_exists(self):
        parser = Arguments(["-h", "-a", "this", "is", "a", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--args"]),
            (True, ["this", "is", "a", "test"])
        )

    def test_match_operation_short_bool_exists_option_long_list_exists(self):
        parser = Arguments(["-h", "--args", "this", "is", "a", "test"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--args"]),
            (True, ["this", "is", "a", "test"])
        )

    # str + bool

    def test_match_operation_long_str_exists_order_option_long_bool_exists(self):
        parser = Arguments(["--print", "test", "--force"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    def test_match_operation_long_str_exists_noorder_option_long_bool_exists(self):
        parser = Arguments(["--print", "--force", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    def test_match_operation_long_str_exists_order_option_short_bool_exists(self):
        parser = Arguments(["--print", "test", "-f"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    def test_match_operation_long_str_exists_noorder_option_short_bool_exists(self):
        parser = Arguments(["--print", "-f", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    def test_match_operation_short_str_exists_order_option_short_bool_exists(self):
        parser = Arguments(["-p", "test", "-f"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    def test_match_operation_short_str_exists_noorder_option_short_bool_exists(self):
        parser = Arguments(["-p", "-f", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    def test_match_operation_short_str_exists_order_option_long_bool_exists(self):
        parser = Arguments(["-p", "test", "--force"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    def test_match_operation_short_str_exists_noorder_option_long_bool_exists(self):
        parser = Arguments(["-p", "--force", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            ("test", True)
        )

    # str + str

    def test_match_operation_long_str_exists_order_option_long_str_exists(self):
        parser = Arguments(["--print", "test", "--message", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    def test_match_operation_long_str_exists_noorder_option_long_str_exists(self):
        parser = Arguments(["--print", "--message", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    def test_match_operation_long_str_exists_order_option_short_str_exists(self):
        parser = Arguments(["--print", "test", "-m", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    def test_match_operation_long_str_exists_noorder_option_short_str_exists(self):
        parser = Arguments(["--print", "-m", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    def test_match_operation_short_str_exists_order_option_short_str_exists(self):
        parser = Arguments(["-p", "test", "-m", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    def test_match_operation_short_str_exists_noorder_option_short_str_exists(self):
        parser = Arguments(["-p", "-m", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    def test_match_operation_short_str_exists_order_option_long_str_exists(self):
        parser = Arguments(["-p", "test", "--message", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    def test_match_operation_short_str_exists_noorder_option_long_str_exists(self):
        parser = Arguments(["-p", "--message", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            ("test", "test1")
        )

    # str + int

    def test_match_operation_long_str_exists_order_option_long_int_exists(self):
        parser = Arguments(["--print", "test", "--level", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    def test_match_operation_long_str_exists_noorder_option_long_int_exists(self):
        parser = Arguments(["--print", "--level", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    def test_match_operation_long_str_exists_order_option_short_int_exists(self):
        parser = Arguments(["--print", "test", "-l", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    def test_match_operation_long_str_exists_noorder_option_short_int_exists(self):
        parser = Arguments(["--print", "-l", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    def test_match_operation_short_str_exists_order_option_short_int_exists(self):
        parser = Arguments(["-p", "test", "-l", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    def test_match_operation_short_str_exists_noorder_option_short_int_exists(self):
        parser = Arguments(["-p", "-l", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    def test_match_operation_short_str_exists_order_option_long_int_exists(self):
        parser = Arguments(["-p", "test", "--level", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    def test_match_operation_short_str_exists_noorder_option_long_int_exists(self):
        parser = Arguments(["-p", "--level", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            ("test", 1312)
        )

    # str + list

    def test_match_operation_long_str_exists_order_option_long_list_exists(self):
        parser = Arguments(["--print", "test", "--args", "this", "is", "a", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_long_str_exists_noorder_option_long_list_exists(self):
        parser = Arguments(["--print", "--args", "this", "is", "a", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    def test_match_operation_long_str_exists_order_option_short_list_exists(self):
        parser = Arguments(["--print", "test", "-a", "this", "is", "a", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_long_str_exists_noorder_option_short_list_exists(self):
        parser = Arguments(["--print", "-a", "this", "is", "a", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    def test_match_operation_short_str_exists_order_option_short_list_exists(self):
        parser = Arguments(["-p", "test", "-a", "this", "is", "a", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_short_str_exists_noorder_option_short_list_exists(self):
        parser = Arguments(["-p", "-a", "this", "is", "a", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    def test_match_operation_short_str_exists_order_option_long_list_exists(self):
        parser = Arguments(["-p", "test", "--args", "this", "is", "a", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_short_str_exists_noorder_option_long_list_exists(self):
        parser = Arguments(["-p", "--args", "this", "is", "a", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=str)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--args"]),
            ("test", ["this", "is", "a", "test1"])
        )

    # int + bool

    def test_match_operation_long_int_exists_order_option_long_bool_exists(self):
        parser = Arguments(["--get", "13", "--force"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    def test_match_operation_long_int_exists_noorder_option_long_bool_exists(self):
        parser = Arguments(["--get", "--force", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    def test_match_operation_long_int_exists_order_option_short_bool_exists(self):
        parser = Arguments(["--get", "13", "-f"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    def test_match_operation_long_int_exists_noorder_option_short_bool_exists(self):
        parser = Arguments(["--get", "-f", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    def test_match_operation_short_int_exists_order_option_short_bool_exists(self):
        parser = Arguments(["-g", "13", "-f"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    def test_match_operation_short_int_exists_noorder_option_short_bool_exists(self):
        parser = Arguments(["-g", "-f", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    def test_match_operation_short_int_exists_order_option_long_bool_exists(self):
        parser = Arguments(["-g", "13", "--force"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    def test_match_operation_short_int_exists_noorder_option_long_bool_exists(self):
        parser = Arguments(["-g", "--force", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--force"]),
            (13, True)
        )

    # int + str

    def test_match_operation_long_int_exists_order_option_long_str_exists(self):
        parser = Arguments(["--get", "13", "--message", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    def test_match_operation_long_int_exists_noorder_option_long_str_exists(self):
        parser = Arguments(["--get", "--message", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    def test_match_operation_long_int_exists_order_option_short_str_exists(self):
        parser = Arguments(["--get", "13", "-m", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    def test_match_operation_long_int_exists_noorder_option_short_str_exists(self):
        parser = Arguments(["--get", "-m", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    def test_match_operation_short_int_exists_order_option_short_str_exists(self):
        parser = Arguments(["-g", "13", "-m", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    def test_match_operation_short_int_exists_noorder_option_short_str_exists(self):
        parser = Arguments(["-g", "-m", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    def test_match_operation_short_int_exists_order_option_long_str_exists(self):
        parser = Arguments(["-g", "13", "--message", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    def test_match_operation_short_int_exists_noorder_option_long_str_exists(self):
        parser = Arguments(["-g", "--message", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--message"]),
            (13, "test1")
        )

    # int + int

    def test_match_operation_long_int_exists_order_option_long_int_exists(self):
        parser = Arguments(["--get", "13", "--level", "1312"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    def test_match_operation_long_int_exists_noorder_option_long_int_exists(self):
        parser = Arguments(["--get", "--level", "1312", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    def test_match_operation_long_int_exists_order_option_short_int_exists(self):
        parser = Arguments(["--get", "13", "-l", "1312"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    def test_match_operation_long_int_exists_noorder_option_short_int_exists(self):
        parser = Arguments(["--get", "-l", "1312", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    def test_match_operation_short_int_exists_order_option_short_int_exists(self):
        parser = Arguments(["-g", "13", "-l", "1312"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    def test_match_operation_short_int_exists_noorder_option_short_int_exists(self):
        parser = Arguments(["-g", "-l", "1312", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    def test_match_operation_short_int_exists_order_option_long_int_exists(self):
        parser = Arguments(["-g", "13", "--level", "1312"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    def test_match_operation_short_int_exists_noorder_option_long_int_exists(self):
        parser = Arguments(["-g", "--level", "1312", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--level"]),
            (13, 1312)
        )

    # int + list

    def test_match_operation_long_int_exists_order_option_long_list_exists(self):
        parser = Arguments(["--get", "13", "--args", "this", "is", "a", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_long_int_exists_noorder_option_long_list_exists(self):
        parser = Arguments(["--get", "--args", "this", "is", "a", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    def test_match_operation_long_int_exists_order_option_short_list_exists(self):
        parser = Arguments(["--get", "13", "-a", "this", "is", "a", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_long_int_exists_noorder_option_short_list_exists(self):
        parser = Arguments(["--get", "-a", "this", "is", "a", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    def test_match_operation_short_int_exists_order_option_short_list_exists(self):
        parser = Arguments(["-g", "13", "-a", "this", "is", "a", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_short_int_exists_noorder_option_short_list_exists(self):
        parser = Arguments(["-g", "-a", "this", "is", "a", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    def test_match_operation_short_int_exists_order_option_long_list_exists(self):
        parser = Arguments(["-g", "13", "--args", "this", "is", "a", "test1"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    @raises(SystemExit)
    def test_match_operation_short_int_exists_noorder_option_long_list_exists(self):
        parser = Arguments(["-g", "--args", "this", "is", "a", "test1", "13"])
        parser.add_operation("--get", short_operation="-g", value_type=int)
        parser.add_option("--args", short_option="-a", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--get"], options["--args"]),
            (13, ["this", "is", "a", "test1"])
        )

    # list + bool

    def test_match_operation_long_list_exists_order_option_long_bool_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "--force"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    def test_match_operation_long_list_exists_noorder_option_long_bool_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "--force", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    def test_match_operation_long_list_exists_order_option_short_bool_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "-f"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    def test_match_operation_long_list_exists_noorder_option_short_bool_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "-f", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    def test_match_operation_short_list_exists_order_option_short_bool_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "-f"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    def test_match_operation_short_list_exists_noorder_option_short_bool_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "-f", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    def test_match_operation_short_list_exists_order_option_long_bool_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "--force"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    def test_match_operation_short_list_exists_noorder_option_long_bool_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "--force", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--force", short_option="-f", value_type=bool)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--force"]),
            (["this", "is", "a", "test"], True)
        )

    # list + str

    def test_match_operation_long_list_exists_order_option_long_str_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "--message", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    def test_match_operation_long_list_exists_noorder_option_long_str_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "--message", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    def test_match_operation_long_list_exists_order_option_short_str_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "-m", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    def test_match_operation_long_list_exists_noorder_option_short_str_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "-m", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    def test_match_operation_short_list_exists_order_option_short_str_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "-m", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    def test_match_operation_short_list_exists_noorder_option_short_str_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "-m", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    def test_match_operation_short_list_exists_order_option_long_str_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "--message", "test1"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    def test_match_operation_short_list_exists_noorder_option_long_str_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "--message", "test1", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=str)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], "test1")
        )

    # list + int

    def test_match_operation_long_list_exists_order_option_long_int_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "--level", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    def test_match_operation_long_list_exists_noorder_option_long_int_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "--level", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    def test_match_operation_long_list_exists_order_option_short_int_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "-l", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    def test_match_operation_long_list_exists_noorder_option_short_int_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "-l", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    def test_match_operation_short_list_exists_order_option_short_int_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "-l", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    def test_match_operation_short_list_exists_noorder_option_short_int_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "-l", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    def test_match_operation_short_list_exists_order_option_long_int_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "--level", "1312"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    def test_match_operation_short_list_exists_noorder_option_long_int_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "--level", "1312", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--level", short_option="-l", value_type=int)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--level"]),
            (["this", "is", "a", "test"], 1312)
        )

    # list + list

    def test_match_operation_long_list_exists_order_option_long_list_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "--message", "test1", "ACAB"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], ["test1", "ACAB"])
        )

    def test_match_operation_long_list_exists_noorder_option_long_list_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "--message", "test1", "ACAB", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a"], ["test1", "ACAB", "test"])
        )

    def test_match_operation_long_list_exists_order_option_short_list_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "test", "-m", "test1", "ACAB"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], ["test1", "ACAB"])
        )

    def test_match_operation_long_list_exists_noorder_option_short_list_exists(self):
        parser = Arguments(["--print", "this", "is", "a", "-m", "test1", "ACAB", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a"], ["test1", "ACAB", "test"])
        )

    def test_match_operation_short_list_exists_order_option_short_list_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "-m", "test1", "ACAB"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], ["test1", "ACAB"])
        )

    def test_match_operation_short_list_exists_noorder_option_short_list_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "-m", "test1", "ACAB", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a"], ["test1", "ACAB", "test"])
        )

    def test_match_operation_short_list_exists_order_option_long_list_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "test", "--message", "test1", "ACAB"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a", "test"], ["test1", "ACAB"])
        )

    def test_match_operation_short_list_exists_noorder_option_long_list_exists(self):
        parser = Arguments(["-p", "this", "is", "a", "--message", "test1", "ACAB", "test"])
        parser.add_operation("--print", short_operation="-p", value_type=list)
        parser.add_option("--message", short_option="-m", value_type=list)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--print"], options["--message"]),
            (["this", "is", "a"], ["test1", "ACAB", "test"])
        )


class TestOperationsOptionsNoGroupParams(unittest.TestCase):
    """
    Test to match all kinds of situation with operations and options when specific parameters are passed
    """

    def test_match_operation_required_exists(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool, required=True)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    @raises(SystemExit)
    def test_match_operation_required_noexists(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_operation("--version", short_operation="-v", value_type=bool, required=True)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--version"],
            False
        )

    def test_match_option_required_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int, required=True)
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_option_required_noexists(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int, required=True)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_bool_defaultvalue(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_operation("--version", short_operation="-v", value_type=bool, default_value=True)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--version"],
            True
        )

    def test_match_operation_str_defaultvalue(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_operation("--print", short_operation="-p", value_type=str, default_value="this_default_text")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            "this_default_text"
        )

    def test_match_operation_int_defaultvalue(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_operation("--print", short_operation="-p", value_type=int, default_value=3)
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            3
        )

    def test_match_operation_list_defaultvalue(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_operation("--print", short_operation="-p", value_type=list, default_value=["this", "is", "a", "list"])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--print"],
            ["this", "is", "a", "list"]
        )

    def test_match_operation_requiredoption_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int, required_by_operations=["--help"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_requiredoption_noexists(self):
        parser = Arguments(["--help"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int, required_by_operations=["--help"])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_availableoption_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int, available_with_operations=["--help"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_availableoption_noexists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation("--help", short_operation="-h", value_type=bool)
        parser.add_option("--level", short_option="-l", value_type=int, available_with_operations=[])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )


class TestOperationsOptionsGroupParams(unittest.TestCase):
    """
    Test to match all kinds of situation with operations and options when specific parameters are passed inside groups
    """

    def test_match_operation_group_availableoption_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option("--level", short_option="-l", value_type=int, available_with_groups=["test"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_availableoption_noexists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option("--level", short_option="-l", value_type=int, available_with_groups=[])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_group_requiredoption_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option("--level", short_option="-l", value_type=int, required_by_groups=["test"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_requiredoption_noexists(self):
        parser = Arguments(["--help"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option("--level", short_option="-l", value_type=int, required_by_groups=["test"])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_group_availableoptiongroupinherit_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_groups=["test"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_availableoptiongroupinherit_noexists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_groups=[])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_group_requiredoptiongroupinherit_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", required_by_groups=["test"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_requiredoptiongroupinherit_noexists(self):
        parser = Arguments(["--help"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", required_by_groups=["test"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_group_requiredoptioninherit_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", required_by_operations=["--help"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_requiredoptioninherit_noexists(self):
        parser = Arguments(["--help"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", required_by_operations=["--help"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_group_availableoptioninherit_exists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_operations=["--help"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_availableoptioninherit_noexists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_operations=[])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts")
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_group_availableoptiongroupnoninherit_exists(self):
        parser = Arguments(["--version", "--level", "4"])
        parser.add_operation_group("test3")
        parser.add_operation("--version", short_operation="-v", value_type=bool, group="test3")
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_groups=["test"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          available_with_groups=["test3"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--version"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_group_availableoptiongroupnoninherit_noexists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation_group("test3")
        parser.add_operation("--version", short_operation="-v", value_type=bool, group="test3")
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_groups=["test"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          available_with_groups=["test3"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--help"], options["--level"]),
            (True, 4)
        )

    def test_match_operation_group_requiredoptiongroupnoninherit_exists(self):
        parser = Arguments(["--version", "--level", "4"])
        parser.add_operation_group("test3")
        parser.add_operation("--version", short_operation="-v", value_type=bool, group="test3")
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", required_by_groups=["test"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          required_by_groups=["test3"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--version"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_requiredoptiongroupnoninherit_noexists(self):
        parser = Arguments(["--help"])
        parser.add_operation_group("test3")
        parser.add_operation("--version", short_operation="-v", value_type=bool, group="test3")
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", required_by_groups=["test"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          required_by_groups=["test3"])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )

    def test_match_operation_group_requiredoptionnoninherit_exists(self):
        parser = Arguments(["--version", "--level", "4"])
        parser.add_operation_group("test3")
        parser.add_operation("--version", short_operation="-v", value_type=bool, group="test3")
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test3")
        parser.add_option_group("opts", required_by_operations=["--help"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          required_by_operations=["--version"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--version"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_requiredoptionnoninherit_noexists(self):
        parser = Arguments(["--version"])
        parser.add_operation_group("test3")
        parser.add_operation("--version", short_operation="-v", value_type=bool, group="test3")
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", required_by_operations=["--help"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          required_by_operations=["--version"])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--version"],
            True
        )

    def test_match_operation_group_availableoptionnoninherit_exists(self):
        parser = Arguments(["--version", "--level", "4"])
        parser.add_operation("--version", short_operation="-v", value_type=bool)
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_operations=["--help"])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          available_with_operations=["--version"])
        operations, options = parser.parse()
        self.assertEqual(
            (operations["--version"], options["--level"]),
            (True, 4)
        )

    @raises(SystemExit)
    def test_match_operation_availableoptionnoninherit_noexists(self):
        parser = Arguments(["--help", "--level", "4"])
        parser.add_operation("--version", short_operation="-v", value_type=bool)
        parser.add_operation_group("test")
        parser.add_operation("--help", short_operation="-h", value_type=bool, group="test")
        parser.add_option_group("opts", available_with_operations=[])
        parser.add_option("--level", short_option="-l", value_type=int, group="opts", inherit_from_group=False,
                          available_with_operations=["--version"])
        operations = parser.parse()[0]
        self.assertEqual(
            operations["--help"],
            True
        )


if __name__ == '__main__':
    unittest.main()
