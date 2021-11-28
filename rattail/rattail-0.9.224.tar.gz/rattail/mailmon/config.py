# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Mail Monitor Configuration
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.config import ConfigProfile, parse_list
from rattail.exceptions import ConfigurationError


class MailMonitorProfile(ConfigProfile):
    """
    Simple class to hold configuration for a MailMon "profile".  Each
    profile determines which email folder(s) will be watched for new
    messages, and which action(s) will then be invoked to process the
    messages.
    """
    section = 'rattail.mailmon'

    def load(self):

        self.imap_server = self._config_string('imap.server')
        self.imap_username = self._config_string('imap.username')
        self.imap_password = self._config_string('imap.password')
        self.imap_folder = self._config_string('imap.folder')
        self.imap_unread_only = self._config_boolean('imap.unread_only')
        self.imap_delay = self._config_int('imap.delay', default=120)
        self.imap_recycle = self._config_int('imap.recycle', default=0,
                                             minimum=0)

        self.max_batch_size = self._config_int('max_batch_size', default=100)

        self.load_defaults()
        self.load_actions()

    def validate(self):
        """
        Validate the configuration for current profile.
        """
        if not self.actions:
            raise ConfigurationError("mailmon profile '{}' has no valid "
                                     "actions to invoke".format(self.key))


def load_mailmon_profiles(config):
    """
    Load all active mail monitor profiles defined within configuration.
    """
    # make sure we have a top-level directive
    keys = config.get('rattail.mailmon', 'monitor')
    if not keys:
        raise ConfigurationError(
            "The mail monitor configuration does not specify any profiles "
            "to be monitored.  Please defined the 'monitor' option within "
            "the [rattail.mailmon] section of your config file.")

    monitored = {}
    for key in parse_list(keys):
        profile = MailMonitorProfile(config, key)

        # only monitor this profile if it validates
        try:
            profile.validate()
        except ConfigurationError as error:
            log.warning(six.text_type(error))
        else:
            monitored[key] = profile

    return monitored
