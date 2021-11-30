#!/usr/bin/env python3

# Libervia Web: Libervia web frontend
# Copyright (C) 2013-2021 Jérôme Poisson <goffi@goffi.org>
# Copyright (C) 2013-2016 Adrien Cossa <souliane@mailoo.org>
# Copyright (C) 2013  Emmanuel Gil Peyrot <linkmauve@linkmauve.fr>

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

from twisted.internet import defer

if defer.Deferred.debug:
    # if we are in debug mode, we want to use ipdb instead of pdb
    try:
        import ipdb
        import pdb

        pdb.set_trace = ipdb.set_trace
        pdb.post_mortem = ipdb.post_mortem
    except ImportError:
        pass

import re
import os.path
import libervia
import sat

from libervia.server.constants import Const as C

from sat.core.i18n import _
from sat.tools import config

from zope.interface import implementer

from twisted.python import usage
from twisted.plugin import IPlugin
from twisted.application.service import IServiceMaker
import configparser


RE_VER_POST = re.compile(r"\.post[0-9]+")

if RE_VER_POST.sub("", libervia.__version__) != RE_VER_POST.sub("", sat.__version__):
    import sys

    sys.stderr.write(
        """sat module version ({sat_version}) and {current_app} version ({current_version}) mismatch

sat module is located at {sat_path}
libervia module is located at {libervia_path}

Please be sure to have the same version running
""".format(
            sat_version=sat.__version__,
            current_app=C.APP_NAME,
            current_version=libervia.__version__,
            sat_path=os.path.dirname(sat.__file__),
            libervia_path=os.path.dirname(libervia.__file__),
        )
    )
    sys.stderr.flush()
    # we call os._exit to avoid help to be printed by twisted
    import os

    os._exit(1)


def coerceConnectionType(value):  # called from Libervia.OPT_PARAMETERS
    assert isinstance(value, str)
    allowed_values = ("http", "https", "both")
    if value not in allowed_values:
        raise ValueError(
            "%(given)s not in %(expected)s"
            % {"given": value, "expected": str(allowed_values)}
        )
    return value


def coerceBool(value):
    return C.bool(value)


def coerceUnicode(value):
    assert isinstance(value, str)
    # XXX: we use this method to check which value to convert to Unicode
    #      but we don't do the conversion here as Twisted expect str
    return value


DATA_DIR_DEFAULT = ''
# prefix used for environment variables
ENV_PREFIX = "LIBERVIA_"
# options which are in sat.conf and on command line,
# see https://twistedmatrix.com/documents/current/api/twisted.python.usage.Options.html
OPT_PARAMETERS_BOTH = [['connection_type', 't', 'https', _("'http', 'https' or 'both' "
                        "(to launch both servers)."),
                        coerceConnectionType],
                       ['port', 'p', 8080,
                        _('The port number to listen HTTP on.'), int],
                       ['port_https', 's', 8443,
                        _('The port number to listen HTTPS on.'), int],
                       ['port_https_ext', 'e', 0, _('The external port number used for '
                        'HTTPS (0 means port_https value).'), int],
                       ['tls_private_key', '', '', _('TLS certificate private key (PEM '
                        'format)'), coerceUnicode],
                       ['tls_certificate', 'c', 'libervia.pem', _('TLS public '
                        'certificate or private key and public certificate combined '
                        '(PEM format)'), coerceUnicode],
                       ['tls_chain', '', '', _('TLS certificate intermediate chain (PEM '
                        'format)'), coerceUnicode],
                       ['redirect_to_https', 'r', True, _('Automatically redirect from '
                        'HTTP to HTTPS.'), coerceBool],
                       ['security_warning', 'w', True, _('Warn user that he is about to '
                        'connect on HTTP.'), coerceBool],
                       ['passphrase', 'k', '', (_("Passphrase for the SàT profile "
                        "named '%s'") % C.SERVICE_PROFILE),
                        coerceUnicode],
                       ['allow_registration', '', True, _('Allow user to register new '
                        'account'), coerceBool],
                       ['base_url_ext', '', '',
                        _('The external URL to use as base URL'),
                        coerceUnicode],
                       ['bridge-retries', '', 10,
                        _('Number of tries to connect to bridge before giving up'), int],
                      ]

# Options which are in sat.conf only
OPT_PARAMETERS_CFG = [
    ["empty_password_allowed_warning_dangerous_list", None, "", None],
    ["vhosts_dict", None, {}, None],
    ["url_redirections_dict", None, {}, None],
    ["menu_json", None, {'': C.DEFAULT_MENU}, None],
    ["menu_extra_json", None, {}, None],
    ["lists_directory_json", None, None, None],
    ["mr_handlers_json", None, None, None],
]

# Flags are in command line only
OPT_FLAGS = [
    ['build-only', 'B', _("Only build website, don't run the server")],
    ['dev-mode', 'D', _('Developer mode, automatically reload modified pages')],
]



def initialise(options):
    """Method to initialise global modules"""
    # XXX: We need to configure logs before any log method is used,
    #      so here is the best place.
    from sat.core import log_config

    log_config.satConfigure(C.LOG_BACKEND_TWISTED, C, backend_data=options)


class Options(usage.Options):
    # optArgs is not really useful in our case, we need more than a flag
    optParameters = OPT_PARAMETERS_BOTH
    optFlags = OPT_FLAGS

    def __init__(self):
        """Read SàT configuration file in order to overwrite the hard-coded default values

        Priority for the usage of the values is (from lowest to highest):
            - hard-coded default values
            - values from SàT configuration files
            - values passed on the command line
        """
        # If we do it the reading later: after the command line options have been parsed,
        # there's no good way to know
        # if the  options values are the hard-coded ones or if they have been passed
        # on the command line.

        # FIXME: must be refactored + code can be factorised with backend
        config_parser = config.parseMainConf()
        self.handleDeprecated(config_parser)
        for param in self.optParameters + OPT_PARAMETERS_CFG:
            name = param[0]
            env_name = f"{ENV_PREFIX}{name.upper()}"
            try:
                value = os.getenv(env_name)
                if value is None:
                    value = config.getConfig(
                        config_parser, C.CONFIG_SECTION, name, Exception)
                try:
                    param[2] = param[4](value)
                except IndexError:  # the coerce method is optional
                    param[2] = value
            except (configparser.NoSectionError, configparser.NoOptionError):
                pass
        usage.Options.__init__(self)
        for opt_data in OPT_PARAMETERS_CFG:
            self[opt_data[0]] = opt_data[2]

    def handleDeprecated(self, config_parser):
        """display warning and/or change option when a deprecated option if found

        param config_parser(ConfigParser): read ConfigParser instance for sat.conf
        """
        replacements = (("ssl_certificate", "tls_certificate"),)
        for old, new in replacements:
            try:
                value = config.getConfig(config_parser, C.CONFIG_SECTION, old, Exception)
            except (configparser.NoSectionError, configparser.NoOptionError):
                pass
            else:
                print(("\n/!\\ Use of {old} is deprecated, please use {new} instead\n"
                      .format(old=old, new=new)))
                config_parser.set(C.CONFIG_SECTION, new, value)


@implementer(IServiceMaker, IPlugin)
class LiberviaMaker(object):

    tapname = C.APP_NAME_FILE
    description = _("The web frontend of Libervia")
    options = Options

    def makeService(self, options):
        from twisted.internet import gireactor
        gireactor.install()
        for opt in OPT_PARAMETERS_BOTH:
            # FIXME: that's a ugly way to get unicode in Libervia
            #        from command line or sat.conf
            #        we should move to argparse and handle options this properly
            try:
                coerce_cb = opt[4]
            except IndexError:
                continue
            if coerce_cb == coerceUnicode:
                if not isinstance(options[opt[0]], str):
                    print(f"FIXME: {opt[0]} is not unicode")
                    options[opt[0]] = options[opt[0]].decode("utf-8")
        initialise(options.parent)
        from libervia.server import server

        return server.Libervia(options)


# affectation to some variable is necessary for twisted introspection to work
serviceMaker = LiberviaMaker()
