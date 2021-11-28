# -*- coding: utf-8 -*-

"""

"""

from __future__ import unicode_literals
import sphinx.util
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList
from sphinx.directives.other import TocTree
from pathlib_mate import Path

from ..doctree import ArticleFolder


class AutoTocTree(Directive):
    """
    Automatically includes ``index.rst`` in toctree from::

        <current_dir>/<any-folder>/index.rst

    Any toctree directive arguments are supported.

    Example, the content of ``<current_dir>/index.rst``::

        .. autodoctree::

    Will be converted to::

        .. toctree::

            ./section1/index.rst
            ./section2/index.rst
            ...
    """
    _opt_append_ahead = "append_ahead"
    _opt_index_file = "index_file"
    _opt_index_file_default = "index.rst"

    has_content = True
    option_spec = TocTree.option_spec.copy()
    option_spec[_opt_append_ahead] = directives.flag
    option_spec[_opt_index_file] = str

    def run(self):
        node = nodes.Element()
        node.document = self.state.document
        current_file = self.state.document.current_source
        output_rst = self.derive_toctree_rst(current_file)
        view_list = StringList(output_rst.splitlines(), source="")
        sphinx.util.nested_parse_with_titles(self.state, view_list, node)
        return node.children

    def derive_toctree_rst(self, current_file):
        """
        Generate the rst content::

            .. toctree::
                args ...

                example.rst
                ...

        :param current_file:
        :return:
        """
        TAB = " " * 4
        lines = list()

        # create the .. toctree:: and its options
        lines.append(".. toctree::")
        for opt in TocTree.option_spec:
            value = self.options.get(opt)
            if value is not None:
                line = "{indent}:{option}: {value}".format(
                    indent=TAB,
                    option=opt,
                    value=value,
                ).rstrip()
                lines.append(line)
        lines.append("")

        if self._opt_append_ahead in self.options:
            for line in list(self.content):
                lines.append(TAB + line)
        index_file = self.options.get(self._opt_index_file, self._opt_index_file_default)

        article_folder = ArticleFolder(
            index_file=index_file,
            dir_path=Path(current_file).parent.abspath,
        )
        for af in article_folder.sub_article_folders:
            line = "{indent}{title} <{relpath}>".format(
                indent=TAB,
                title=af.title,
                relpath=af.rel_path,
            )
            lines.append(line)

        if self._opt_append_ahead not in self.options:
            for line in list(self.content):
                lines.append(TAB + line)

        lines.append("")
        return "\n".join(lines)
