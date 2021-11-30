# Copyright 2020 Katteli Inc.
# TestFlows.com Open-Source Software Testing Framework (http://testflows.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from testflows.core import *
from testflows._core.test import TestDecorator
from testflows._core.testtype import TestSubType

RecipeModule = TestModule
RecipeSuite = TestSuite
RecipeCheck = TestCheck
RecipeOutline = TestOutline
RecipeBackground = TestBackground
RecipeStep = TestStep

class Recipe(Test):
    def __new__(cls, name=None, **kwargs):
        kwargs["subtype"] = TestSubType.Recipe
        return super(Recipe, cls).__new__(cls, name, **kwargs)

class RecipePlan(TestDecorator):
    type = Recipe
