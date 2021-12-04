# Copyright Louis Paternault 2015-2021
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Abstract class for jinja2 renderers."""

import datetime
import os
import pathlib
import textwrap

import jinja2
import pkg_resources

from evariste import utils
from evariste.plugins import NoMatch
from evariste.plugins.renderer.dest import DestRenderer
from evariste.plugins.renderer.jinja2.readme import Jinja2ReadmeRenderer
from evariste.plugins.renderer.jinja2.file import Jinja2FileRenderer

NOW = datetime.datetime.now()


class JinjaRenderer(DestRenderer):
    """Abstract class for jinja2 renderers."""

    # pylint: disable=too-few-public-methods

    subplugins = {"file": Jinja2FileRenderer, "readme": Jinja2ReadmeRenderer}
    default_templatevar = {
        "date": NOW.strftime("%x"),
        "time": NOW.strftime("%X"),
        "datetime": NOW.strftime("%c"),
    }
    template = "tree.html"

    def __init__(self, shared):
        super().__init__(shared)

        self.environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self._templatedirs())
        )
        self.environment.filters["basename"] = os.path.basename
        self.environment.filters["yesno"] = utils.yesno

    def _templatedirs(self):
        """Iterator over the directories in which templates may exist.

        - Directories are returned as strings;
        - directories may not exist.
        """
        if self.local.setup["templatedirs"] is not None:
            yield from utils.expand_path(self.local.setup["templatedirs"]).split()
        yield pkg_resources.resource_filename(  # pylint: disable=no-member
            self.__class__.__module__, os.path.join("data", "templates")
        )
        yield from [
            os.path.join(utils.expand_path(path), "templates")
            for path in [
                ".evariste",
                "~/.config/evariste",
                "~/.evariste",
                "/usr/share/evariste",
            ]
        ]

    def render(self, tree):
        # Copy targets to destination
        for file in tree.walk(dirs=False, files=True):
            if file.report.success:
                for target in file.report.targets:
                    utils.copy(
                        (file.root.from_fs / target).as_posix(),
                        (pathlib.Path(self.destdir) / target).as_posix(),
                    )
        # Select main template
        if self.local.setup["template"] is None:
            template = self.template
        else:
            template = self.local.setup["template"]

        # Create template loading file renderers
        content = ""
        for subrenderer in self.iter_subplugins("file"):
            if subrenderer.extension is None:
                subtemplate = subrenderer.template
            else:
                subtemplate = f"{subrenderer.template}.{subrenderer.extension}"
            content += textwrap.dedent(
                f"""\
                    {{%
                        from "file/{subtemplate}"
                        import file as file_{subrenderer.template}
                        with context
                    %}}
                    """
            )
        content += f"""{{% include "{template}" %}}"""

        # Render template
        return self.environment.from_string(content).render(
            {
                "destdir": pathlib.Path(self.destdir),
                "shared": self.shared,
                "local": self.local,
                "sourcepath": self._sourcepath,
                "render_file": self._render_file,
                "render_readme": self._render_readme,
                "render_template": self._render_template,
                "templatevar": self._get_templatevar(),
                "tree": tree,
            }
        )

    def _get_templatevar(self):
        """Return the template variables.

        - First, update it with the default variables of this class
          (`self.default_templatevar`), then its ancestors.
        - Then, update it with the variables defined in the setup file.
        """
        templatevar = {}
        for parent in reversed(self.__class__.mro()):  # pylint: disable=no-member
            templatevar.update(getattr(parent, "default_templatevar", {}))
        templatevar.update(self.shared.setup[f"{self.keyword}.templatevar"])
        return templatevar

    @jinja2.pass_context
    def _render_file(self, context, filename):
        """Render ``context['file']``, which is a :class:`pathlib.Path`."""
        for parent in self.__class__.mro():  # pylint: disable=no-member
            try:
                return self.shared.builder.plugins.match(
                    f"{parent.keyword}.file",  # pylint: disable=no-member
                    filename,
                ).render(filename, context)
            except NoMatch:
                pass
        return ""

    @jinja2.pass_context
    def _sourcepath(self, context, tree):
        """Return the path to the source file or archive.

        This functions builds the archive before returning its path. It can be
        called several times: the archive will be built only once.
        """
        # pylint: disable=no-self-use
        return tree.make_archive(context["destdir"])

    @jinja2.pass_context
    def _render_readme(self, context, tree):
        """Find the readme of tree, and returns the corresponding code."""
        # pylint: disable=unused-argument
        readme = self.render_readme(tree, context)
        if readme:
            return readme
        return ""

    @jinja2.pass_context
    def _render_template(self, context, template):
        """Render template given in argument."""
        return textwrap.indent(
            self.environment.get_or_select_template(template).render(context), "  "
        )
