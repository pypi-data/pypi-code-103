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
import re
import pytest
from helium import (
    go_to, write, press, click, drag_file, find_all, wait_until, S, Text, Link, Button,
    select, scroll_down, get_driver, ENTER
)


if os.getenv("LIBERVIA_TEST_ENV_E2E_WEB") is None:
    pytest.skip(
        "skipping end-to-end tests, we are not in a test environment for Libervia",
        allow_module_level=True
    )

pytestmark = pytest.mark.usefixtures("test_profiles", "screenshot_on_failure")


class TestLogin:

    def test_user_can_create_account(self, nobody_logged_in, sent_emails):
        go_to("https://libervia-web.test:8443/login")
        click("no account yet")
        write("new_account", into="login")
        write("some_email@example.net", into="email")
        write("testtest", into="password")
        click("register new account")
        wait_until(lambda: get_driver().current_url.endswith("/login"))
        write("testtest", into="password")
        click("log in")
        wait_until(Text("you are logged").exists)
        wait_until(lambda: len(sent_emails) == 2)
        if sent_emails[0].to == "admin@server1.test":
            admin_email, user_email = sent_emails
        else:
            user_email, admin_email = sent_emails
        assert admin_email.to == "admin@server1.test"
        # profile name must be specified in admin email
        assert "new_account" in admin_email.body
        assert user_email.to == "some_email@example.net"
        # user jid must be specified in the email
        assert "new_account@server1.test" in user_email.body
        # use can now log-in

    def test_user_can_log_in(self, nobody_logged_in):
        go_to("https://libervia-web.test:8443/login")
        write("account1_s3", into="login")
        write("test", into="password")
        click("log in")
        wait_until(Text("you are logged").exists)
        assert Button("Disconnect").exists()

    def test_wrong_password_fails(self, nobody_logged_in):
        go_to("https://libervia-web.test:8443/login")
        write("account1_s2", into="login")
        write("wrong_password", into="password")
        click("log in")
        assert Text("Your login and/or password is incorrect. Please try again.")


class TestPhotos:
    ACCOUNT1_ALBUMS_URL = (
        "https://libervia-web.test:8443/photos/album/account1@files.server1.test/albums"
    )
    TEST_ALBUM_URL = f"{ACCOUNT1_ALBUMS_URL}/test%20album"

    @pytest.mark.dependency(name="create_album")
    def test_user_can_create_album(self, log_in_account1):
        go_to("https://libervia-web.test:8443/photos")
        wait_until(Link("create").exists)
        click("create")
        write("test album", into="album name")
        click("create")
        album_link = Link("test album")
        wait_until(album_link.exists)
        click(album_link)
        wait_until(lambda: S("#file_drop").exists())
        wait_until(lambda: not S("#loading_screen").exists())
        drag_file("/src/libervia-backend/tests/_files/test_1.jpg", "drop photos here")
        wait_until(lambda: len(find_all(S("div.progress_finished")))==1)
        drag_file("/src/libervia-backend/tests/_files/test_2.jpg", "drop photos here")
        wait_until(lambda: len(find_all(S("div.progress_finished")))==2)
        assert S('img[alt="test_1.jpg"]').exists()
        assert S('img[alt="test_2.jpg"]').exists()

    @pytest.mark.dependency(depends=["create_album"])
    def test_user_can_slideshow(self, log_in_account1):
        go_to(self.TEST_ALBUM_URL)
        wait_until(lambda: not S("#loading_screen").exists())
        thumb_1 = S("img[alt='test_1.jpg'].is-photo-thumbnail")
        assert thumb_1.exists()
        click(thumb_1)
        assert S("div.slideshow").exists()
        active_slide_1 = S("div.swiper-slide-active")
        assert active_slide_1.exists()
        # if we don't save the web_element here, the test in wait_until fails
        # it seems that Helium is re-using the selector, i.e. we get the other
        # slide in active_slide_1.
        active_slide_1_elt = active_slide_1.web_element
        click(S(".swiper-button-next"))
        wait_until(
            lambda:
            "swiper-slide-active" not in active_slide_1_elt.get_attribute("class")
        )
        active_slide_2 = S("div.swiper-slide-active")
        assert active_slide_2.exists()
        active_slide_2_elt = active_slide_2.web_element
        assert active_slide_1_elt != active_slide_2_elt
        click(S(".click_to_close"))
        assert not S("div.slideshow").exists()

    @pytest.mark.dependency(name="ext_user_no_access", depends=["create_album"])
    def test_external_user_cant_access_album(self, log_in_account1_s2):
        go_to(self.TEST_ALBUM_URL)
        assert Text("Unauthorized").exists()
        assert "Error" in get_driver().title

    @pytest.mark.dependency(name="invite_ext_user", depends=["create_album", "ext_user_no_access"])
    def test_invitation_of_external_user(self, log_in_account1):
        """User can invite somebody not in its roster by its full JID"""
        go_to(self.TEST_ALBUM_URL)
        wait_until(lambda: not S("#loading_screen").exists())
        click("manage invitations")
        assert Text("people who can access this page").exists()
        contact_input = S("input[name='contact']")
        write("account1@server2.test", into=contact_input)
        press(ENTER)
        assert contact_input.web_element.get_attribute("value") == ""
        assert Text("account1@server2.test").exists()

    @pytest.mark.dependency(depends=["create_album", "invite_ext_user"])
    def test_invited_user_can_access_album(self, log_in_account1_s2):
        go_to(self.TEST_ALBUM_URL)
        assert not Text("Unauthorized").exists()
        assert not "Error" in get_driver().title
        assert len(find_all(S("img.is-photo-thumbnail"))) == 2

    @pytest.mark.dependency(name="invite_by_email", depends=["create_album"])
    def test_invitation_by_email(self, log_in_account1, sent_emails, shared_data):
        """User can invite somebody without XMPP account by email"""
        go_to(self.TEST_ALBUM_URL)
        wait_until(lambda: not S("#loading_screen").exists())
        click("manage invitations")
        assert Text("people who can access this page").exists()
        click("invite by email")
        wait_until(Text("Invite somebody by email").exists)
        write("somebody@example.net", "email")
        write("Some Guest", "name")
        click("send invitation")
        wait_until(lambda: len(sent_emails) == 1)
        invitation_email = sent_emails[0]
        assert "Welcome" in invitation_email.body
        url_match = re.search(r"https:\/\/.+\/g\/\w+", sent_emails[0].body)
        assert url_match is not None
        shared_data["invitation_url"] = url_match.group()

    @pytest.mark.dependency(depends=["invite_by_email"])
    def test_email_guest_can_access_album(self, nobody_logged_in, shared_data):
        go_to(shared_data["invitation_url"])
        click("test album")
        wait_until(lambda: not S("#loading_screen").exists())
        assert len(find_all(S("img.is-photo-thumbnail"))) == 2


class TestLists:
    TEST_GENERIC_LIST_URL = (
        "https://libervia-web.test:8443/lists/view/account1@server1.test/"
        "fdp%2Fsubmitted%2Forg.salut-a-toi.tickets%3A0_test-generic-list"
    )

    @pytest.mark.dependency(name="create_generic_list")
    def test_user_can_create_generic(self, log_in_account1):
        go_to("https://libervia-web.test:8443/lists/view")
        click("create a list")
        tickets_btn = S("//span[text()='Tickets']")
        click(tickets_btn)
        write("test-generic-list", "name of the list")
        click("create list")
        wait_until(Text("Success").exists)


    @pytest.mark.dependency(
        name="create_generic_list_item", depends=["create_generic_list"]
    )
    def test_user_can_create_generic_list_item(self):
        go_to(self.TEST_GENERIC_LIST_URL)
        click("create")
        write("test item", "title")
        write("label 1, label 2", "labels")
        select("type", "feature request")
        write("this is a test body", "body")
        scroll_down(600)
        click("create list item")
        wait_until(Text("Success").exists)
        assert Link("create").exists()
        assert Link("manage invitations").exists()
        item = Link("test item")
        assert item.exists()
        labels_elt = item.web_element.find_element_by_class_name("xmlui_field__labels")
        labels = [t.text for t in labels_elt.find_elements_by_tag_name("span")]
        assert labels == ["label 1", "label 2"]

    @pytest.mark.dependency(depends=["create_generic_list_item"])
    def test_list_item_can_be_displayed(self):
        go_to(self.TEST_GENERIC_LIST_URL)
        item = Link("test item")
        # FIXME: we can't click on the item created above with Selenium, looks like a
        #        Selenium bug, to be checked
        go_to(item.href)
        item_title = Text("test item")
        assert item_title.exists()
        item_body = Text("this is a test body")
        assert item_body.exists()
