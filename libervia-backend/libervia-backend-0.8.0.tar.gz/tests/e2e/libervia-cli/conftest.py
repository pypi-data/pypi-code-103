#!/usr/bin/env python3

# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import tempfile
from pathlib import Path
from textwrap import dedent
import json
import pytest
from sh import li


class LiberviaCliJson:
    """li like commands parsing result as JSON"""

    def __init__(self):
        self.subcommands = []

    def __call__(self, *args, **kwargs):
        args = self.subcommands + list(args)
        self.subcommands.clear()
        kwargs['output'] = 'json-raw'
        kwargs['_tty_out'] = False
        cmd = li(*args, **kwargs)
        return json.loads(cmd.stdout)

    def __getattr__(self, name):
        if name.startswith('_'):
            # no li subcommand starts with a "_",
            # and pytest uses some attributes with this name scheme
            return super().__getattr__(name)
        self.subcommands.append(name)
        return self


class LiberviaCliElt(LiberviaCliJson):
    """li like commands parsing result as domishElement"""

    def __init__(self):
        super().__init__()
        from sat.tools.xml_tools import ElementParser
        self.parser = ElementParser()

    def __call__(self, *args, **kwargs):
        args = self.subcommands + list(args)
        self.subcommands.clear()
        kwargs['output'] = 'xml-raw'
        kwargs['_tty_out'] = False
        cmd = li(*args, **kwargs)
        return self.parser(cmd.stdout.decode().strip())


class Editor:

    def __init__(self):
        # temporary directory will be deleted Automatically when this object will be
        # destroyed
        self.tmp_dir_obj = tempfile.TemporaryDirectory(prefix="libervia_e2e_test_editor_")
        self.tmp_dir_path = Path(self.tmp_dir_obj.name)
        if not sys.executable:
            raise Exception("Can't find python executable")
        self.editor_set = False
        self.editor_path = self.tmp_dir_path / "editor.py"
        self.ori_content_path = self.tmp_dir_path / "original_content"
        self.new_content_path = self.tmp_dir_path / "new_content"
        self.base_script = dedent(f"""\
            #!{sys.executable}
            import sys

            def content_filter(content):
                return {{content_filter}}

            with open(sys.argv[1], 'r+') as f:
                original_content = f.read()
                f.seek(0)
                new_content = content_filter(original_content)
                f.write(new_content)
                f.truncate()

            with open("{self.ori_content_path}", "w") as f:
                f.write(original_content)

            with open("{self.new_content_path}", "w") as f:
                f.write(new_content)
            """
        )
        self._env = os.environ.copy()
        self._env["EDITOR"] = str(self.editor_path)

    def set_filter(self, content_filter: str = "content"):
        """Python code to modify original content

        The code will be applied to content received by editor.
        The original content received by editor is in the "content" variable.
        If filter_ is not specified, original content is written unmodified.
        Code must be on a single line.
        """
        if '\n' in content_filter:
            raise ValueError("new lines can't be used in filter_")
        with self.editor_path.open('w') as f:
            f.write(self.base_script.format(content_filter=content_filter))
        self.editor_path.chmod(0o700)
        self.editor_set = True

    @property
    def env(self):
        """Get environment variable with the editor set"""
        if not self.editor_set:
            self.set_filter()
        return self._env

    @property
    def original_content(self):
        """Last content received by editor, before any modification

        returns None if editor has not yet been called
        """
        try:
            with self.ori_content_path.open() as f:
                return f.read()
        except FileNotFoundError:
            return None

    @property
    def new_content(self):
        """Last content writen by editor

        This is the final content, after filter has been applied to original content
        returns None if editor has not yet been called
        """
        try:
            with self.new_content_path.open() as f:
                return f.read()
        except FileNotFoundError:
            return None


@pytest.fixture(scope="session")
def li_json():
    """Run li with "json-raw" output, and returns the parsed value"""
    return LiberviaCliJson()


@pytest.fixture(scope="session")
def li_elt():
    """Run li with "xml-raw" output, and returns the parsed value"""
    return LiberviaCliElt()


@pytest.fixture()
def editor():
    """Create a fake editor to automatise edition from CLI"""
    return Editor()
