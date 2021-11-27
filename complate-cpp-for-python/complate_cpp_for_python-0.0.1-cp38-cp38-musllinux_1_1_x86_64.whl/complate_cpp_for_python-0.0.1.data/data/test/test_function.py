# Copyright 2021 Torsten Mehnert
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import pytest
from complatecpp import Value


def test_without_arguments():
    value = Value(lambda: "I have no args :(")
    func = value.get_function()
    assert func.apply([]) == "I have no args :("


def test_with_1_argument():
    value = Value(lambda a1: 23 + a1)
    func = value.get_function()
    assert func.apply([1]) == 24


def test_with_2_arguments():
    value = Value(lambda a1, a2: 23 + a1 + a2)
    func = value.get_function()
    assert func.apply([1, 2]) == 26


def test_with_3_arguments():
    value = Value(lambda a1, a2, a3: 23 + a1 + a2 + a3)
    func = value.get_function()
    assert func.apply([1, 2, 3]) == 29


def test_with_4_arguments():
    value = Value(lambda a1, a2, a3, a4: 23 + a1 + a2 + a3 + a4)
    func = value.get_function()
    assert func.apply([1, 2, 3, 4]) == 33


def test_with_5_arguments():
    value = Value(lambda a1, a2, a3, a4, a5: 23 + a1 + a2 + a3 + a4 + a5)
    func = value.get_function()
    assert func.apply([1, 2, 3, 4, 5]) == 38


def test_with_6_arguments():
    value = Value(lambda a1, a2, a3, a4, a5, a6: 23 + a1 + a2 + a3 + a4 + a5 + a6)
    func = value.get_function()
    assert func.apply([1, 2, 3, 4, 5, 6]) == 44


def test_with_7_arguments():
    value = Value(lambda a1, a2, a3, a4, a5, a6, a7: 23 + a1 + a2 + a3 + a4 + a5 + a6 + a7)
    func = value.get_function()
    assert func.apply([1, 2, 3, 4, 5, 6, 7]) == 51


def test_with_8_arguments():
    value = Value(lambda a1, a2, a3, a4, a5, a6, a7, a8: 23 + a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8)
    func = value.get_function()
    assert func.apply([1, 2, 3, 4, 5, 6, 7, 8]) == 59


def test_with_default_argument():
    value = Value(lambda x=5: x + 1)
    func = value.get_function()
    assert func.apply([]) == 6
    assert func.apply([1]) == 2


def test_throws_on_more_than_8_arguments():
    value = Value(lambda: "Too much arguments")
    func = value.get_function()
    with pytest.raises(ValueError, match=".*More then 8 arguments are not supported.*"):
        func.apply([1, 2, 3, 4, 5, 6, 7, 8, 9])


def test_throws_on_missing_arguments():
    value = Value(lambda a1, a2: a1 + a2)
    func = value.get_function()
    with pytest.raises(TypeError, match=".*missing 1 required positional argument: 'a2'.*"):
        func.apply([1])


def test_throws_on_too_much_arguments():
    value = Value(lambda a1: a1)
    func = value.get_function()
    with pytest.raises(TypeError, match=".*takes 1 positional argument but 2 were given.*"):
        func.apply([1, 2])
