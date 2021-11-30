#!/usr/bin/env python3

# jp: a SAT command line tool
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

import asyncio
from sat.core.i18n import _

### logging ###
import logging as log
log.basicConfig(level=log.WARNING,
                format='[%(name)s] %(message)s')
###

import sys
import os
import os.path
import argparse
import inspect
import tty
import termios
from pathlib import Path
from glob import iglob
from importlib import import_module
from sat_frontends.tools.jid import JID
from sat.tools import config
from sat.tools.common import dynamic_import
from sat.tools.common import uri
from sat.tools.common import date_utils
from sat.tools.common import utils
from sat.tools.common.ansi import ANSI as A
from sat.core import exceptions
import sat_frontends.jp
from sat_frontends.jp.loops import QuitException, getJPLoop
from sat_frontends.jp.constants import Const as C
from sat_frontends.bridge.bridge_frontend import BridgeException
from sat_frontends.tools import misc
import xml.etree.ElementTree as ET  # FIXME: used temporarily to manage XMLUI
from collections import OrderedDict

## bridge handling
# we get bridge name from conf and initialise the right class accordingly
main_config = config.parseMainConf()
bridge_name = config.getConfig(main_config, '', 'bridge', 'dbus')
JPLoop = getJPLoop(bridge_name)


try:
    import progressbar
except ImportError:
    msg = (_('ProgressBar not available, please download it at '
             'http://pypi.python.org/pypi/progressbar\n'
             'Progress bar deactivated\n--\n'))
    print(msg, file=sys.stderr)
    progressbar=None

#consts
DESCRIPTION = """This software is a command line tool for XMPP.
Get the latest version at """ + C.APP_URL

COPYLEFT = """Copyright (C) 2009-2021 Jérôme Poisson, Adrien Cossa
This program comes with ABSOLUTELY NO WARRANTY;
This is free software, and you are welcome to redistribute it under certain conditions.
"""

PROGRESS_DELAY = 0.1 # the progression will be checked every PROGRESS_DELAY s


def date_decoder(arg):
    return date_utils.date_parse_ext(arg, default_tz=date_utils.TZ_LOCAL)


class LiberviaCli:
    """
    This class can be use to establish a connection with the
    bridge. Moreover, it should manage a main loop.

    To use it, you mainly have to redefine the method run to perform
    specify what kind of operation you want to perform.

    """
    def __init__(self):
        """

        @attribute quit_on_progress_end (bool): set to False if you manage yourself
            exiting, or if you want the user to stop by himself
        @attribute progress_success(callable): method to call when progress just started
            by default display a message
        @attribute progress_success(callable): method to call when progress is
            successfully finished by default display a message
        @attribute progress_failure(callable): method to call when progress failed
            by default display a message
        """
        self.sat_conf = main_config
        self.set_color_theme()
        bridge_module = dynamic_import.bridge(bridge_name, 'sat_frontends.bridge')
        if bridge_module is None:
            log.error("Can't import {} bridge".format(bridge_name))
            sys.exit(1)

        self.bridge = bridge_module.AIOBridge()
        self._onQuitCallbacks = []

    def get_config(self, name, section=C.CONFIG_SECTION, default=None):
        """Retrieve a setting value from sat.conf"""
        return config.getConfig(self.sat_conf, section, name, default=default)

    def guess_background(self):
        # cf. https://unix.stackexchange.com/a/245568 (thanks!)
        try:
            # for VTE based terminals
            vte_version = int(os.getenv("VTE_VERSION", 0))
        except ValueError:
            vte_version = 0

        color_fg_bg = os.getenv("COLORFGBG")

        if ((sys.stdin.isatty() and sys.stdout.isatty()
             and (
                 # XTerm
                 os.getenv("XTERM_VERSION")
                 # Konsole
                 or os.getenv("KONSOLE_VERSION")
                 # All VTE based terminals
                 or vte_version >= 3502
             ))):
            # ANSI escape sequence
            stdin_fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(stdin_fd)
            try:
                tty.setraw(sys.stdin.fileno())
                # we request background color
                sys.stdout.write("\033]11;?\a")
                sys.stdout.flush()
                expected = "\033]11;rgb:"
                for c in expected:
                    ch = sys.stdin.read(1)
                    if ch != c:
                        # background id is not supported, we default to "dark"
                        # TODO: log something?
                        return 'dark'
                red, green, blue = [
                    int(c, 16)/65535 for c in sys.stdin.read(14).split('/')
                ]
                # '\a' is the last character
                sys.stdin.read(1)
            finally:
                termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_settings)

            lum = utils.per_luminance(red, green, blue)
            if lum <= 0.5:
                return 'dark'
            else:
                return 'light'
        elif color_fg_bg:
            # no luck with ANSI escape sequence, we try COLORFGBG environment variable
            try:
                bg = int(color_fg_bg.split(";")[-1])
            except ValueError:
                return "dark"
            if bg in list(range(7)) + [8]:
                return "dark"
            else:
                return "light"
        else:
            # no autodetection method found
            return "dark"

    def set_color_theme(self):
        background = self.get_config('background', default='auto')
        if background == 'auto':
            background = self.guess_background()
        if background not in ('dark', 'light'):
            raise exceptions.ConfigError(_(
                'Invalid value set for "background" ({background}), please check '
                'your settings in libervia.conf').format(
                    background=repr(background)
                ))
        self.background = background
        if background == 'light':
            C.A_HEADER = A.FG_MAGENTA
            C.A_SUBHEADER = A.BOLD + A.FG_RED
            C.A_LEVEL_COLORS = (C.A_HEADER, A.BOLD + A.FG_BLUE, A.FG_MAGENTA, A.FG_CYAN)
            C.A_SUCCESS = A.FG_GREEN
            C.A_FAILURE = A.BOLD + A.FG_RED
            C.A_WARNING = A.FG_RED
            C.A_PROMPT_PATH = A.FG_BLUE
            C.A_PROMPT_SUF = A.BOLD
            C.A_DIRECTORY = A.BOLD + A.FG_MAGENTA
            C.A_FILE = A.FG_BLACK

    def _bridgeConnected(self):
        self.parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter, description=DESCRIPTION)
        self._make_parents()
        self.add_parser_options()
        self.subparsers = self.parser.add_subparsers(
            title=_('Available commands'), dest='command', required=True)

        # progress attributes
        self._progress_id = None # TODO: manage several progress ids
        self.quit_on_progress_end = True

        # outputs
        self._outputs = {}
        for type_ in C.OUTPUT_TYPES:
            self._outputs[type_] = OrderedDict()
        self.default_output = {}

        self.own_jid = None  # must be filled at runtime if needed

    @property
    def progress_id(self):
        return self._progress_id

    async def set_progress_id(self, progress_id):
        # because we use async, we need an explicit setter
        self._progress_id = progress_id
        await self.replayCache('progress_ids_cache')

    @property
    def watch_progress(self):
        try:
            self.pbar
        except AttributeError:
            return False
        else:
            return True

    @watch_progress.setter
    def watch_progress(self, watch_progress):
        if watch_progress:
            self.pbar = None

    @property
    def verbosity(self):
        try:
            return self.args.verbose
        except AttributeError:
            return 0

    async def replayCache(self, cache_attribute):
        """Replay cached signals

        @param cache_attribute(str): name of the attribute containing the cache
            if the attribute doesn't exist, there is no cache and the call is ignored
            else the cache must be a list of tuples containing the replay callback as
            first item, then the arguments to use
        """
        try:
            cache = getattr(self, cache_attribute)
        except AttributeError:
            pass
        else:
            for cache_data in cache:
                await cache_data[0](*cache_data[1:])

    def disp(self, msg, verbosity=0, error=False, end='\n'):
        """Print a message to user

        @param msg(unicode): message to print
        @param verbosity(int): minimal verbosity to display the message
        @param error(bool): if True, print to stderr instead of stdout
        @param end(str): string appended after the last value, default a newline
        """
        if self.verbosity >= verbosity:
            if error:
                print(msg, end=end, file=sys.stderr)
            else:
                print(msg, end=end)

    async def output(self, type_, name, extra_outputs, data):
        if name in extra_outputs:
            method = extra_outputs[name]
        else:
            method = self._outputs[type_][name]['callback']

        ret = method(data)
        if inspect.isawaitable(ret):
            await ret

    def addOnQuitCallback(self, callback, *args, **kwargs):
        """Add a callback which will be called on quit command

        @param callback(callback): method to call
        """
        self._onQuitCallbacks.append((callback, args, kwargs))

    def getOutputChoices(self, output_type):
        """Return valid output filters for output_type

        @param output_type: True for default,
            else can be any registered type
        """
        return list(self._outputs[output_type].keys())

    def _make_parents(self):
        self.parents = {}

        # we have a special case here as the start-session option is present only if
        # connection is not needed, so we create two similar parents, one with the
        # option, the other one without it
        for parent_name in ('profile', 'profile_session'):
            parent = self.parents[parent_name] = argparse.ArgumentParser(add_help=False)
            parent.add_argument(
                "-p", "--profile", action="store", type=str, default='@DEFAULT@',
                help=_("Use PROFILE profile key (default: %(default)s)"))
            parent.add_argument(
                "--pwd", action="store", metavar='PASSWORD',
                help=_("Password used to connect profile, if necessary"))

        profile_parent, profile_session_parent = (self.parents['profile'],
                                                  self.parents['profile_session'])

        connect_short, connect_long, connect_action, connect_help = (
            "-c", "--connect", "store_true",
            _("Connect the profile before doing anything else")
        )
        profile_parent.add_argument(
            connect_short, connect_long, action=connect_action, help=connect_help)

        profile_session_connect_group = profile_session_parent.add_mutually_exclusive_group()
        profile_session_connect_group.add_argument(
            connect_short, connect_long, action=connect_action, help=connect_help)
        profile_session_connect_group.add_argument(
            "--start-session", action="store_true",
            help=_("Start a profile session without connecting"))

        progress_parent = self.parents['progress'] = argparse.ArgumentParser(
            add_help=False)
        if progressbar:
            progress_parent.add_argument(
                "-P", "--progress", action="store_true", help=_("Show progress bar"))

        verbose_parent = self.parents['verbose'] = argparse.ArgumentParser(add_help=False)
        verbose_parent.add_argument(
            '--verbose', '-v', action='count', default=0,
            help=_("Add a verbosity level (can be used multiple times)"))

        quiet_parent = self.parents['quiet'] = argparse.ArgumentParser(add_help=False)
        quiet_parent.add_argument(
            '--quiet', '-q', action='store_true',
            help=_("be quiet (only output machine readable data)"))

        draft_parent = self.parents['draft'] = argparse.ArgumentParser(add_help=False)
        draft_group = draft_parent.add_argument_group(_('draft handling'))
        draft_group.add_argument(
            "-D", "--current", action="store_true", help=_("load current draft"))
        draft_group.add_argument(
            "-F", "--draft-path", type=Path, help=_("path to a draft file to retrieve"))


    def make_pubsub_group(self, flags, defaults):
        """generate pubsub options according to flags

        @param flags(iterable[unicode]): see [CommandBase.__init__]
        @param defaults(dict[unicode, unicode]): help text for default value
            key can be "service" or "node"
            value will be set in " (DEFAULT: {value})", or can be None to remove DEFAULT
        @return (ArgumentParser): parser to add
        """
        flags = misc.FlagsHandler(flags)
        parent = argparse.ArgumentParser(add_help=False)
        pubsub_group = parent.add_argument_group('pubsub')
        pubsub_group.add_argument("-u", "--pubsub-url",
                                  help=_("Pubsub URL (xmpp or http)"))

        service_help = _("JID of the PubSub service")
        if not flags.service:
            default = defaults.pop('service', _('PEP service'))
            if default is not None:
                service_help += _(" (DEFAULT: {default})".format(default=default))
        pubsub_group.add_argument("-s", "--service", default='',
                                  help=service_help)

        node_help = _("node to request")
        if not flags.node:
            default = defaults.pop('node', _('standard node'))
            if default is not None:
                node_help += _(" (DEFAULT: {default})".format(default=default))
        pubsub_group.add_argument("-n", "--node", default='', help=node_help)

        if flags.single_item:
            item_help = ("item to retrieve")
            if not flags.item:
                default = defaults.pop('item', _('last item'))
                if default is not None:
                    item_help += _(" (DEFAULT: {default})".format(default=default))
            pubsub_group.add_argument("-i", "--item", default='',
                                      help=item_help)
            pubsub_group.add_argument(
                "-L", "--last-item", action='store_true', help=_('retrieve last item'))
        elif flags.multi_items:
            # mutiple items, this activate several features: max-items, RSM, MAM
            # and Orbder-by
            pubsub_group.add_argument(
                "-i", "--item", action='append', dest='items', default=[],
                help=_("items to retrieve (DEFAULT: all)"))
            if not flags.no_max:
                max_group = pubsub_group.add_mutually_exclusive_group()
                # XXX: defaut value for --max-items or --max is set in parse_pubsub_args
                max_group.add_argument(
                    "-M", "--max-items", dest="max", type=int,
                    help=_("maximum number of items to get ({no_limit} to get all items)"
                           .format(no_limit=C.NO_LIMIT)))
                # FIXME: it could be possible to no duplicate max (between pubsub
                #        max-items and RSM max)should not be duplicated, RSM could be
                #        used when available and pubsub max otherwise
                max_group.add_argument(
                    "-m", "--max", dest="rsm_max", type=int,
                    help=_("maximum number of items to get per page (DEFAULT: 10)"))

            # RSM

            rsm_page_group = pubsub_group.add_mutually_exclusive_group()
            rsm_page_group.add_argument(
                "-a", "--after", dest="rsm_after",
                help=_("find page after this item"), metavar='ITEM_ID')
            rsm_page_group.add_argument(
                "-b", "--before", dest="rsm_before",
                help=_("find page before this item"), metavar='ITEM_ID')
            rsm_page_group.add_argument(
                "--index", dest="rsm_index", type=int,
                help=_("index of the page to retrieve"))


            # MAM

            pubsub_group.add_argument(
                "-f", "--filter", dest='mam_filters', nargs=2,
                action='append', default=[], help=_("MAM filters to use"),
                metavar=("FILTER_NAME", "VALUE")
            )

            # Order-By

            # TODO: order-by should be a list to handle several levels of ordering
            #       but this is not yet done in SàT (and not really useful with
            #       current specifications, as only "creation" and "modification" are
            #       available)
            pubsub_group.add_argument(
                "-o", "--order-by", choices=[C.ORDER_BY_CREATION,
                                             C.ORDER_BY_MODIFICATION],
                help=_("how items should be ordered"))

        if not flags.all_used:
            raise exceptions.InternalError('unknown flags: {flags}'.format(
                flags=', '.join(flags.unused)))
        if defaults:
            raise exceptions.InternalError(f'unused defaults: {defaults}')

        return parent

    def add_parser_options(self):
        self.parser.add_argument(
            '--version',
            action='version',
            version=("{name} {version} {copyleft}".format(
                name = C.APP_NAME,
                version = self.version,
                copyleft = COPYLEFT))
        )

    def register_output(self, type_, name, callback, description="", default=False):
        if type_ not in C.OUTPUT_TYPES:
            log.error("Invalid output type {}".format(type_))
            return
        self._outputs[type_][name] = {'callback': callback,
                                      'description': description
                                     }
        if default:
            if type_ in self.default_output:
                self.disp(
                    _('there is already a default output for {type}, ignoring new one')
                    .format(type=type_)
                )
            else:
                self.default_output[type_] = name


    def parse_output_options(self):
        options = self.command.args.output_opts
        options_dict = {}
        for option in options:
            try:
                key, value = option.split('=', 1)
            except ValueError:
                key, value = option, None
            options_dict[key.strip()] = value.strip() if value is not None else None
        return options_dict

    def check_output_options(self, accepted_set, options):
        if not accepted_set.issuperset(options):
            self.disp(
                _("The following output options are invalid: {invalid_options}").format(
                invalid_options = ', '.join(set(options).difference(accepted_set))),
                error=True)
            self.quit(C.EXIT_BAD_ARG)

    def import_plugins(self):
        """Automaticaly import commands and outputs in jp

        looks from modules names cmd_*.py in jp path and import them
        """
        path = os.path.dirname(sat_frontends.jp.__file__)
        # XXX: outputs must be imported before commands as they are used for arguments
        for type_, pattern in ((C.PLUGIN_OUTPUT, 'output_*.py'),
                               (C.PLUGIN_CMD, 'cmd_*.py')):
            modules = (
                os.path.splitext(module)[0]
                for module in map(os.path.basename, iglob(os.path.join(path, pattern))))
            for module_name in modules:
                module_path = "sat_frontends.jp." + module_name
                try:
                    module = import_module(module_path)
                    self.import_plugin_module(module, type_)
                except ImportError as e:
                    self.disp(
                        _("Can't import {module_path} plugin, ignoring it: {e}")
                        .format(module_path=module_path, e=e),
                        error=True)
                except exceptions.CancelError:
                    continue
                except exceptions.MissingModule as e:
                    self.disp(_("Missing module for plugin {name}: {missing}".format(
                        name = module_path,
                        missing = e)), error=True)


    def import_plugin_module(self, module, type_):
        """add commands or outpus from a module to jp

        @param module: module containing commands or outputs
        @param type_(str): one of C_PLUGIN_*
        """
        try:
            class_names =  getattr(module, '__{}__'.format(type_))
        except AttributeError:
            log.disp(
                _("Invalid plugin module [{type}] {module}")
                .format(type=type_, module=module),
                error=True)
            raise ImportError
        else:
            for class_name in class_names:
                cls = getattr(module, class_name)
                cls(self)

    def get_xmpp_uri_from_http(self, http_url):
        """parse HTML page at http(s) URL, and looks for xmpp: uri"""
        if http_url.startswith('https'):
            scheme = 'https'
        elif http_url.startswith('http'):
            scheme = 'http'
        else:
            raise exceptions.InternalError('An HTTP scheme is expected in this method')
        self.disp(f"{scheme.upper()} URL found, trying to find associated xmpp: URI", 1)
        # HTTP URL, we try to find xmpp: links
        try:
            from lxml import etree
        except ImportError:
            self.disp(
                "lxml module must be installed to use http(s) scheme, please install it "
                "with \"pip install lxml\"",
                error=True)
            self.quit(1)
        import urllib.request, urllib.error, urllib.parse
        parser = etree.HTMLParser()
        try:
            root = etree.parse(urllib.request.urlopen(http_url), parser)
        except etree.XMLSyntaxError as e:
            self.disp(_("Can't parse HTML page : {msg}").format(msg=e))
            links = []
        else:
            links = root.xpath("//link[@rel='alternate' and starts-with(@href, 'xmpp:')]")
        if not links:
            self.disp(
                _('Could not find alternate "xmpp:" URI, can\'t find associated XMPP '
                  'PubSub node/item'),
                error=True)
            self.quit(1)
        xmpp_uri = links[0].get('href')
        return xmpp_uri

    def parse_pubsub_args(self):
        if self.args.pubsub_url is not None:
            url = self.args.pubsub_url

            if url.startswith('http'):
                # http(s) URL, we try to retrieve xmpp one from there
                url = self.get_xmpp_uri_from_http(url)

            try:
                uri_data = uri.parseXMPPUri(url)
            except ValueError:
                self.parser.error(_('invalid XMPP URL: {url}').format(url=url))
            else:
                if uri_data['type'] == 'pubsub':
                    # URL is alright, we only set data not already set by other options
                    if not self.args.service:
                        self.args.service = uri_data['path']
                    if not self.args.node:
                        self.args.node = uri_data['node']
                    uri_item = uri_data.get('item')
                    if uri_item:
                        # there is an item in URI
                        # we use it only if item is not already set
                        # and item_last is not used either
                        try:
                            item = self.args.item
                        except AttributeError:
                            try:
                                items = self.args.items
                            except AttributeError:
                                self.disp(
                                    _("item specified in URL but not needed in command, "
                                      "ignoring it"),
                                    error=True)
                            else:
                                if not items:
                                    self.args.items = [uri_item]
                        else:
                            if not item:
                                try:
                                    item_last = self.args.item_last
                                except AttributeError:
                                    item_last = False
                                if not item_last:
                                    self.args.item = uri_item
                else:
                    self.parser.error(
                        _('XMPP URL is not a pubsub one: {url}').format(url=url)
                    )
        flags = self.args._cmd._pubsub_flags
        # we check required arguments here instead of using add_arguments' required option
        # because the required argument can be set in URL
        if C.SERVICE in flags and not self.args.service:
            self.parser.error(_("argument -s/--service is required"))
        if C.NODE in flags and not self.args.node:
            self.parser.error(_("argument -n/--node is required"))
        if C.ITEM in flags and not self.args.item:
            self.parser.error(_("argument -i/--item is required"))

        # FIXME: mutually groups can't be nested in a group and don't support title
        #        so we check conflict here. This may be fixed in Python 3, to be checked
        try:
            if self.args.item and self.args.item_last:
                self.parser.error(
                    _("--item and --item-last can't be used at the same time"))
        except AttributeError:
            pass

        try:
            max_items = self.args.max
            rsm_max = self.args.rsm_max
        except AttributeError:
            pass
        else:
            # we need to set a default value for max, but we need to know if we want
            # to use pubsub's max or RSM's max. The later is used if any RSM or MAM
            # argument is set
            if max_items is None and rsm_max is None:
                to_check = ('mam_filters', 'rsm_max', 'rsm_after', 'rsm_before',
                            'rsm_index')
                if any((getattr(self.args, name) for name in to_check)):
                    # we use RSM
                    self.args.rsm_max = 10
                else:
                    # we use pubsub without RSM
                    self.args.max = 10
            if self.args.max is None:
                self.args.max = C.NO_LIMIT

    async def main(self, args, namespace):
        try:
            await self.bridge.bridgeConnect()
        except Exception as e:
            if isinstance(e, exceptions.BridgeExceptionNoService):
                print(_("Can't connect to SàT backend, are you sure it's launched ?"))
                self.quit(C.EXIT_BACKEND_NOT_FOUND, raise_exc=False)
            elif isinstance(e, exceptions.BridgeInitError):
                print(_("Can't init bridge"))
                self.quit(C.EXIT_BRIDGE_ERROR, raise_exc=False)
            else:
                print(
                    _("Error while initialising bridge: {e}").format(e=e)
                )
                self.quit(C.EXIT_BRIDGE_ERROR, raise_exc=False)
            return
        await self.bridge.getReady()
        self.version = await self.bridge.getVersion()
        self._bridgeConnected()
        self.import_plugins()
        try:
            self.args = self.parser.parse_args(args, namespace=None)
            if self.args._cmd._use_pubsub:
                self.parse_pubsub_args()
            await self.args._cmd.run()
        except SystemExit as e:
            self.quit(e.code, raise_exc=False)
            return
        except QuitException:
            return

    def _run(self, args=None, namespace=None):
        self.loop = JPLoop()
        self.loop.run(self, args, namespace)

    @classmethod
    def run(cls):
        cls()._run()

    def _read_stdin(self, stdin_fut):
        """Callback called by ainput to read stdin"""
        line = sys.stdin.readline()
        if line:
            stdin_fut.set_result(line.rstrip(os.linesep))
        else:
            stdin_fut.set_exception(EOFError())

    async def ainput(self, msg=''):
        """Asynchronous version of buildin "input" function"""
        self.disp(msg, end=' ')
        sys.stdout.flush()
        loop = asyncio.get_running_loop()
        stdin_fut = loop.create_future()
        loop.add_reader(sys.stdin, self._read_stdin, stdin_fut)
        return await stdin_fut

    async def confirm(self, message):
        """Request user to confirm action, return answer as boolean"""
        res = await self.ainput(f"{message} (y/N)? ")
        return res in ("y", "Y")

    async def confirmOrQuit(self, message, cancel_message=_("action cancelled by user")):
        """Request user to confirm action, and quit if he doesn't"""
        confirmed = await self.confirm(message)
        if not confirmed:
            self.disp(cancel_message)
            self.quit(C.EXIT_USER_CANCELLED)

    def quitFromSignal(self, exit_code=0):
        r"""Same as self.quit, but from a signal handler

        /!\: return must be used after calling this method !
        """
        # XXX: python-dbus will show a traceback if we exit in a signal handler
        # so we use this little timeout trick to avoid it
        self.loop.call_later(0, self.quit, exit_code)

    def quit(self, exit_code=0, raise_exc=True):
        """Terminate the execution with specified exit_code

        This will stop the loop.
        @param exit_code(int): code to return when quitting the program
        @param raise_exp(boolean): if True raise a QuitException to stop code execution
            The default value should be used most of time.
        """
        # first the onQuitCallbacks
        try:
            callbacks_list = self._onQuitCallbacks
        except AttributeError:
            pass
        else:
            for callback, args, kwargs in callbacks_list:
                callback(*args, **kwargs)

        self.loop.quit(exit_code)
        if raise_exc:
            raise QuitException

    async def check_jids(self, jids):
        """Check jids validity, transform roster name to corresponding jids

        @param profile: profile name
        @param jids: list of jids
        @return: List of jids

        """
        names2jid = {}
        nodes2jid = {}

        for contact in await self.bridge.getContacts(self.profile):
            jid_s, attr, groups = contact
            _jid = JID(jid_s)
            try:
                names2jid[attr["name"].lower()] = jid_s
            except KeyError:
                pass

            if _jid.node:
                nodes2jid[_jid.node.lower()] = jid_s

        def expand_jid(jid):
            _jid = jid.lower()
            if _jid in names2jid:
                expanded = names2jid[_jid]
            elif _jid in nodes2jid:
                expanded = nodes2jid[_jid]
            else:
                expanded = jid
            return expanded

        def check(jid):
            if not jid.is_valid:
                log.error (_("%s is not a valid JID !"), jid)
                self.quit(1)

        dest_jids=[]
        try:
            for i in range(len(jids)):
                dest_jids.append(expand_jid(jids[i]))
                check(dest_jids[i])
        except AttributeError:
            pass

        return dest_jids

    async def a_pwd_input(self, msg=''):
        """Like ainput but with echo disabled (useful for passwords)"""
        # we disable echo, code adapted from getpass standard module which has been
        # written by Piers Lauder (original), Guido van Rossum (Windows support and
        # cleanup) and Gregory P. Smith (tty support & GetPassWarning), a big thanks
        # to them (and for all the amazing work on Python).
        stdin_fd = sys.stdin.fileno()
        old = termios.tcgetattr(sys.stdin)
        new = old[:]
        new[3] &= ~termios.ECHO
        tcsetattr_flags = termios.TCSAFLUSH
        if hasattr(termios, 'TCSASOFT'):
            tcsetattr_flags |= termios.TCSASOFT
        try:
            termios.tcsetattr(stdin_fd, tcsetattr_flags, new)
            pwd = await self.ainput(msg=msg)
        finally:
            termios.tcsetattr(stdin_fd, tcsetattr_flags, old)
            sys.stderr.flush()
        self.disp('')
        return pwd

    async def connectOrPrompt(self, method, err_msg=None):
        """Try to connect/start profile session and prompt for password if needed

        @param method(callable): bridge method to either connect or start profile session
            It will be called with password as sole argument, use lambda to do the call
            properly
        @param err_msg(str): message to show if connection fail
        """
        password = self.args.pwd
        while True:
            try:
                await method(password or '')
            except Exception as e:
                if ((isinstance(e, BridgeException)
                     and e.classname == 'PasswordError'
                     and self.args.pwd is None)):
                    if password is not None:
                        self.disp(A.color(C.A_WARNING, _("invalid password")))
                    password = await self.a_pwd_input(
                        _("please enter profile password:"))
                else:
                    self.disp(err_msg.format(profile=self.profile, e=e), error=True)
                    self.quit(C.EXIT_ERROR)
            else:
                break

    async def connect_profile(self):
        """Check if the profile is connected and do it if requested

        @exit: - 1 when profile is not connected and --connect is not set
               - 1 when the profile doesn't exists
               - 1 when there is a connection error
        """
        # FIXME: need better exit codes

        self.profile = await self.bridge.profileNameGet(self.args.profile)

        if not self.profile:
            log.error(
                _("The profile [{profile}] doesn't exist")
                .format(profile=self.args.profile)
            )
            self.quit(C.EXIT_ERROR)

        try:
            start_session = self.args.start_session
        except AttributeError:
            pass
        else:
            if start_session:
                await self.connectOrPrompt(
                    lambda pwd: self.bridge.profileStartSession(pwd, self.profile),
                    err_msg="Can't start {profile}'s session: {e}"
                )
                return
            elif not await self.bridge.profileIsSessionStarted(self.profile):
                if not self.args.connect:
                    self.disp(_(
                        "Session for [{profile}] is not started, please start it "
                        "before using jp, or use either --start-session or --connect "
                        "option"
                        .format(profile=self.profile)
                    ), error=True)
                    self.quit(1)
            elif not getattr(self.args, "connect", False):
                return


        if not hasattr(self.args, 'connect'):
            # a profile can be present without connect option (e.g. on profile
            # creation/deletion)
            return
        elif self.args.connect is True:  # if connection is asked, we connect the profile
            await self.connectOrPrompt(
                lambda pwd: self.bridge.connect(self.profile, pwd, {}),
                err_msg = 'Can\'t connect profile "{profile!s}": {e}'
            )
            return
        else:
            if not await self.bridge.isConnected(self.profile):
                log.error(
                    _("Profile [{profile}] is not connected, please connect it "
                      "before using jp, or use --connect option")
                    .format(profile=self.profile)
                )
                self.quit(1)

    async def get_full_jid(self, param_jid):
        """Return the full jid if possible (add main resource when find a bare jid)"""
        # TODO: to be removed, bare jid should work with all commands, notably for file
        #   as backend now handle jingles message initiation
        _jid = JID(param_jid)
        if not _jid.resource:
            #if the resource is not given, we try to add the main resource
            main_resource = await self.bridge.getMainResource(param_jid, self.profile)
            if main_resource:
                return f"{_jid.bare}/{main_resource}"
        return param_jid


class CommandBase(object):

    def __init__(self, host, name, use_profile=True, use_output=False, extra_outputs=None,
                       need_connect=None, help=None, **kwargs):
        """Initialise CommandBase

        @param host: Jp instance
        @param name(unicode): name of the new command
        @param use_profile(bool): if True, add profile selection/connection commands
        @param use_output(bool, unicode): if not False, add --output option
        @param extra_outputs(dict): list of command specific outputs:
            key is output name ("default" to use as main output)
            value is a callable which will format the output (data will be used as only
            argument)
            if a key already exists with normal outputs, the extra one will be used
        @param need_connect(bool, None): True if profile connection is needed
            False else (profile session must still be started)
            None to set auto value (i.e. True if use_profile is set)
            Can't be set if use_profile is False
        @param help(unicode): help message to display
        @param **kwargs: args passed to ArgumentParser
            use_* are handled directly, they can be:
            - use_progress(bool): if True, add progress bar activation option
                progress* signals will be handled
            - use_verbose(bool): if True, add verbosity option
            - use_pubsub(bool): if True, add pubsub options
                mandatory arguments are controlled by pubsub_req
            - use_draft(bool): if True, add draft handling options
            ** other arguments **
            - pubsub_flags(iterable[unicode]): tuple of flags to set pubsub options,
              can be:
                C.SERVICE: service is required
                C.NODE: node is required
                C.ITEM: item is required
                C.SINGLE_ITEM: only one item is allowed
        """
        try: # If we have subcommands, host is a CommandBase and we need to use host.host
            self.host = host.host
        except AttributeError:
            self.host = host

        # --profile option
        parents = kwargs.setdefault('parents', set())
        if use_profile:
            # self.host.parents['profile'] is an ArgumentParser with profile connection
            # arguments
            if need_connect is None:
                need_connect = True
            parents.add(
                self.host.parents['profile' if need_connect else 'profile_session'])
        else:
            assert need_connect is None
        self.need_connect = need_connect
        # from this point, self.need_connect is None if connection is not needed at all
        # False if session starting is needed, and True if full connection is needed

        # --output option
        if use_output:
            if extra_outputs is None:
                extra_outputs = {}
            self.extra_outputs = extra_outputs
            if use_output == True:
                use_output = C.OUTPUT_TEXT
            assert use_output in C.OUTPUT_TYPES
            self._output_type = use_output
            output_parent = argparse.ArgumentParser(add_help=False)
            choices = set(self.host.getOutputChoices(use_output))
            choices.update(extra_outputs)
            if not choices:
                raise exceptions.InternalError(
                    "No choice found for {} output type".format(use_output))
            try:
                default = self.host.default_output[use_output]
            except KeyError:
                if 'default' in choices:
                    default = 'default'
                elif 'simple' in choices:
                    default = 'simple'
                else:
                    default = list(choices)[0]
            output_parent.add_argument(
                '--output', '-O', choices=sorted(choices), default=default,
                help=_("select output format (default: {})".format(default)))
            output_parent.add_argument(
                '--output-option', '--oo', action="append", dest='output_opts',
                default=[], help=_("output specific option"))
            parents.add(output_parent)
        else:
            assert extra_outputs is None

        self._use_pubsub = kwargs.pop('use_pubsub', False)
        if self._use_pubsub:
            flags = kwargs.pop('pubsub_flags', [])
            defaults = kwargs.pop('pubsub_defaults', {})
            parents.add(self.host.make_pubsub_group(flags, defaults))
            self._pubsub_flags = flags

        # other common options
        use_opts = {k:v for k,v in kwargs.items() if k.startswith('use_')}
        for param, do_use in use_opts.items():
            opt=param[4:] # if param is use_verbose, opt is verbose
            if opt not in self.host.parents:
                raise exceptions.InternalError("Unknown parent option {}".format(opt))
            del kwargs[param]
            if do_use:
                parents.add(self.host.parents[opt])

        self.parser = host.subparsers.add_parser(name, help=help, **kwargs)
        if hasattr(self, "subcommands"):
            self.subparsers = self.parser.add_subparsers(dest='subcommand', required=True)
        else:
            self.parser.set_defaults(_cmd=self)
        self.add_parser_options()

    @property
    def sat_conf(self):
        return self.host.sat_conf

    @property
    def args(self):
        return self.host.args

    @property
    def profile(self):
        return self.host.profile

    @property
    def verbosity(self):
        return self.host.verbosity

    @property
    def progress_id(self):
        return self.host.progress_id

    async def set_progress_id(self, progress_id):
        return await self.host.set_progress_id(progress_id)

    async def progressStartedHandler(self, uid, metadata, profile):
        if profile != self.profile:
            return
        if self.progress_id is None:
            # the progress started message can be received before the id
            # so we keep progressStarted signals in cache to replay they
            # when the progress_id is received
            cache_data = (self.progressStartedHandler, uid, metadata, profile)
            try:
                cache = self.host.progress_ids_cache
            except AttributeError:
                cache = self.host.progress_ids_cache = []
            cache.append(cache_data)
        else:
            if self.host.watch_progress and uid == self.progress_id:
                await self.onProgressStarted(metadata)
                while True:
                    await asyncio.sleep(PROGRESS_DELAY)
                    cont = await self.progressUpdate()
                    if not cont:
                        break

    async def progressFinishedHandler(self, uid, metadata, profile):
        if profile != self.profile:
            return
        if uid == self.progress_id:
            try:
                self.host.pbar.finish()
            except AttributeError:
                pass
            await self.onProgressFinished(metadata)
            if self.host.quit_on_progress_end:
                self.host.quitFromSignal()

    async def progressErrorHandler(self, uid, message, profile):
        if profile != self.profile:
            return
        if uid == self.progress_id:
            if self.args.progress:
                self.disp('') # progress is not finished, so we skip a line
            if self.host.quit_on_progress_end:
                await self.onProgressError(message)
                self.host.quitFromSignal(C.EXIT_ERROR)

    async def progressUpdate(self):
        """This method is continualy called to update the progress bar

        @return (bool): False to stop being called
        """
        data = await self.host.bridge.progressGet(self.progress_id, self.profile)
        if data:
            try:
                size = data['size']
            except KeyError:
                self.disp(_("file size is not known, we can't show a progress bar"), 1,
                          error=True)
                return False
            if self.host.pbar is None:
                #first answer, we must construct the bar

                # if the instance has a pbar_template attribute, it is used has model,
                # else default one is used
                # template is a list of part, where part can be either a str to show directly
                # or a list where first argument is a name of a progressbar widget, and others
                # are used as widget arguments
                try:
                    template = self.pbar_template
                except AttributeError:
                    template = [
                        _("Progress: "), ["Percentage"], " ", ["Bar"], " ",
                        ["FileTransferSpeed"], " ", ["ETA"]
                    ]

                widgets = []
                for part in template:
                    if isinstance(part, str):
                        widgets.append(part)
                    else:
                        widget = getattr(progressbar, part.pop(0))
                        widgets.append(widget(*part))

                self.host.pbar = progressbar.ProgressBar(max_value=int(size), widgets=widgets)
                self.host.pbar.start()

            self.host.pbar.update(int(data['position']))

        elif self.host.pbar is not None:
            return False

        await self.onProgressUpdate(data)

        return True

    async def onProgressStarted(self, metadata):
        """Called when progress has just started

        can be overidden by a command
        @param metadata(dict): metadata as sent by bridge.progressStarted
        """
        self.disp(_("Operation started"), 2)

    async def onProgressUpdate(self, metadata):
        """Method called on each progress updata

        can be overidden by a command to handle progress metadata
        @para metadata(dict): metadata as returned by bridge.progressGet
        """
        pass

    async def onProgressFinished(self, metadata):
        """Called when progress has just finished

        can be overidden by a command
        @param metadata(dict): metadata as sent by bridge.progressFinished
        """
        self.disp(_("Operation successfully finished"), 2)

    async def onProgressError(self, e):
        """Called when a progress failed

        @param error_msg(unicode): error message as sent by bridge.progressError
        """
        self.disp(_("Error while doing operation: {e}").format(e=e), error=True)

    def disp(self, msg, verbosity=0, error=False, end='\n'):
        return self.host.disp(msg, verbosity, error, end)

    def output(self, data):
        try:
            output_type = self._output_type
        except AttributeError:
            raise exceptions.InternalError(
                _('trying to use output when use_output has not been set'))
        return self.host.output(output_type, self.args.output, self.extra_outputs, data)

    def getPubsubExtra(self, extra=None):
        """Helper method to compute extra data from pubsub arguments

        @param extra(None, dict): base extra dict, or None to generate a new one
        @return (dict): dict which can be used directly in the bridge for pubsub
        """
        if extra is None:
            extra = {}
        else:
            intersection = {C.KEY_ORDER_BY}.intersection(list(extra.keys()))
            if intersection:
                raise exceptions.ConflictError(
                    "given extra dict has conflicting keys with pubsub keys "
                    "{intersection}".format(intersection=intersection))

        # RSM

        for attribute in ('max', 'after', 'before', 'index'):
            key = 'rsm_' + attribute
            if key in extra:
                raise exceptions.ConflictError(
                    "This key already exists in extra: u{key}".format(key=key))
            value = getattr(self.args, key, None)
            if value is not None:
                extra[key] = str(value)

        # MAM

        if hasattr(self.args, 'mam_filters'):
            for key, value in self.args.mam_filters:
                key = 'filter_' + key
                if key in extra:
                    raise exceptions.ConflictError(
                        "This key already exists in extra: u{key}".format(key=key))
                extra[key] = value

        # Order-By

        try:
            order_by = self.args.order_by
        except AttributeError:
            pass
        else:
            if order_by is not None:
                extra[C.KEY_ORDER_BY] = self.args.order_by
        return extra

    def add_parser_options(self):
        try:
            subcommands = self.subcommands
        except AttributeError:
            # We don't have subcommands, the class need to implements add_parser_options
            raise NotImplementedError

        # now we add subcommands to ourself
        for cls in subcommands:
            cls(self)

    async def run(self):
        """this method is called when a command is actually run

        It set stuff like progression callbacks and profile connection
        You should not overide this method: you should call self.start instead
        """
        # we keep a reference to run command, it may be useful e.g. for outputs
        self.host.command = self

        try:
            show_progress = self.args.progress
        except AttributeError:
            # the command doesn't use progress bar
            pass
        else:
            if show_progress:
                self.host.watch_progress = True
            # we need to register the following signal even if we don't display the
            # progress bar
            self.host.bridge.register_signal(
                "progressStarted", self.progressStartedHandler)
            self.host.bridge.register_signal(
                "progressFinished", self.progressFinishedHandler)
            self.host.bridge.register_signal(
                "progressError", self.progressErrorHandler)

        if self.need_connect is not None:
            await self.host.connect_profile()
        await self.start()

    async def start(self):
        """This is the starting point of the command, this method must be overriden

        at this point, profile are connected if needed
        """
        raise NotImplementedError


class CommandAnswering(CommandBase):
    """Specialised commands which answer to specific actions

    to manage action_types answer,
    """
    action_callbacks = {} # XXX: set managed action types in a dict here:
                          # key is the action_type, value is the callable
                          # which will manage the answer. profile filtering is
                          # already managed when callback is called

    def __init__(self, *args, **kwargs):
        super(CommandAnswering, self).__init__(*args, **kwargs)

    async def onActionNew(self, action_data, action_id, security_limit, profile):
        if profile != self.profile:
            return
        try:
            action_type = action_data['meta_type']
        except KeyError:
            try:
                xml_ui = action_data["xmlui"]
            except KeyError:
                pass
            else:
                self.onXMLUI(xml_ui)
        else:
            try:
                callback = self.action_callbacks[action_type]
            except KeyError:
                pass
            else:
                await callback(action_data, action_id, security_limit, profile)

    def onXMLUI(self, xml_ui):
        """Display a dialog received from the backend.

        @param xml_ui (unicode): dialog XML representation
        """
        # FIXME: we temporarily use ElementTree, but a real XMLUI managing module
        #        should be available in the future
        # TODO: XMLUI module
        ui = ET.fromstring(xml_ui.encode('utf-8'))
        dialog = ui.find("dialog")
        if dialog is not None:
            self.disp(dialog.findtext("message"), error=dialog.get("level") == "error")

    async def start_answering(self):
        """Auto reply to confirmation requests"""
        self.host.bridge.register_signal("actionNew", self.onActionNew)
        actions = await self.host.bridge.actionsGet(self.profile)
        for action_data, action_id, security_limit in actions:
            await self.onActionNew(action_data, action_id, security_limit, self.profile)
