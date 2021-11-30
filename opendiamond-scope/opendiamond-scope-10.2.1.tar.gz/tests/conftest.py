#
#  The OpenDiamond Platform for Interactive Search
#
# SPDX-FileCopyrightText: 2021 Carnegie Mellon University
# SPDX-License-Identifier: EPL-1.0
#

from datetime import datetime, timedelta

import pytest
from click.testing import CliRunner
from dateutil.tz import tzutc

from opendiamond.scope import ScopeCookie

from .test_cookies import KeyPair


@pytest.fixture(scope="module")
def isolated_runner():
    runner = CliRunner()
    with runner.isolated_filesystem():
        yield runner


@pytest.fixture(scope="module")
def create_scope():
    with open("key.pem", "w") as keyfile:
        keyfile.write(KeyPair.valid[0].key)

    return ScopeCookie.generate(
        ["diamond.test"],
        [],
        datetime.now(tz=tzutc()) + timedelta(days=1),
        KeyPair.valid[0].key,
    ).encode()
