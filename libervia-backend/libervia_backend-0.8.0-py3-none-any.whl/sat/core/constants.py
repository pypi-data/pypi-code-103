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

try:
    from xdg import BaseDirectory
    from os.path import expanduser, realpath
except ImportError:
    BaseDirectory = None
from os.path import dirname
import sat


class Const(object):

    ## Application ##
    APP_NAME = "Libervia"
    APP_COMPONENT = "backend"
    APP_NAME_ALT = "SàT"
    APP_NAME_FILE = "libervia"
    APP_NAME_FULL = f"{APP_NAME} ({APP_COMPONENT})"
    APP_VERSION = (
        sat.__version__
    )  # Please add 'D' at the end of version in sat/VERSION for dev versions
    APP_RELEASE_NAME = "La Cecília"
    APP_URL = "https://salut-a-toi.org"

    ## Runtime ##
    PLUGIN_EXT = "py"
    HISTORY_SKIP = "skip"

    ## Main config ##
    DEFAULT_BRIDGE = "dbus"

    ## Protocol ##
    XMPP_C2S_PORT = 5222
    XMPP_MAX_RETRIES = None
    # default port used on Prosody, may differ on other servers
    XMPP_COMPONENT_PORT = 5347

    ## Parameters ##
    NO_SECURITY_LIMIT = -1  #  FIXME: to rename
    SECURITY_LIMIT_MAX = 0
    INDIVIDUAL = "individual"
    GENERAL = "general"
    # General parameters
    HISTORY_LIMIT = "History"
    SHOW_OFFLINE_CONTACTS = "Offline contacts"
    SHOW_EMPTY_GROUPS = "Empty groups"
    # Parameters related to connection
    FORCE_SERVER_PARAM = "Force server"
    FORCE_PORT_PARAM = "Force port"
    # Parameters related to encryption
    PROFILE_PASS_PATH = ("General", "Password")
    MEMORY_CRYPTO_NAMESPACE = "crypto"  # for the private persistent binary dict
    MEMORY_CRYPTO_KEY = "personal_key"
    # Parameters for static blog pages
    # FIXME: blog constants should not be in core constants
    STATIC_BLOG_KEY = "Blog page"
    STATIC_BLOG_PARAM_TITLE = "Title"
    STATIC_BLOG_PARAM_BANNER = "Banner"
    STATIC_BLOG_PARAM_KEYWORDS = "Keywords"
    STATIC_BLOG_PARAM_DESCRIPTION = "Description"

    ## Menus ##
    MENU_GLOBAL = "GLOBAL"
    MENU_ROOM = "ROOM"
    MENU_SINGLE = "SINGLE"
    MENU_JID_CONTEXT = "JID_CONTEXT"
    MENU_ROSTER_JID_CONTEXT = "ROSTER_JID_CONTEXT"
    MENU_ROSTER_GROUP_CONTEXT = "MENU_ROSTER_GROUP_CONTEXT"
    MENU_ROOM_OCCUPANT_CONTEXT = "MENU_ROOM_OCCUPANT_CONTEXT"

    ## Profile and entities ##
    PROF_KEY_NONE = "@NONE@"
    PROF_KEY_DEFAULT = "@DEFAULT@"
    PROF_KEY_ALL = "@ALL@"
    ENTITY_ALL = "@ALL@"
    ENTITY_ALL_RESOURCES = "@ALL_RESOURCES@"
    ENTITY_MAIN_RESOURCE = "@MAIN_RESOURCE@"
    ENTITY_CAP_HASH = "CAP_HASH"
    ENTITY_TYPE = "type"
    ENTITY_TYPE_MUC = "MUC"

    ## Roster jids selection ##
    PUBLIC = "PUBLIC"
    ALL = (
        "ALL"
    )  # ALL means all known contacts, while PUBLIC means everybody, known or not
    GROUP = "GROUP"
    JID = "JID"

    ## Messages ##
    MESS_TYPE_INFO = "info"
    MESS_TYPE_CHAT = "chat"
    MESS_TYPE_ERROR = "error"
    MESS_TYPE_GROUPCHAT = "groupchat"
    MESS_TYPE_HEADLINE = "headline"
    MESS_TYPE_NORMAL = "normal"
    MESS_TYPE_AUTO = "auto"  # magic value to let the backend guess the type
    MESS_TYPE_STANDARD = (
        MESS_TYPE_CHAT,
        MESS_TYPE_ERROR,
        MESS_TYPE_GROUPCHAT,
        MESS_TYPE_HEADLINE,
        MESS_TYPE_NORMAL,
    )
    MESS_TYPE_ALL = MESS_TYPE_STANDARD + (MESS_TYPE_INFO, MESS_TYPE_AUTO)

    MESS_EXTRA_INFO = "info_type"
    EXTRA_INFO_DECR_ERR = "DECRYPTION_ERROR"
    EXTRA_INFO_ENCR_ERR = "ENCRYPTION_ERROR"

    # encryption is a key for plugins
    MESS_KEY_ENCRYPTION = "ENCRYPTION"
    # encrypted is a key for frontends
    MESS_KEY_ENCRYPTED = "encrypted"
    MESS_KEY_TRUSTED = "trusted"

    MESS_KEY_ATTACHMENTS = "attachments"
    MESS_KEY_ATTACHMENTS_MEDIA_TYPE = "media_type"
    MESS_KEY_ATTACHMENTS_PREVIEW = "preview"
    MESS_KEY_ATTACHMENTS_RESIZE = "resize"

    # File encryption algorithms
    ENC_AES_GCM = "AES-GCM"

    ## Chat ##
    CHAT_ONE2ONE = "one2one"
    CHAT_GROUP = "group"

    ## Presence ##
    PRESENCE_UNAVAILABLE = "unavailable"
    PRESENCE_SHOW_AWAY = "away"
    PRESENCE_SHOW_CHAT = "chat"
    PRESENCE_SHOW_DND = "dnd"
    PRESENCE_SHOW_XA = "xa"
    PRESENCE_SHOW = "show"
    PRESENCE_STATUSES = "statuses"
    PRESENCE_STATUSES_DEFAULT = "default"
    PRESENCE_PRIORITY = "priority"

    ## Common namespaces ##
    NS_XML = "http://www.w3.org/XML/1998/namespace"
    NS_CLIENT = "jabber:client"
    NS_FORWARD = "urn:xmpp:forward:0"
    NS_DELAY = "urn:xmpp:delay"
    NS_XHTML = "http://www.w3.org/1999/xhtml"

    ## Common XPath ##

    IQ_GET = '/iq[@type="get"]'
    IQ_SET = '/iq[@type="set"]'

    ## Directories ##

    # directory for components specific data
    COMPONENTS_DIR = "components"
    CACHE_DIR = "cache"
    # files in file dir are stored for long term
    # files dir is global, i.e. for all profiles
    FILES_DIR = "files"
    # FILES_LINKS_DIR is a directory where files owned by a specific profile
    # are linked to the global files directory. This way the directory can be
    #  shared per profiles while keeping global directory where identical files
    # shared between different profiles are not duplicated.
    FILES_LINKS_DIR = "files_links"
    # FILES_TMP_DIR is where profile's partially transfered files are put.
    # Once transfer is completed, they are moved to FILES_DIR
    FILES_TMP_DIR = "files_tmp"

    ## Templates ##
    TEMPLATE_TPL_DIR = "templates"
    TEMPLATE_THEME_DEFAULT = "default"
    TEMPLATE_STATIC_DIR = "static"
    # templates i18n
    KEY_LANG = "lang"
    KEY_THEME = "theme"

    ## Plugins ##

    # PLUGIN_INFO keys
    # XXX: we use PI instead of PLUG_INFO which would normally be used
    #      to make the header more readable
    PI_NAME = "name"
    PI_IMPORT_NAME = "import_name"
    PI_MAIN = "main"
    PI_HANDLER = "handler"
    PI_TYPE = (
        "type"
    )  #  FIXME: should be types, and should handle single unicode type or tuple of types (e.g. "blog" and "import")
    PI_MODES = "modes"
    PI_PROTOCOLS = "protocols"
    PI_DEPENDENCIES = "dependencies"
    PI_RECOMMENDATIONS = "recommendations"
    PI_DESCRIPTION = "description"
    PI_USAGE = "usage"

    # Types
    PLUG_TYPE_XEP = "XEP"
    PLUG_TYPE_MISC = "MISC"
    PLUG_TYPE_EXP = "EXP"
    PLUG_TYPE_SEC = "SEC"
    PLUG_TYPE_SYNTAXE = "SYNTAXE"
    PLUG_TYPE_BLOG = "BLOG"
    PLUG_TYPE_IMPORT = "IMPORT"
    PLUG_TYPE_ENTRY_POINT = "ENTRY_POINT"

    # Modes
    PLUG_MODE_CLIENT = "client"
    PLUG_MODE_COMPONENT = "component"
    PLUG_MODE_DEFAULT = (PLUG_MODE_CLIENT,)
    PLUG_MODE_BOTH = (PLUG_MODE_CLIENT, PLUG_MODE_COMPONENT)

    # names of widely used plugins
    TEXT_CMDS = "TEXT-COMMANDS"

    # PubSub event categories
    PS_PEP = "PEP"
    PS_MICROBLOG = "MICROBLOG"

    # PubSub
    PS_PUBLISH = "publish"
    PS_RETRACT = "retract"  # used for items
    PS_DELETE = "delete"  # used for nodes
    PS_ITEM = "item"
    PS_ITEMS = "items"  # Can contain publish and retract items
    PS_EVENTS = (PS_ITEMS, PS_DELETE)

    ## MESSAGE/NOTIFICATION LEVELS ##

    LVL_INFO = "info"
    LVL_WARNING = "warning"
    LVL_ERROR = "error"

    ## XMLUI ##
    XMLUI_WINDOW = "window"
    XMLUI_POPUP = "popup"
    XMLUI_FORM = "form"
    XMLUI_PARAM = "param"
    XMLUI_DIALOG = "dialog"
    XMLUI_DIALOG_CONFIRM = "confirm"
    XMLUI_DIALOG_MESSAGE = "message"
    XMLUI_DIALOG_NOTE = "note"
    XMLUI_DIALOG_FILE = "file"
    XMLUI_DATA_ANSWER = "answer"
    XMLUI_DATA_CANCELLED = "cancelled"
    XMLUI_DATA_TYPE = "type"
    XMLUI_DATA_MESS = "message"
    XMLUI_DATA_LVL = "level"
    XMLUI_DATA_LVL_INFO = LVL_INFO
    XMLUI_DATA_LVL_WARNING = LVL_WARNING
    XMLUI_DATA_LVL_ERROR = LVL_ERROR
    XMLUI_DATA_LVL_DEFAULT = XMLUI_DATA_LVL_INFO
    XMLUI_DATA_LVLS = (XMLUI_DATA_LVL_INFO, XMLUI_DATA_LVL_WARNING, XMLUI_DATA_LVL_ERROR)
    XMLUI_DATA_BTNS_SET = "buttons_set"
    XMLUI_DATA_BTNS_SET_OKCANCEL = "ok/cancel"
    XMLUI_DATA_BTNS_SET_YESNO = "yes/no"
    XMLUI_DATA_BTNS_SET_DEFAULT = XMLUI_DATA_BTNS_SET_OKCANCEL
    XMLUI_DATA_FILETYPE = "filetype"
    XMLUI_DATA_FILETYPE_FILE = "file"
    XMLUI_DATA_FILETYPE_DIR = "dir"
    XMLUI_DATA_FILETYPE_DEFAULT = XMLUI_DATA_FILETYPE_FILE

    ## Logging ##
    LOG_LVL_DEBUG = "DEBUG"
    LOG_LVL_INFO = "INFO"
    LOG_LVL_WARNING = "WARNING"
    LOG_LVL_ERROR = "ERROR"
    LOG_LVL_CRITICAL = "CRITICAL"
    LOG_LEVELS = (
        LOG_LVL_DEBUG,
        LOG_LVL_INFO,
        LOG_LVL_WARNING,
        LOG_LVL_ERROR,
        LOG_LVL_CRITICAL,
    )
    LOG_BACKEND_STANDARD = "standard"
    LOG_BACKEND_TWISTED = "twisted"
    LOG_BACKEND_BASIC = "basic"
    LOG_BACKEND_CUSTOM = "custom"
    LOG_BASE_LOGGER = "root"
    LOG_TWISTED_LOGGER = "twisted"
    LOG_OPT_SECTION = "DEFAULT"  # section of sat.conf where log options should be
    LOG_OPT_PREFIX = "log_"
    # (option_name, default_value) tuples
    LOG_OPT_COLORS = (
        "colors",
        "true",
    )  # true for auto colors, force to have colors even if stdout is not a tty, false for no color
    LOG_OPT_TAINTS_DICT = (
        "levels_taints_dict",
        {
            LOG_LVL_DEBUG: ("cyan",),
            LOG_LVL_INFO: (),
            LOG_LVL_WARNING: ("yellow",),
            LOG_LVL_ERROR: ("red", "blink", r"/!\ ", "blink_off"),
            LOG_LVL_CRITICAL: ("bold", "red", "Guru Meditation ", "normal_weight"),
        },
    )
    LOG_OPT_LEVEL = ("level", "info")
    LOG_OPT_FORMAT = ("fmt", "%(message)s")  # similar to logging format.
    LOG_OPT_LOGGER = ("logger", "")  # regex to filter logger name
    LOG_OPT_OUTPUT_SEP = "//"
    LOG_OPT_OUTPUT_DEFAULT = "default"
    LOG_OPT_OUTPUT_MEMORY = "memory"
    LOG_OPT_OUTPUT_MEMORY_LIMIT = 300
    LOG_OPT_OUTPUT_FILE = "file"  # file is implicit if only output
    LOG_OPT_OUTPUT = (
        "output",
        LOG_OPT_OUTPUT_SEP + LOG_OPT_OUTPUT_DEFAULT,
    )  # //default = normal output (stderr or a file with twistd), path/to/file for a file (must be the first if used), //memory for memory (options can be put in parenthesis, e.g.: //memory(500) for a 500 lines memory)

    ## action constants ##
    META_TYPE_FILE = "file"
    META_TYPE_OVERWRITE = "overwrite"
    META_TYPE_NOT_IN_ROSTER_LEAK = "not_in_roster_leak"

    ## HARD-CODED ACTIONS IDS (generated with uuid.uuid4) ##
    AUTHENTICATE_PROFILE_ID = "b03bbfa8-a4ae-4734-a248-06ce6c7cf562"
    CHANGE_XMPP_PASSWD_ID = "878b9387-de2b-413b-950f-e424a147bcd0"

    ## Text values ##
    BOOL_TRUE = "true"
    BOOL_FALSE = "false"

    ## Special values used in bridge methods calls ##
    HISTORY_LIMIT_DEFAULT = -1
    HISTORY_LIMIT_NONE = -2

    ## Progress error special values ##
    PROGRESS_ERROR_DECLINED = "declined"  #  session has been declined by peer user
    PROGRESS_ERROR_FAILED = "failed"  #  something went wrong with the session

    ## Files ##
    FILE_TYPE_DIRECTORY = "directory"
    FILE_TYPE_FILE = "file"
    # when filename can't be found automatically, this one will be used
    FILE_DEFAULT_NAME = "unnamed"

    ## Permissions management ##
    ACCESS_PERM_READ = "read"
    ACCESS_PERM_WRITE = "write"
    ACCESS_PERMS = {ACCESS_PERM_READ, ACCESS_PERM_WRITE}
    ACCESS_TYPE_PUBLIC = "public"
    ACCESS_TYPE_WHITELIST = "whitelist"
    ACCESS_TYPES = (ACCESS_TYPE_PUBLIC, ACCESS_TYPE_WHITELIST)

    ## Common data keys ##
    KEY_THUMBNAILS = "thumbnails"
    KEY_PROGRESS_ID = "progress_id"

    ## Common extra keys/values ##
    KEY_ORDER_BY = "order_by"

    ORDER_BY_CREATION = 'creation'
    ORDER_BY_MODIFICATION = 'modification'

    # internationalisation
    DEFAULT_LOCALE = "en_GB"

    ## Command Line ##

    # Exit codes used by CLI applications
    EXIT_OK = 0
    EXIT_ERROR = 1  # generic error, when nothing else match
    EXIT_BAD_ARG = 2  # arguments given by user are bad
    EXIT_BRIDGE_ERROR = 3  # can't connect to bridge
    EXIT_BRIDGE_ERRBACK = 4  # something went wrong when calling a bridge method
    EXIT_BACKEND_NOT_FOUND = 5  # can't find backend with this bride
    EXIT_NOT_FOUND = 16  # an item required by a command was not found
    EXIT_DATA_ERROR = 17  # data needed for a command is invalid
    EXIT_MISSING_FEATURE = 18  # a needed plugin or feature is not available
    EXIT_CONFLICT = 19  # an item already exists
    EXIT_USER_CANCELLED = 20  # user cancelled action
    EXIT_INTERNAL_ERROR = 111  # unexpected error
    EXIT_FILE_NOT_EXE = (
        126
    )  # a file to be executed was found, but it was not an executable utility (cf. man 1 exit)
    EXIT_CMD_NOT_FOUND = 127  # a utility to be executed was not found (cf. man 1 exit)
    EXIT_CMD_ERROR = 127  # a utility to be executed returned an error exit code
    EXIT_SIGNAL_INT = 128  # a command was interrupted by a signal (cf. man 1 exit)

    ## Misc ##
    SAVEFILE_DATABASE = APP_NAME_FILE + ".db"
    IQ_SET = '/iq[@type="set"]'
    ENV_PREFIX = "SAT_"  # Prefix used for environment variables
    IGNORE = "ignore"
    NO_LIMIT = -1  # used in bridge when a integer value is expected
    DEFAULT_MAX_AGE = 1209600  # default max age of cached files, in seconds
    STANZA_NAMES = ("iq", "message", "presence")

    # Stream Hooks
    STREAM_HOOK_SEND = "send"
    STREAM_HOOK_RECEIVE = "receive"

    @classmethod
    def LOG_OPTIONS(cls):
        """Return options checked for logs"""
        # XXX: we use a classmethod so we can use Const inheritance to change default options
        return (
            cls.LOG_OPT_COLORS,
            cls.LOG_OPT_TAINTS_DICT,
            cls.LOG_OPT_LEVEL,
            cls.LOG_OPT_FORMAT,
            cls.LOG_OPT_LOGGER,
            cls.LOG_OPT_OUTPUT,
        )

    @classmethod
    def bool(cls, value):
        """@return (bool): bool value for associated constant"""
        assert isinstance(value, str)
        return value.lower() in (cls.BOOL_TRUE, "1", "yes", "on")

    @classmethod
    def boolConst(cls, value):
        """@return (str): constant associated to bool value"""
        assert isinstance(value, bool)
        return cls.BOOL_TRUE if value else cls.BOOL_FALSE



## Configuration ##
if (
    BaseDirectory
):  # skipped when xdg module is not available (should not happen in backend)
    if "org.libervia.cagou" in BaseDirectory.__file__:
        # FIXME: hack to make config read from the right location on Android
        # TODO: fix it in a more proper way

        # we need to use Android API to get downloads directory
        import os.path
        from jnius import autoclass

        # we don't want the very verbose jnius log when we are in DEBUG level
        import logging
        logging.getLogger('jnius').setLevel(logging.WARNING)
        logging.getLogger('jnius.reflect').setLevel(logging.WARNING)

        Environment = autoclass("android.os.Environment")

        BaseDirectory = None
        Const.DEFAULT_CONFIG = {
            "local_dir": "/data/data/org.libervia.cagou/app",
            "media_dir": "/data/data/org.libervia.cagou/files/app/media",
            # FIXME: temporary location for downloads, need to call API properly
            "downloads_dir": os.path.join(
                Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS
                ).getAbsolutePath(),
                Const.APP_NAME_FILE,
            ),
            "pid_dir": "%(local_dir)s",
            "log_dir": "%(local_dir)s",
        }
        Const.CONFIG_FILES = [
            "/data/data/org.libervia.cagou/files/app/android/"
            + Const.APP_NAME_FILE
            + ".conf"
        ]
    else:
        import os
        # we use parent of "sat" module dir as last config path, this is useful for
        # per instance configurations (e.g. a dev instance and a main instance)
        root_dir = dirname(dirname(sat.__file__)) + '/'
        Const.CONFIG_PATHS = (
            # /etc/_sat.conf is used for system-related settings (e.g. when media_dir
            # is set by the distribution and has not reason to change, or in a Docker
            # image)
            ["/etc/_", "/etc/", "~/", "~/."]
            + [
                "{}/".format(path)
                for path in list(BaseDirectory.load_config_paths(Const.APP_NAME_FILE))
            ]
            # this is to handle legacy sat.conf
            + [
                "{}/".format(path)
                for path in list(BaseDirectory.load_config_paths("sat"))
            ]
            + [root_dir]
        )

        # on recent versions of Flatpak, FLATPAK_ID is set at run time
        # it seems that this is not the case on older versions,
        # but FLATPAK_SANDBOX_DIR seems set then
        if os.getenv('FLATPAK_ID') or os.getenv('FLATPAK_SANDBOX_DIR'):
            # for Flatpak, the conf can't be set in /etc or $HOME, so we have
            # to add /app
            Const.CONFIG_PATHS.append('/app/')

        ## Configuration ##
        Const.DEFAULT_CONFIG = {
            "media_dir": "/usr/share/" + Const.APP_NAME_FILE + "/media",
            "local_dir": BaseDirectory.save_data_path(Const.APP_NAME_FILE),
            "downloads_dir": "~/Downloads/" + Const.APP_NAME_FILE,
            "pid_dir": "%(local_dir)s",
            "log_dir": "%(local_dir)s",
        }

        # List of the configuration filenames sorted by ascending priority
        Const.CONFIG_FILES = [
            realpath(expanduser(path) + Const.APP_NAME_FILE + ".conf")
            for path in Const.CONFIG_PATHS
        ] + [
            # legacy sat.conf
            realpath(expanduser(path) + "sat.conf")
            for path in Const.CONFIG_PATHS
        ]

