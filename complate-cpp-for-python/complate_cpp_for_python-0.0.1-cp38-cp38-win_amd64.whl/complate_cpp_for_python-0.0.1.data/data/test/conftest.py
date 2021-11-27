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

from complatecpp import QuickJsRendererBuilder

from fixtures.assets import Assets
from fixtures.todo import TodoWithSlots, TodoWithProps
from fixtures.timespan import Timespan


@pytest.fixture
def quickjs_renderer(views, bindings, prototypes):
    return QuickJsRendererBuilder() \
        .source(views) \
        .bindings(bindings) \
        .prototypes(prototypes) \
        .unique()


@pytest.fixture
def views():
    with open(resource_path("views.js")) as views:
        return views.read()


@pytest.fixture
def views_creator(views):
    return lambda: views


@pytest.fixture
def views_mock():
    with open(resource_path("views.mock.js")) as views:
        return views.read()


@pytest.fixture
def views_malformed():
    with open(resource_path("views.js.malformed")) as views:
        return views.read()


@pytest.fixture
def bindings():
    return {
        "renderedBy": "complate-cpp-for-python",
        "getRendererLink": lambda: "https://github.com/tmehnert/complate-cpp-for-python",
        "assets": Assets(base_uri="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist")
    }


@pytest.fixture
def bindings_creator(bindings):
    return lambda: bindings


@pytest.fixture
def prototypes():
    return [Assets, TodoWithSlots, TodoWithProps, Timespan]


@pytest.fixture
def prototypes_creator(prototypes):
    return lambda: prototypes


@pytest.fixture
def todolist_html():
    with open(resource_path("todolist.html")) as views:
        return views.read()


@pytest.fixture
def todolist_parameters():
    return {
        "todos": [
            TodoWithSlots(what="Change the tires of your car",
                          description="You stored the tires at your mom's house.",
                          updateLink="https://example.org/todos/4/update",
                          timespan=Timespan(amount=9, unit="days", veryLate=True)),
            TodoWithProps(what="Book a hotel for next summer",
                          description="Hopefully our situation is then better.",
                          updateLink="https://example.org/todos/5/update",
                          timespan=Timespan(amount=11, unit="months", veryLate=False))
        ]
    }


def resource_path(filename):
    from os.path import dirname
    return "%s/resources/%s" % (dirname(__file__), filename)
