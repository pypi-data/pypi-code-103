"""
Write technical docs
"""
import os
import re
from datetime import datetime
from pathlib import Path
from textwrap import dedent
from typing import Optional

from jaepeto.patterns import (
    CIParser,
    ContainerParser,
    PyVersionDetector,
    describe_file_architecture,
    group_imports_at_level,
    infer_important_functions,
    read_packages,
)
from jaepeto.summaries import summarise_function
from jaepeto.utils import get_line_changes_for_file, parse_config, post


def create_technical_doc(
    source_module_name: str,
    source_code_dir: Path,
    technical_doc_file: Path,
    repo_info: str = None,
    project_title: str = "Project",
    project_summary: Optional[str] = None,
):
    write_document_intro(technical_doc_file, project_title, project_summary)
    create_architecture_section(source_code_dir, technical_doc_file)
    create_src_overview(
        source_module_name, source_code_dir / source_module_name, technical_doc_file
    )


def write_document_intro(technical_doc_file: Path, project_title: str, project_summary):
    with open(technical_doc_file, "w") as file:
        file.write(f"# {(project_title + ' Technical Documentation').strip()}")
        file.write(f"\n\n**Last updated:** {datetime.now().strftime('%Y-%m-%d')}\\")
        file.write("\n_Document generation aided by **Jaepeto**_")

        if project_summary:
            file.write(f"\n\n{project_summary}")

        file.write("\n\n* [Introduction](#introduction)")
        file.write("\n* [Code Overview](#code-overview)")

        file.write("\n\n## Introduction")
        file.write(
            f"""\n\nThis is a technical document detailing
        at a high-level
        what {project_title} does, how it operates,
        and how it is built.
        It is meant for consumption internally
        by technical developers
        and managers."""
        )

        file.write("\n\n### Scope")
        file.write(
            """\n\nThis document provides high-level summaries
        of the project codebase."""
        )

        file.write("\n\n### Context")
        file.write(
            """\n\nThe outline of this document was generated
        by **Jaepeto**.
        The documentation should be reviewed
        and detail provided manually
        before the documentation is released."""
        )


def create_architecture_section(source_code_dir: Path, technical_doc_file: Path):
    with open(technical_doc_file, "r") as f:
        contents = f.readlines()

    contents.append("\n\n## Project Architecture\n\n")

    if packages := read_packages(source_code_dir):
        contents.append("The project has the following dependencies:\n")
        for _package in packages:
            contents.append(f"\n* {_package}")
        contents.append("\n\n")

    container_parser = ContainerParser()
    if container_arch := container_parser.parse(source_code_dir):
        contents.append(container_arch + "\n\n")

    ci_parser = CIParser()
    ci_parser.parse(source_code_dir)
    if ci_arch := str(ci_parser):
        contents.append(ci_arch + "\n\n")

    with open(technical_doc_file, "w") as file:
        file.writelines(contents)


def create_src_overview(
    module_name: str, source_code_dir: Path, technical_doc_file: Path
):
    with open(technical_doc_file, "r") as file:
        contents = file.readlines()

    # Assume contents just have intro
    contents.append("\n\n## Code Overview\n\n")

    version_detector = PyVersionDetector()

    for pyfile in source_code_dir.glob("**/*.py"):
        with open(pyfile, "r") as f:
            _pyfile_contents = f.readlines()

        version_detector.review(pyfile, _pyfile_contents)
    del _pyfile_contents
    contents.append(str(version_detector) + "\n\n")

    entrypoints = infer_important_functions(module_name, source_code_dir.parent)
    num_entrypoints = len(entrypoints)

    if 0 < num_entrypoints <= 5:
        contents.append(
            f"There are {num_entrypoints} source code objects in top-level `__main__`/`__init__`:\n\n"
        )
        for _entrypoint in entrypoints:
            entrypoint_func = _entrypoint.split(".")[-1]
            entrypoint_file = (os.sep).join(_entrypoint.split(".")[:-1]) + ".py"
            contents.append(f"### `{entrypoint_func}` from `{entrypoint_file}`\n")

            _entrypoint_doc = summarise_function(entrypoint_func, entrypoint_file)
            if _entrypoint_doc:
                contents.append(f" \n```\n{_entrypoint_doc}\n```\n")
            else:
                contents.append(
                    "\nFunction cannot be summarised: No documentation is present for this code.\n"
                )

        contents.append(
            "\nThese entrypoints are broken down into the following modules:\n\n"
        )
    elif num_entrypoints == 0:
        contents.append(
            f"There are 0 source code entrypoints in top-level `__main__`/`__init__` files.\n"
        )
    else:
        contents.append(
            f"""There are {num_entrypoints} source code objects
                        in top-level `__main__`/`__init__`.
                        They are broken down into the following modules:\n\n"""
        )

    entrypoint_groups = group_imports_at_level(entrypoints, level=2)
    for _entrypoint, _count in entrypoint_groups:
        contents.append(f"* `{_entrypoint}` has {_count} entrypoints\n")

    new_contents, _ = create_module_overview(
        source_code_dir, [f"\n### **{source_code_dir.stem}/**"], 0
    )
    contents += new_contents

    with open(technical_doc_file, "w") as file:
        file.writelines(contents)


def create_module_overview(module_path: Path, doc_contents, n_calls: int):
    hash_level = len(doc_contents[-1].replace("\n", "").split()[0]) + 1

    for subdir in module_path.glob("*"):
        if subdir.stem == "__pycache__":
            continue

        if subdir.is_dir():
            doc_contents.append(f"\n\n{'#'*hash_level} {subdir.stem}/")
            doc_contents, n_calls = create_module_overview(
                subdir, doc_contents, n_calls
            )

    for py_file in module_path.glob("*.py"):
        if py_file.stem == "__init__":
            continue

        doc_contents.append(f"\n\n{'#'*hash_level} {py_file.stem}.py")

        lines_added, lines_removed, most_common_author = get_line_changes_for_file(
            str(py_file)
        )
        doc_contents.append(
            dedent(
                f"""
            \n\nFile has {lines_added} lines added and {lines_removed} lines removed
            in the past 4 weeks."""
            )
        )
        if most_common_author:
            doc_contents[-1] += f" {most_common_author} is the inferred code owner."

        doc_contents.append("\n")

        if file_arch := describe_file_architecture(py_file):
            doc_contents.append(file_arch)

    return doc_contents, n_calls


def generate_documentation() -> None:
    """
    Generate and save technical documentation.

    This is a CLI entrypoint to the codebase.
    The current working directory must be the root of the project
    for which documentation is to be generated.
    The root project must contain a `.jaepeto.ini` file.
    """
    config_path = Path.cwd() / ".jaepeto.ini"

    if not config_path.exists():
        print(f"Error running jaepeto: No config file found at {config_path}")
    else:
        config = parse_config(config_path)

        tech_doc_path = (
            config_path.parent / config["doc_dir"] / config["docs"]["technical_name"]
        ).with_suffix(".md")

        post("notify", None)

        create_technical_doc(
            config["src"],
            config_path.parent,
            tech_doc_path,
            project_title=config["name"],
            project_summary=config["description"],
        )
        print(f"Successfully generated technical documentation at {tech_doc_path}")
