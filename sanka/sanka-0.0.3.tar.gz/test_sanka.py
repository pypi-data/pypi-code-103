from unittest import TestCase

from sanka import Sanka


class SankaTest(TestCase):

    def test_count_calls_for_no_arg_function(self):

        @Sanka
        def function():
            pass

        num_calls = 10

        for i in range(num_calls):
            function()

        assert function(Sanka.YaDead) == num_calls

    def test_count_calls_for_function_with_args(self):

        @Sanka
        def function(takes, some_args):
            pass

        num_calls = 10

        for i in range(num_calls):
            function('takes', 'some_args')

        assert function(Sanka.YaDead) == num_calls

