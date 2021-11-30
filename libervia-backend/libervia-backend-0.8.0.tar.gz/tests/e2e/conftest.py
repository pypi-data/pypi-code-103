#!/usr/bin/env python3

# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import tempfile
import string
import hashlib
import random
from pathlib import Path
from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message
from email.message import EmailMessage
import sh
from sh import li
import pytest


class FakeFile:
    ALPHABET = f"{string.ascii_letters}{string.digits}_"
    BUF_SIZE = 65535

    def __init__(self):
        self.tmp_dir_obj = tempfile.TemporaryDirectory(prefix="libervia_e2e_test_files_")
        self.tmp_dir_path = Path(self.tmp_dir_obj.name)
        self.source_files = self.tmp_dir_path / "source"
        self.source_files.mkdir()
        self.dest_files = self.tmp_dir_path / "dest"
        self.dest_files.mkdir()
        self.hashes = {}

    @property
    def dest_path(self):
        """Path of a directory where files can be received

        The directory will be deleted at the end of session.
        Files from other test can be present, be sure to create a unique subdirectory or
        to use a unique destination file name
        """
        return self.dest_files

    def new_dest_file(self) -> Path:
        """Path to a randomly named destination file

        The file will be in self.dest_path.
        The file should be deleted after use. If not, it will be deleted at the end of
        session with the whole temporary test files directory.
        """
        name = ''.join(random.choices(self.ALPHABET, k=8))
        return self.dest_files / name

    def size(self, size: int, use_cache: bool = True):
        """Create a file of requested size, and returns its path

        @param use_cache: if True and a file of this size already exists, it is re-used
        """
        dest_path = self.source_files / str(size)
        if not use_cache or not dest_path.exists():
            hash_ = hashlib.sha256()
            remaining = size
            with dest_path.open('wb') as f:
                while remaining:
                    if remaining > self.BUF_SIZE:
                        to_get = self.BUF_SIZE
                    else:
                        to_get = remaining
                    buf = os.urandom(to_get)
                    f.write(buf)
                    hash_.update(buf)
                    remaining -= to_get
            self.hashes[dest_path] = hash_.hexdigest()
        return dest_path

    def get_source_hash(self, source_file: Path) -> str:
        """Retrieve hash calculated for a generated source file"""
        return self.hashes[source_file]

    def get_dest_hash(self, dest_file: Path) -> str:
        """Calculate hash of file at given path"""
        hash_ = hashlib.sha256()
        with dest_file.open('rb') as f:
            while True:
                buf = f.read(self.BUF_SIZE)
                if not buf:
                    break
                hash_.update(buf)
        return hash_.hexdigest()


class TestMessage(EmailMessage):

    @property
    def subject(self):
        return self['subject']

    @property
    def from_(self):
        return self['from']

    @property
    def to(self):
        return self['to']

    @property
    def body(self):
        return self.get_payload(decode=True).decode()


class SMTPMessageHandler(Message):
    messages = []

    def __init__(self):
        super().__init__(message_class=TestMessage)

    def handle_message(self, message):
        self.messages.append(message)


@pytest.fixture(scope="session")
def test_profiles():
    """Test accounts created using in-band registration

    They will be removed at the end of session.
    The number of account per servers is set in the "accounts_by_servers" dict.
    Jids are in the form "account[x]@server[y].test".
    The profiles used are in the form "account[x]" for server1.test, and
    "account[x]_s[y]" for other servers.
    Password is "test" for all profiles and XMPP accounts.
    "account1" is connected and set as default profile
    Profiles created are returned as a tuple
    """
    profiles = []
    nb_servers = 3
    accounts_by_servers = {
        1: 1,
        2: 1,
        3: 1,
    }
    for server_idx in range(1, nb_servers+1):
        account_stop = accounts_by_servers[server_idx] + 1
        for account_idx in range(1, account_stop):
            profile_suff = f"_s{server_idx}" if server_idx>1 else ""
            profile = f"account{account_idx}{profile_suff}"
            profiles.append(profile)
            try:
                li.account.create(
                    f"account{account_idx}@server{server_idx}.test",
                    "test",
                    profile=profile,
                    host=f"server{server_idx}.test"
                )
            except sh.ErrorReturnCode_19:
                # this is the conlict exit code, this can happen when tests are run
                # inside a container when --keep-profiles is used with run_e2e.py.
                pass
    li.profile.modify(profile="account1", default=True, connect=True)
    li.profile.connect(profile="account1_s2", connect=True)
    yield tuple(profiles)
    # This environment may be used during tests development
    if os.getenv("LIBERVIA_TEST_E2E_KEEP_PROFILES") == None:
        for profile in profiles:
            li.account.delete(profile=profile, connect=True, force=True)
            li.profile.delete(profile, force=True)


@pytest.fixture(scope="class")
def pubsub_nodes(test_profiles):
    """Create 2 testing nodes

    Both nodes will be created with "account1" profile, named "test" and have an "open"
    access model.
    One node will be on account1's PEP, the other one on pubsub.server1.test.
    """
    li.pubsub.node.create(
        "-f", "access_model", "open",
        node="test",
        profile="account1", connect=True
    )
    li.pubsub.node.create(
        "-f", "access_model", "open",
        service="pubsub.server1.test", node="test",
        profile="account1"
    )
    yield
    li.pubsub.node.delete(
        node="test",
        profile="account1", connect=True,
        force=True
    )
    li.pubsub.node.delete(
        service="pubsub.server1.test", node="test",
        profile="account1",
        force=True
    )


@pytest.fixture(scope="session")
def fake_file():
    """Manage dummy files creation and destination path"""
    return FakeFile()


@pytest.fixture(scope="session")
def test_files():
    """Return a Path to test files directory"""
    return Path(__file__).parent.parent / "_files"


@pytest.fixture(scope="session")
def fake_smtp():
    """Create a fake STMP server to check sent emails"""
    controller = Controller(SMTPMessageHandler())
    controller.hostname = "0.0.0.0"
    controller.start()
    yield
    controller.stop()


@pytest.fixture
def sent_emails(fake_smtp):
    """Catch email sent during the tests"""
    SMTPMessageHandler.messages.clear()
    return SMTPMessageHandler.messages


@pytest.fixture(scope="class")
def shared_data():
    """A dictionary used for share data between dependent tests"""
    return {}
