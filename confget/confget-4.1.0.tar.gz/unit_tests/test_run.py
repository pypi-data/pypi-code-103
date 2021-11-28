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

"""Run the confget tests using the Python methods.

Load the test data, then run the tests using the objects provided by
the Python library, not by executing the command-line tool.
"""

import io
import itertools
import sys
import unittest

import ddt  # type: ignore

import confget

from confget import format as cformat

# pylint: disable=wrong-import-position
from .data import test_defs as tdefs  # noqa: E402
from .data import test_load as tload  # noqa: E402

# pylint: enable=wrong-import-position


try:
    from typing import Dict

    _TYPING_USED = [Dict, tdefs]
except ImportError:
    _TYPING_USED = [tdefs]


TESTS = tload.load_all_tests(tdefs.get_test_path(None))

FULL_TEST_DATA_BEFORE_RIF = [
    (fname, test)
    for fname, idx, test in sorted(
        itertools.chain(
            *[
                [
                    (tfile[0], idx, test)
                    for idx, test in enumerate(tfile[1].tests)
                ]
                for tfile in TESTS.items()
            ]
        )
    )
]

FULL_TEST_DATA = list(
    itertools.chain(
        *[
            [(fname, use_rif, test) for use_rif in (False, True)]
            for fname, test in FULL_TEST_DATA_BEFORE_RIF
        ]
    )
)

SKIP_ARGS = set(["check_only"])


@ddt.ddt
class TestStuff(unittest.TestCase):
    # pylint: disable=no-self-use
    """Run the tests using the Python library."""

    @ddt.data(*FULL_TEST_DATA)
    @ddt.unpack
    def test_run(
        self,  # type: TestStuff
        fname,  # type: str
        use_rif,  # type: bool
        test,  # type: tdefs.SingleTestDef
    ):  # type: (...) -> None
        """Instantiate a confget object, load the data, check it."""

        if set(test.args.keys()) & SKIP_ARGS:
            return
        if test.backend != "ini" and use_rif:
            return

        config = test.get_config()

        def get_file_data():
            # type: () -> Dict[str, Dict[str, str]]
            """Read the file data: backend or read_ini_file()."""
            if use_rif:
                return confget.read_ini_file(config)

            backend = test.get_backend()
            obj = backend(config)
            return obj.read_file()

        if test.stdin:
            fname = tdefs.get_test_path(test.stdin)
            with io.open(fname, mode="r", encoding="UTF-8") as stdin:
                save_stdin = sys.stdin
                try:
                    sys.stdin = stdin
                    data = get_file_data()
                finally:
                    sys.stdin = save_stdin
        else:
            data = get_file_data()

        res = cformat.filter_vars(config, data)
        output = test.do_xform(line for line in res)
        test.output.check_result(output)
