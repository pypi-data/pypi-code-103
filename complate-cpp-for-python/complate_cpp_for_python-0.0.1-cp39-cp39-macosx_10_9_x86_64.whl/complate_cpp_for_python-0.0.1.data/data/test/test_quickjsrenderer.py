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
import json
from complatecpp import QuickJsRenderer, StringStream
from fixtures.encoder import Encoder


def test_construct_throws_render_undefined():
    with pytest.raises(RuntimeError, match=".*ReferenceError: 'render' is not defined.*"):
        QuickJsRenderer("")


def test_construct_views_malformed(views_malformed):
    with pytest.raises(RuntimeError, match=".*SyntaxError.*"):
        QuickJsRenderer(views_malformed)


def test_render_dict_throws_view_undefined(views):
    renderer = QuickJsRenderer(views)
    with pytest.raises(RuntimeError, match=".*Error: unknown view macro: `MissingView` is not registered.*"):
        renderer.render_tostring("MissingView", {})


def test_render_dict(quickjs_renderer, todolist_parameters, todolist_html):
    stream = StringStream()
    quickjs_renderer.render(
        view="TodoList",
        parameters=todolist_parameters,
        stream=stream
    )
    assert stream.str() == todolist_html


def test_render_dict_tostring(quickjs_renderer, todolist_parameters, todolist_html):
    html = quickjs_renderer.render_tostring(
        view="TodoList",
        parameters=todolist_parameters
    )
    assert html == todolist_html


def test_render_json_throws_view_undefined(views):
    renderer = QuickJsRenderer(views)
    with pytest.raises(RuntimeError, match=".*Error: unknown view macro: `MissingView` is not registered.*"):
        renderer.render_tostring("MissingView", "{}")


def test_render_json_throws_not_object(views):
    renderer = QuickJsRenderer(views)
    with pytest.raises(RuntimeError, match=".*SyntaxError: 'parameters' is not an object.*"):
        renderer.render_tostring("TodoList", "")


def test_render_json(quickjs_renderer, todolist_parameters, todolist_html):
    stream = StringStream()
    quickjs_renderer.render(
        view="TodoList",
        parameters=json.dumps(todolist_parameters, cls=Encoder),
        stream=stream
    )
    assert stream.str() == todolist_html


def test_render_json_tostring(quickjs_renderer, todolist_parameters, todolist_html):
    html = quickjs_renderer.render_tostring(
        view="TodoList",
        parameters=json.dumps(todolist_parameters, cls=Encoder)
    )
    assert html == todolist_html
