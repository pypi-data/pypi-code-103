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
import shutil
import pytest
import sh
from sh import li
from sat.tools.common import uri


if os.getenv("LIBERVIA_TEST_ENV_E2E") is None:
    pytest.skip(
        "skipping end-to-end tests, we are not in a test environment",
        allow_module_level=True
    )


pytestmark = pytest.mark.usefixtures("test_profiles")


class TestInstall:

    def test_li_can_run(self):
        li("--version")


class TestLiberviaCliAccount:

    def test_create_and_delete(self, li_json):
        """Create an account in-band, connect it, then delete it and its profile"""
        li.account.create(
            "test_create@server1.test",
            "test",
            profile="test_create",
            host="server1.test"
        )
        profiles = li_json.profile.list()
        assert "test_create" in profiles
        li.profile.connect(connect=True, profile="test_create")
        li.account.delete(profile="test_create", force=True)
        li.profile.delete("test_create", force=True)
        profiles = li_json.profile.list()
        assert "test_create" not in profiles


@pytest.mark.usefixtures("pubsub_nodes")
class TestLiberviaCliPubsub:

    def test_node_create_info_delete(self):
        node_name = "tmp_node"
        with pytest.raises(sh.ErrorReturnCode_16):
            # the node should not exist
            li.pubsub.node.info(node=node_name)
        try:
            li.pubsub.node.create(node=node_name)
            # if node exist as expected, following command won't raise an exception
            metadata = li.pubsub.node.info(node=node_name)
            assert len(metadata.strip())
        finally:
            li.pubsub.node.delete(node=node_name, force=True)

        with pytest.raises(sh.ErrorReturnCode_16):
            # the node should not exist anymore
            li.pubsub.node.info(node=node_name)

    def test_set_get_delete_purge(self, li_elt):
        content = "test item"
        payload = f"<test>{content}</test>"

        # we create 3 items and check them
        item1_id = li.pubsub.set(node="test", quiet=True, _in=payload)
        item2_id = li.pubsub.set(node="test", quiet=True, _in=payload)
        item3_id = li.pubsub.set(node="test", quiet=True, _in=payload)
        parsed_elt = li_elt.pubsub.get(node="test", item=item1_id)
        payload = parsed_elt.firstChildElement()
        assert payload.name == 'test'
        assert str(payload) == content
        parsed_elt = li_elt.pubsub.get(node="test", item=item2_id)
        payload = parsed_elt.firstChildElement()
        assert payload.name == 'test'
        assert str(payload) == content
        parsed_elt = li_elt.pubsub.get(node="test", item=item3_id)
        payload = parsed_elt.firstChildElement()
        assert payload.name == 'test'
        assert str(payload) == content

        # deleting first item should work
        li.pubsub.delete(node="test", item=item1_id, force=True)
        with pytest.raises(sh.ErrorReturnCode_16):
            li.pubsub.get(node="test", item=item1_id)

        # there must be a least item2 and item3 in the node
        node_items = li_elt.pubsub.get(node="test")
        assert len(list(node_items.elements())) >= 2

        # after purge, node must be empty
        li.pubsub.node.purge(node="test", force=True)
        node_items = li_elt.pubsub.get(node="test")
        assert len(list(node_items.elements())) == 0

    def test_edit(self, editor, li_elt):
        content = "original item"
        payload = f"<test>{content}</test>"
        item_id = li.pubsub.set(node="test", quiet=True, _in=payload)
        editor.set_filter('content.replace("original", "edited")')
        li.pubsub.edit(node="test", item=item_id, _env=editor.env)
        assert "original item" in editor.original_content
        parsed_elt = li_elt.pubsub.get(node="test", item=item_id)
        edited_payload = parsed_elt.firstChildElement()
        expected_edited_content = content.replace("original", "edited")
        assert edited_payload.name == 'test'
        assert str(edited_payload) == expected_edited_content

    def test_affiliations(self, li_json):
        affiliations = li_json.pubsub.affiliations()
        assert affiliations["test"] == "owner"

    def test_uri(self):
        built_uri = li.pubsub.uri(
            service="pubsub.example.net", node="some_node"
        ).strip()
        assert built_uri == "xmpp:pubsub.example.net?;node=some_node"
        built_uri = li.pubsub.uri(
            service="pubsub.example.net", node="some_node", item="some_item"
        ).strip()
        assert built_uri == "xmpp:pubsub.example.net?;node=some_node;item=some_item"


class TestLiberviaCliBlog:
    MICROBLOG_NS = "urn:xmpp:microblog:0"

    def test_set_get(self, li_json):
        li.blog.set(_in="markdown **bold** [link](https://example.net)")
        item_data = li_json.blog.get(max=1)
        item = item_data[0][0]
        metadata = item_data[1]
        assert metadata['service'] == "account1@server1.test"
        assert metadata['node'] == self.MICROBLOG_NS
        assert metadata['rsm'].keys() <= {"first", "last", "index", "count"}
        item_id = item['id']
        expected_uri = uri.buildXMPPUri(
            'pubsub', subtype="microblog", path="account1@server1.test",
            node=self.MICROBLOG_NS, item=item_id
        )
        assert item['uri'] == expected_uri
        assert item['content_xhtml'] == (
            '<div><p>markdown <strong>bold</strong> '
            '<a href="https://example.net">link</a></p></div>'
        )
        assert isinstance(item['published'], int)
        assert isinstance(item['updated'], int)
        assert isinstance(item['comments'], list)
        assert isinstance(item['tags'], list)
        assert item['author'] == 'account1'
        assert item['author_jid'] == 'account1@server1.test'

    def test_edit(self, editor, li_json):
        payload_md = "content in **markdown**"
        editor.set_filter(repr(payload_md))
        li.blog.edit(_env=editor.env)
        assert len(editor.original_content) == 0
        assert editor.new_content == payload_md
        items_data = li_json.blog.get(max_items=1)
        last_item = items_data[0][0]
        last_item_id = last_item['id']
        assert last_item['content'] == "content in markdown"
        assert last_item['content_xhtml'] == (
            "<div><p>content in <strong>markdown</strong></p></div>"
        )
        editor.set_filter('f"{content} extended"')
        li.blog.edit("--last-item", _env=editor.env)
        assert editor.original_content == payload_md
        assert editor.new_content == f"{payload_md} extended"
        items_data = li_json.blog.get(max_items=1)
        last_item = items_data[0][0]
        # we check that the id hasn't been modified
        assert last_item['id'] == last_item_id
        assert last_item['content'] == "content in markdown extended"
        assert last_item['content_xhtml'] == (
            "<div><p>content in <strong>markdown</strong> extended</p></div>"
        )


class TestLiberviaCliFile:

    def test_upload_get(self, fake_file):
        source_file = fake_file.size(10240)
        source_file_hash = fake_file.get_source_hash(source_file)
        upload_url = li.file.upload(source_file).strip()

        dest_file = fake_file.new_dest_file()
        try:
            li.file.get(upload_url, dest_file=dest_file)
            dest_file_hash = fake_file.get_dest_hash(dest_file)
        finally:
            dest_file.unlink()

        assert source_file_hash == dest_file_hash

    def test_send_receive(self, fake_file):
        source_file = fake_file.size(10240)
        source_file_hash = fake_file.get_source_hash(source_file)
        send_cmd = li.file.send(source_file, "account1@server2.test", _bg=True)
        dest_path = fake_file.dest_files / "test_send_receive"
        dest_path.mkdir()
        try:
            li.file.receive(
                "account1@server1.test", profile="account1_s2", path=dest_path)
            dest_file = dest_path / source_file.name
            dest_file_hash = fake_file.get_dest_hash(dest_file)
        finally:
            shutil.rmtree(dest_path)
        send_cmd.wait()

        assert source_file_hash == dest_file_hash
