# templtest -- a tool for testing Ansible role templates
# Copyright (C) 2021  Alexey Busygin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path
from typing import Any, Dict, Optional

from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar
from jinja2 import Environment, FileSystemLoader
from yaml import safe_load


TemplateVars = Dict[str, Any]


class BaseTemplateRenderer:

    templates: Path
    defaults: Path
    vars: Path

    def __init__(self, role: Path):
        self.templates = Path(role, "templates")
        self.defaults = Path(role, "defaults")
        self.vars = Path(role, "vars")

    def render(self, template: Path, inventory: Optional[Path] = None,
               extra: Optional[Path] = None) -> str:
        raise NotImplementedError()

    def load_variables(self, inventory: Optional[Path],
                       extra: Optional[Path]) -> TemplateVars:
        variables: TemplateVars = {}
        if self.defaults.is_dir():
            variables.update(_load_var_dir(self.defaults))
        if inventory is not None:
            variables.update(_yaml_load(inventory))
        if self.vars.is_dir():
            variables.update(_load_var_dir(self.vars))
        if extra is not None:
            variables.update(_yaml_load(extra))
        return variables


class Jinja2TemplateRenderer(BaseTemplateRenderer):

    def render(self, template: Path, inventory: Optional[Path] = None,
               extra: Optional[Path] = None) -> str:
        loader = FileSystemLoader(searchpath=str(self.templates))
        environment = Environment(
            loader=loader,
            keep_trailing_newline=True,
            lstrip_blocks=True,
            trim_blocks=True,
        )
        renderer = environment.get_template(str(template))
        variables = self.load_variables(inventory, extra)
        return renderer.render(**variables)


class AnsibleTemplateRenderer(BaseTemplateRenderer):

    def render(self, template: Path, inventory: Optional[Path] = None,
               extra: Optional[Path] = None) -> str:
        loader = _create_dataloader(self.templates)
        variables = self.load_variables(inventory, extra)
        templar = _create_templar(loader, variables)
        template_fullpath = Path(self.templates, template)
        template_text = template_fullpath.read_text(encoding="utf-8")
        return templar.template(
            variable=template_text,
            convert_data=False,
            fail_on_undefined=False,
        )


def _create_dataloader(basedir: Path) -> DataLoader:
    loader = DataLoader()
    loader.set_basedir(basedir)
    return loader


def _create_templar(loader: DataLoader, variables: TemplateVars) -> Templar:
    templar = Templar(loader=loader, variables=variables)
    templar.environment.keep_trailing_newline = True
    templar.environment.lstrip_blocks = True
    templar.environment.trim_blocks = True
    return templar


def _load_var_dir(directory: Path) -> TemplateVars:
    for filename in ["main.yml", "main.yaml", "main"]:
        path = Path(directory, filename)
        if path.is_file():
            return _yaml_load(path)
    return {}


def _yaml_load(path: Path) -> TemplateVars:
    if path.is_file():
        data = path.read_text()
        return safe_load(data)
    return {}
