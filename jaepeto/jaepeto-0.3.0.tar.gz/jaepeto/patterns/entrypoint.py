"""
Detect important functions to the codebase.
"""
import ast
import os
import re
from itertools import groupby
from operator import itemgetter
from pathlib import Path
from typing import List, Optional, Tuple


def identify_module_imports(
    module: str, file_contents: List[str]
) -> List[Tuple[str, str]]:
    imports = []

    for line in file_contents:
        if up_import_match := re.match(r"from \.\.(\w.*) import", line):
            _import_group = up_import_match.group(1)

            if resolved_import := _identify_uplevel_import(
                module, line, _import_group, from_import=True
            ):
                imports.extend(resolved_import)
        elif up_import_match := re.match(r"import \.\.(\w.*)", line):
            _import_group = up_import_match.group(1)

            if resolved_import := _identify_uplevel_import(
                module, line, _import_group, from_import=False
            ):
                imports.extend(resolved_import)
        elif resolved_import := _identify_module_import(module, line):
            imports.extend(resolved_import)

    return imports


def _identify_uplevel_import(
    module: str, line: str, import_group: str, from_import: bool
) -> List[str]:
    if "." in module:
        _new_module = ".".join(module.split(".")[:-1])
    else:
        _new_module = ""

    if from_import:
        _new_line = re.sub(
            rf"from \.\.{import_group} import", rf"from .{import_group} import", line
        )
    else:
        _new_line = re.sub(
            rf"import \.\.{import_group}", rf"import .{import_group}", line
        )

    return _identify_module_import(_new_module, _new_line)


def _identify_module_import(module: str, line: str) -> List[str]:
    imports = []

    if from_match := re.match(
        rf"from ({module}(\..*)?|\..*) import (.*)", line.strip()
    ):
        submodule = from_match.group(1)

        if submodule.startswith("."):
            submodule = module + submodule

        for module_import in from_match.group(3).split(","):
            as_split_import = module_import.split("as ")

            import_path = f"{submodule}.{as_split_import[0].strip()}"

            if len(as_split_import) == 1:
                imports.append((import_path, as_split_import[0].strip()))
            elif len(as_split_import) == 2:
                import_representation = as_split_import[1].strip()
                imports.append((import_path, import_representation))
            else:
                raise ImportError(f"Unrecognised import type {module_import}")
    elif import_match := re.match(rf"import ((?:{module}|\.).*)", line.strip()):
        import_path = import_match.group(1).strip()

        if import_path.startswith("."):
            import_path = module + import_path

        imports.append((import_path, import_path))

    return imports


def identify_module_calls(
    imports: List[Tuple[str, str]], file_contents: List[str]
) -> List[str]:
    """
    Identify uses of a module within a codebase.

    Looks for function calls of given imports for a given file.

    Parameters
    ----------
    imports : list of (str, str) tuples
        Module imports in the file. May be imported as a module, or a function using the `from` syntax.
        First element of each tuple is the import. Second element is the imported object as would appear in the file.
    file_contents : list of str
        List of lines in a given file. Lines to read for function calls.

    Returns
    -------
    list of str
        <module>.<function> for each function called in the given file

    Examples
    --------
    >>> imports = [("module.sub", "module.sub")]
    >>> contents = ["result = module.sub.func(1, 2, 3)"]
    >>> identify_module_uses(imports, contents)
        ["module.sub.func"]

    >>> imports = [("module.sub.func", "func_alias")]
    >>> contents = ["func_alias()"]
    >>> identify_module_uses(imports, contents)
        ["module.sub.func"]
    """
    called_imports = []

    for line in file_contents:
        if not imports:
            return []

        for idx, (module_path, module_import) in enumerate(imports):
            if object_call_match := re.search(
                rf"(^|[^a-zA-Z_\.]){module_import}(\..*)?\(.*\)", line
            ):
                if submodule_group := object_call_match.group(2):
                    called_imports.append(module_path + submodule_group)
                else:
                    called_imports.append(module_path)

    return called_imports


def resolve_import_paths(
    module: str, file_path: Path, root: Optional[Path] = None
) -> List[str]:
    """
    Resolve object imports to absolute paths.

    Parameters
    ----------
    module : str
        The name of the module for imports
    file_path : pathlib.Path
        Relative path to a file to read the imports of
    root : pathlib.Path, optional
        Root path from which to form absolute path. If none, use `file_path.parents[1]`.
        Should be one step above `module`.

    Returns
    -------
    list of str
        Absolute imports for functions imported in `file_path`

    Raises
    ------
    RuntimeError
        If a detected imported module does not have an __init__ file and file does not exist
    """
    with open(file_path, "r") as f:
        file_contents = f.readlines()

    absolute_imports: List[str] = []
    imports = identify_module_imports(module, file_contents)

    root = root if root else file_path.parents[1]

    for _import_statement, _ in imports:
        _imported_path = Path(os.sep.join(_import_statement.split(".")[:-1]))
        _imported_path_absolute = root / _imported_path

        if _imported_path_absolute.with_suffix(".py").exists():
            # Import points to file. Assume imported object lies within the file
            absolute_imports.append(_import_statement)
        elif _imported_path_absolute.is_dir():
            _imported_path_init = _imported_path_absolute / "__init__.py"

            if not _imported_path_init.exists():
                raise RuntimeError(
                    f"Trying to resolve {_import_statement}; {_imported_path_init} does not exist"
                )

            resolved_imports = resolve_import_paths(
                ".".join(_import_statement.split(".")[:-1]),
                _imported_path_init,
                root=root,
            )

            for _resolved_import in resolved_imports:
                # TODO: warn if no import resolution is made
                if _resolved_import.split(".")[-1] == _import_statement.split(".")[-1]:
                    # Assume module does not have multiple objects with same name
                    absolute_imports.append(_resolved_import)
                    break
        else:
            raise RuntimeError(f"{_imported_path_absolute} cannot be resolved")

    return absolute_imports


def infer_important_functions(module: str, root: Path) -> List[str]:
    module_root = root / module

    if (main_file := module_root / "__main__.py").exists():
        # TODO detect called functions in main
        paths = resolve_import_paths(module, main_file)
        if all_imports := detect_all_imports(main_file):
            paths = [p for p in paths if p.split(".")[-1] in all_imports]
        return paths

    elif (init_file := module_root / "__init__.py").exists():
        paths = resolve_import_paths(module, init_file)
        if all_imports := detect_all_imports(init_file):
            paths = [p for p in paths if p.split(".")[-1] in all_imports]
        return paths

    else:
        return []


def detect_all_imports(file: Path):
    with open(file, "r") as f:
        tree = ast.parse(f.read())

    for elem in tree.body:
        if not isinstance(elem, ast.Assign):
            continue

        if elem.targets[0].id != "__all__":
            continue

        return [all_import.value for all_import in elem.value.elts]

    return None


def group_imports_at_level(imports: List[str], level: int):
    if level < 1:
        raise ValueError(f"Level must be greater than 0, was {level}")

    short_imports = [
        ".".join(split_import[:level])
        for split_import in [_import.split(".") for _import in imports]
        if len(split_import) >= level
    ]
    short_imports.sort()

    grouped_imports = []

    for _import, grouper in groupby(short_imports):
        counts = 0
        for _ in grouper:
            counts += 1
        grouped_imports.append((_import, counts))

    grouped_imports.sort(key=itemgetter(1), reverse=True)
    return grouped_imports
