from unittest import TestCase

from sanka import sanka
from sanka import YaDead


class SankaTest(TestCase):

    def test___str__(self):

        @sanka
        def function():
            pass

        assert str(function) == 'function'

    def test_count_calls_for_no_arg_function(self):

        @sanka
        def function():
            pass

        num_calls = 2

        for i in range(num_calls):
            function()

        assert function(YaDead) == num_calls

    def test_count_calls_for_function_with_args(self):

        @sanka
        def function(takes, some_args):
            pass

        num_calls = 2

        for i in range(num_calls):
            function('takes', 'some_args')

        assert function(YaDead) == num_calls

    def test_count_calls_for_multiple_functions(self):

        @sanka
        def function1():
            pass
        @sanka
        def function2():
            pass

        num_calls_for_first_function = 2
        num_calls_for_second_function = 3

        for i in range(num_calls_for_first_function):
            function1()
        for i in range(num_calls_for_second_function):
            function2()

        assert function1(YaDead) == num_calls_for_first_function
        assert function2(YaDead) == num_calls_for_second_function

    def test_sanka_decorator_can_detect_no_function_calls(self):
        @sanka
        def function():
            pass

        assert function(YaDead) == 0

    def test_sanka_decorator_only_accepts_function_as_callback(self):

        with self.assertRaises(TypeError):
            @sanka(callback='not a function')
            def function():
                pass

    def test_sanka_decorator_can_accept_callback(self):
        @sanka(callback=lambda count: count)
        def function():
            pass

        num_calls = 2

        for i in range(num_calls):
            function()

        assert function(YaDead) == num_calls

    def test_sanka_can_call_back_every_call(self):
        side_effect_counts = []

        @sanka(
            callback=lambda count: side_effect_counts.append(count),
            only_callback_when_dead = False
        )
        def function():
            pass

        num_calls = 2

        for i in range(num_calls):
            function()

        assert side_effect_counts == list(range(1, num_calls + 1))
        assert function(YaDead) == num_calls

