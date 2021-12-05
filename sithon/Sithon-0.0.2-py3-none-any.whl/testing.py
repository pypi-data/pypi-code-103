from typing import Any

from . import log

import aiofiles
import importlib

import os
import sys


class Import:
    def __init__(self, _from, _import) -> None:
        self._from = _from
        self._import = _import

    def __str__(self):
        if self._from:
            return f"{self._from}.{self._import}"

        return self._import


class Function:
    def __init__(self, name: str, body: str, line: int) -> None:
        self.name = name
        self.body = body

        self.line = line
        self.end_pos = 0

        self.pos = 0

    def __str__(self):
        return self.name

    @property
    def cursor(self):
        return self.body[self.pos:]


class Testing:
    def __init__(self) -> None:
        self.cwd: str = os.getcwd()

        self.cur_file: str = ""
        self.code: str = ""

        self.line: int = 0

        self.test_files: list[str] = []

        self.imports: dict[str, Import] = {}
        self.functions: list[Function] = []
        self.cur_fn: Function = None

        self.idents: dict[str, str | float | int] = {}

    @property
    def locate(self):
        return ":".join([self.cur_file, self.cur_fn.name, str(self.line)])

    async def start(self) -> None:
        self._initialize_all_test_files()

        if not self.test_files:
            log.error("No test files found.")
            return

        for f in self.test_files:
            await self._parse(f)
            # remove all data, from previous file.
            self._empty()

    def _parse_import(self, line: str) -> Import:
        if " as " in line:
            log.error("Import with alias is not supported")
            sys.exit(1)

        _import = ""
        _module = ""

        if line.startswith("import "):
            _import = line.split("import ")[1].strip()

        if line.startswith("from "):
            _module, _import = line.split("from ")[1].split(" import ")

        return Import(_module, _import)

    def _empty(self):
        self.idents.clear()
        self.functions.clear()
        self.imports.clear()
        self.line = 0

    async def _parse(self, f: str):
        self.cur_file = f
        self.code = await self._get_code()

        code_split = self.code.split("\n")
        pos = 0
        while pos < len(code_split):
            line = code_split[pos]

            if not line:
                self.line += 1
                pos += 1
                continue

            if line.startswith("import ") or line.startswith("from "):
                imp = self._parse_import(line)
                self.imports[str(imp)] = imp

                self.line += 1
                pos += 1
                continue

            if line.startswith("async def ") or line.startswith("def "):
                self.line += 1

                if "def test_" not in line:
                    log.fatal(self.locate, "only test_ functions are allowed in test files.")
                    return

                _line = self.line
                start = pos
                pos += 1

                while pos + 1 <= len(code_split) and not code_split[pos].startswith("async def"):
                    pos += 1
                    self.line += 1

                body = "\n".join(code_split[start:pos])
                name = line.split("test_")[1].split("(")[0].strip()
                fun = Function(name, body, _line)
                fun.end_pos = len(body)

                self.functions.append(fun)

                continue

            self.line += 1
            pos += 1

        for fun in self.functions:
            self.line = fun.line
            self.cur_fn = fun

            fun.pos += len(fun.body.split("\n")[0])

            if "assert" not in fun.body:
                log.warn(self.locate, f"`{fun.name}` does not contain an `assert` statement.")

            while fun.pos < fun.end_pos:
                if fun.cursor[0] == "\n":
                    fun.pos += 1
                    self.line += 1
                    continue

                if fun.cursor[0].isalpha():
                    start = fun.pos
                    fun.pos += 1

                    while fun.cursor[0].isalpha():
                        fun.pos += 1

                    ident_name = fun.body[start:fun.pos]
                    fun.pos += 1

                    if fun.cursor[:1] == "=" and fun.cursor[2] != "=":
                        fun.pos += 2

                        if fun.cursor.split("\n")[0].endswith(")"):
                            # _module._name(*_args)
                            self.line += 1
                            self.idents[ident_name] = await self._parse_and_call_function(fun)
                            continue

                        if fun.cursor[0] == '"' or fun.cursor[0] == "'":
                            starter = fun.cursor[0]

                            fun.pos += 1
                            start = fun.pos

                            while (fun.cursor[0] != '"' and starter == '"') or (
                                    fun.cursor[0] != "'" and starter == "'"):
                                fun.pos += 1

                                if fun.cursor[0] == "\n":
                                    self.line += 1

                            self.idents[ident_name] = fun.body[start:fun.pos]
                            self.line += 1
                            continue

                        if fun.cursor[0].isnumeric():
                            self.line += 1
                            if fun.cursor[:1] == "x":
                                log.fatal(self.locate, "hexadecimal numbers are not supported.")
                                return

                            start = fun.pos

                            while fun.cursor[0].isnumeric() or fun.cursor[0] == ".":
                                fun.pos += 1

                            self.idents[ident_name], _ = Testing.check_type(fun.body[start:fun.pos])
                    else:
                        if ident_name == "assert":
                            start = fun.pos
                            fun.pos += 6

                            while fun.pos + 1 < len(fun.body):
                                fun.pos += 1

                                if fun.cursor[0] == "\n":
                                    break

                            full = fun.body[start:fun.pos + 1]
                            left, right = full.split(" == ")

                            left, ltype = Testing.check_type(left.strip())
                            right, rtype = Testing.check_type(right.strip())

                            if ltype == "ident":
                                if left not in self.idents:
                                    if len(left.split("(")) > 1:
                                        left = await self._parse_and_call_function(left)
                                    else:
                                        log.fatal(self.locate, f"Identifier `{left}` not found.")
                                        return
                                else:
                                    left = self.idents[left]

                            if rtype == "ident":
                                if right not in self.idents:
                                    # is function
                                    if len(right.split("(")) > 1:
                                        right = await self._parse_and_call_function(right)
                                    else:
                                        log.fatal(self.locate, f"Identifier `{right}` not found.")
                                        return
                                else:
                                    right = self.idents[right]

                            if left != right:
                                log.test_fail(self.locate, full, left, right)
                            else:
                                log.test_pass(self.locate, full, left, right)

                            self.line += 1

                fun.pos += 1

    def get_import(self, name: str) -> Import:
        for imp in self.imports.values():
            if imp._import == name:
                return imp

    async def _parse_and_call_function(self, fun: Function | str) -> Any:
        # _module._name(*_args)
        is_coroutine = False

        if isinstance(fun, Function):
            func = fun.cursor.split("\n")[0].split("(")[0]
        else:
            func = fun.split("(")[0]

        if func.startswith("await"):
            is_coroutine = True
            func = func.split("await ")[1]

        _module, _name = func.split(".")

        if isinstance(fun, Function):
            _args = fun.cursor.split("\n")[0].split("(")[1].split(")")[0].split(",")
        else:
            _args = fun.split("(")[1].split(")")[0].split(",")

        if len(_args) == 1 and _args[0] == "":
            _args.clear()

        if not (module := self.get_import(_module)):
            log.fatal(self.locate, f"module `{_module}` is not imported.")
            return

        sys.path.append(os.path.join(self.cwd, _module))
        module = importlib.import_module(str(module))

        if not hasattr(module, _name):
            log.fatal(self.locate, f"module `{_module}` does not have function `{_name}`.")
            return

        if _args:
            for idx, val in enumerate(_args):
                _args[idx], _ = Testing.check_type(val.strip())

        try:
            if is_coroutine:
                return await getattr(module, _name)(*_args)

            return getattr(module, _name)(*_args)
        except Exception as e:
            return e

    async def _get_code(self):
        async with aiofiles.open(self.cur_file, mode="r") as f:
            ret = await f.read()

            if ret:
                return ret

            log.fatal(self.locate, "Could not read: " + self.cur_file)

    @staticmethod
    def check_type(val: str) -> list[int | float | str, str]:
        if (
            "." in val and (len((check := val.split("."))) == 2
            and check[0].isdigit() and check[1].isdigit())
        ):
            return [float(val), "float"]

        if val.isdigit():
            return [int(val), "int"]

        if val.startswith("'") and val.endswith("'") or val.startswith('"') and val.endswith('"'):
            return [val.split('"')[1] or val.split("'")[1], "string"]

        return [val, "ident"]

    def _initialize_all_test_files(self) -> None:
        for root, dirs, files in os.walk('.'):
            for f in files:
                if f.startswith('test_') and f.endswith(".py"):
                    self.test_files.append(os.path.join(root, f))
