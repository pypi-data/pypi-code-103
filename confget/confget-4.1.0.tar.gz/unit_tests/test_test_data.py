# Copyright (c) 2020  Peter Pentchev <roam@ringlet.net>
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

"""Make sure the test data is up to date."""

import sys

try:
    from typing import Set
except ImportError:
    pass

if sys.version_info[0] < 3:
    import pathlib2 as pathlib  # pylint: disable=import-error
else:
    import pathlib


def test_test_data():
    # type: () -> None
    """Compare the test data to the one in the source t/ directory."""

    def get_files(path):
        # type: (pathlib.Path) -> Set[pathlib.Path]
        """Get the relevant files from the test data directory."""
        tdefs = path / "defs/tests"
        files_ini = set(path.glob("*.ini"))
        files_tests = set(tdefs.glob("*.json"))
        assert files_ini and files_tests
        files = files_ini | files_tests
        assert (path.is_file() for path in files)
        return files

    local = pathlib.Path(__file__).parent.parent / "test_data"
    local_tests = get_files(local)

    upstream = pathlib.Path(__file__).parent.parent.parent / "t"
    if not upstream.is_dir():
        return
    upstream_tests = get_files(upstream)

    for test in sorted(upstream_tests):
        local_test = local / test.relative_to(upstream)
        assert local_test.is_file()
        assert local_test.read_text(encoding="UTF-8") == test.read_text(
            encoding="UTF-8"
        )

    for test in sorted(local_tests):
        upstream_test = upstream / test.relative_to(local)
        assert upstream_test.is_file()
