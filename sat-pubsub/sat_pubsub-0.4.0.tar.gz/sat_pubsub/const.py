#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Copyright (c) 2012-2021 Jérôme Poisson
# Copyright (c) 2013-2016 Adrien Cossa
# Copyright (c) 2003-2011 Ralph Meijer


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
# --

# This program is based on Idavoll (http://idavoll.ik.nu/),
# originaly written by Ralph Meijer (http://ralphm.net/blog/)
# It is sublicensed under AGPL v3 (or any later version) as allowed by the original
# license.

# --

# Here is a copy of the original license:

# Copyright (c) 2003-2011 Ralph Meijer

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


SERVICE_NAME = 'Libervia Pubsub Service'
NS_CLIENT = 'jabber:client'
NS_GROUPBLOG_PREFIX = 'urn:xmpp:groupblog:'
NS_ITEM_CONFIG = "http://jabber.org/protocol/pubsub#item-config"
NS_ATOM = "http://www.w3.org/2005/Atom"
NS_PUBSUB_RSM = "http://jabber.org/protocol/pubsub#rsm"
NS_FORWARD = 'urn:xmpp:forward:0'
NS_FDP = 'urn:xmpp:fdp:0'
NS_SCHEMA_RESTRICT = 'https://salut-a-toi/protocol/schema#restrict:0'

FDP_TEMPLATE_PREFIX = "fdp/template/"
FDP_SUBMITTED_PREFIX = "fdp/submitted/"

OPT_ACCESS_MODEL = 'pubsub#access_model'
OPT_ROSTER_GROUPS_ALLOWED = 'pubsub#roster_groups_allowed'
OPT_PERSIST_ITEMS = "pubsub#persist_items"
OPT_MAX_ITEMS = "pubsub#max_items"
OPT_DELIVER_PAYLOADS = "pubsub#deliver_payloads"
OPT_SEND_LAST_PUBLISHED_ITEM = "pubsub#send_last_published_item"
OPT_PUBLISH_MODEL = 'pubsub#publish_model'
OPT_OVERWRITE_POLICY = "pubsub#overwrite_policy"
OPT_CONSISTENT_PUBLISHER = 'pubsub#consistent_publisher'
OPT_SERIAL_IDS = 'pubsub#serial_ids'
OPT_FTS_LANGUAGE = 'pubsub#fts_language'
VAL_AMODEL_OPEN = 'open'
VAL_AMODEL_PRESENCE = 'presence'
VAL_AMODEL_PUBLISHER_ROSTER = 'publisher-roster'
VAL_AMODEL_WHITELIST = 'whitelist'
VAL_AMODEL_PUBLISH_ONLY = 'publish-only'
VAL_AMODEL_SELF_PUBLISHER = 'self-publisher'
VAL_AMODEL_DEFAULT = VAL_AMODEL_OPEN
VAL_AMODEL_ALL = (VAL_AMODEL_OPEN, VAL_AMODEL_PUBLISHER_ROSTER, VAL_AMODEL_WHITELIST, VAL_AMODEL_PUBLISH_ONLY, VAL_AMODEL_SELF_PUBLISHER)
VAL_PMODEL_PUBLISHERS = 'publishers'
VAL_PMODEL_SUBSCRIBERS = 'subscribers'
VAL_PMODEL_OPEN = 'open'
VAL_PMODEL_DEFAULT = VAL_PMODEL_PUBLISHERS
VAL_RSM_MAX_DEFAULT = 10 # None for no limit
VAL_FTS_GENERIC = 'generic'
VAL_OWPOL_ORIGINAL = "original_publisher"
VAL_OWPOL_ANY_PUB = "any_publisher"
VAL_OWPOL_DEFAUT = VAL_OWPOL_ORIGINAL
FLAG_ENABLE_RSM = True
FLAG_ENABLE_MAM = True
MAM_FILTER_CATEGORY = 'http://salut-a-toi.org/protocols/mam_filter_category'
MAM_FILTER_FTS = 'urn:xmpp:fulltext:0'
