#!/usr/bin/env python3

# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2021 Jérôme Poisson (goffi@goffi.org)

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

import urllib.request, urllib.error, urllib.parse
import ssl


def disable_tls_validation():
    # allow to disable certificate validation
    ctx_no_verify = ssl.create_default_context()
    ctx_no_verify.check_hostname = False
    ctx_no_verify.verify_mode = ssl.CERT_NONE

    class HTTPSHandler(urllib.request.HTTPSHandler):
        no_certificate_check = False

        def __init__(self, *args, **kwargs):
            urllib.request._HTTPSHandler_ori.__init__(self, *args, **kwargs)
            if self.no_certificate_check:
                self._context = ctx_no_verify

    urllib.request._HTTPSHandler_ori = urllib.request.HTTPSHandler
    urllib.request.HTTPSHandler = HTTPSHandler
    urllib.request.HTTPSHandler.no_certificate_check = True
