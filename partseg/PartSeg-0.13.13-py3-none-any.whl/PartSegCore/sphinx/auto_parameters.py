"""
This module contain utilities to document Register class.
"""
import inspect
from typing import Any, Dict

from sphinx.application import Sphinx
from sphinx.ext.autodoc import ModuleLevelDocumenter

from PartSegCore.algorithm_describe_base import AlgorithmDescribeBase, AlgorithmProperty, Register
from PartSegCore.class_generator import extract_type_info, extract_type_name


# noinspection PyUnusedLocal
def algorithm_parameters_doc(app: Sphinx, what, name: str, obj, options, lines: list):
    if inspect.isclass(obj) and issubclass(obj, AlgorithmDescribeBase) and not inspect.isabstract(obj):
        fields = [x for x in obj.get_fields() if isinstance(x, AlgorithmProperty)]
        if fields:
            lines.extend(["", "This algorithm has following parameters:", ""])
        for el in fields:
            if el.help_text:
                lines.append(
                    "- **{}** ({})- {}, {}".format(
                        el.name, extract_type_name(el.value_type), el.user_name, el.help_text
                    )
                )
            else:
                lines.append(f"- **{el.name}** ({extract_type_name(el.value_type)})- {el.user_name}")


class RegisterDocumenter(ModuleLevelDocumenter):
    objtype = "register_data"
    directivetype = "data"

    @classmethod
    def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
        return isinstance(member, Register)

    def document_members(self, all_members: bool = False) -> None:
        pass

    def add_content(self, more_content: Any, no_docstring: bool = False) -> None:
        super().add_content(more_content, no_docstring)
        if not isinstance(self.object, Register):
            raise ValueError("Not Register object")
        source = "autogenerated"
        k = 0
        if self.object.methods:
            self.add_line(
                "Need methods: {}".format(", ".join("``" + x + "``" for x in self.object.methods)),
                source,
                k,
            )

            self.add_line("", source, k + 1)
            k += 2
        if self.object.class_methods:
            self.add_line(
                "Need class methods: {}".format(", ".join("``" + x + "``" for x in self.object.class_methods)),
                source,
                k,
            )

            self.add_line("", source, k + 1)
            k += 2
        self.add_line("Default content:", source, k)
        self.add_line("", "autogenerated", k + 1)
        k += 2
        for i, (name, val) in enumerate(self.object.items(), k):
            self.add_line(f"- **{name}** - :py:class:`~{extract_type_info(val)[0]}`", "autogenerated", i)
        self.add_line("", "autogenerated", len(self.object) + k)


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect("autodoc-process-docstring", algorithm_parameters_doc)
    app.add_autodocumenter(RegisterDocumenter)
    return {"version": "0.9", "env_version": 1, "parallel_read_safe": True}
