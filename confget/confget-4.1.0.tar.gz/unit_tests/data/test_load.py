# Copyright (c) 2018 - 2021  Peter Pentchev <roam@ringlet.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""Load a test definition from a JSON file."""
# pylint: disable=consider-using-dict-comprehension

import io
import json
import os

from . import test_defs as tdefs

try:
    from typing import Any, Dict  # noqa: H301

    TESTING_USED = (tdefs, Any, Dict)
except ImportError:
    pass


def _load_test_v2(data, _version):
    # type: (Dict[str, Any], Dict[str, int]) -> tdefs.FileDef
    """Load the tests from a v1.x test file."""
    build = {"tests": []}  # type: Dict[str, Any]

    for test in data["tests"]:
        raw = dict(
            [
                (key, value)
                for key, value in test.items()
                if key in ("args", "keys", "xform", "backend", "stdin")
            ]
        )

        if "exact" in test["output"]:
            raw["output"] = tdefs.ExactOutputDef(exact=test["output"]["exact"])
        elif "exit" in test["output"]:
            raw["output"] = tdefs.ExitOKOutputDef(
                success=test["output"]["exit"]
            )
        else:
            raise ValueError("test output: " + repr(test["output"]))

        build["tests"].append(tdefs.SingleTestDef(**raw))

    return tdefs.FileDef(**build)


_PARSERS = {2: _load_test_v2}


def load_test(fname):
    # type: (str) -> tdefs.FileDef
    """Load a single test file into a TestFileDef object."""
    with io.open(fname, mode="r", encoding="UTF-8") as testf:
        data = json.load(testf)

    version = {
        "major": data["format"]["version"]["major"],
        "minor": data["format"]["version"]["minor"],
    }
    assert isinstance(version["major"], int)
    assert isinstance(version["minor"], int)

    parser = _PARSERS.get(version["major"], None)
    if parser is not None:
        return parser(data, version)
    raise NotImplementedError(
        "Unsupported test format version {major}.{minor} for {fname}".format(
            major=version["major"], minor=version["minor"], fname=fname
        )
    )


def load_all_tests(testdir):
    # type: (str) -> Dict[str, tdefs.FileDef]
    """Load all the tests in the defs/tests/ subdirectory."""
    tdir = testdir + "/defs/tests/"
    filenames = sorted(
        fname for fname in os.listdir(tdir) if fname.endswith(".json")
    )
    return dict(
        [
            (os.path.splitext(fname)[0], load_test(tdir + fname))
            for fname in filenames
        ]
    )
