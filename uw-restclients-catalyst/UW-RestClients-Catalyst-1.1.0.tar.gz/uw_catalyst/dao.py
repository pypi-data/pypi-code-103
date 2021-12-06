# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

"""
Contains Catalyst DAO implementations.
"""
from restclients_core.dao import DAO
from os.path import abspath, dirname
from datetime import datetime
import hashlib
import pytz
import os


class Catalyst_DAO(DAO):
    def service_name(self):
        return "catalyst"

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]

    def _sol_auth_url(self, url):
        return url.replace("/rest/", "/js_rest/", 1)

    def _load_resource(self, method, url, headers, body):
        if self.get_service_setting("SOL_AUTH_PRIVATE_KEY") is not None:
            url = self._sol_auth_url(url)

        return super(Catalyst_DAO, self)._load_resource(
            method, url, headers, body)

    def _custom_headers(self, method, url, headers, body):
        private_key = self.get_service_setting("SOL_AUTH_PRIVATE_KEY")
        if private_key is not None:
            url = self._sol_auth_url(url)
            now_with_tz = datetime.now(pytz.utc).strftime(
                "%a %b %d %H:%M:%S %Z %Y")
            header_base = "%s\nGET\n%s\n%s\n" % (private_key, url, now_with_tz)
            hashed = hashlib.sha1(header_base.encode("utf-8")).hexdigest()
            public_key = self.get_service_setting("SOL_AUTH_PUBLIC_KEY")

            return {"Authorization": "SolAuth %s:%s" % (public_key, hashed),
                    "Date": now_with_tz}
