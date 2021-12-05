import yaml
from datetime import timedelta
from pathlib import Path

from .util import join_nonempty

################################################################################
# Config system base classes

class ConfigError(Exception):
    pass


class ClassdataStrMixin:
    def __str__(self):
        return '\n'.join(self._get_str_lines())

    def _get_dict_for_str(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith('_')}

    def _get_str_lines(self, indent=0):
        for k, v in self._get_dict_for_str().items():
            get_child = getattr(v, '_get_str_lines', None)
            if get_child:
                yield '{}{}:'.format(' '*indent, k)
                yield from get_child(indent+2)
            else:
                if isinstance(v, str):
                    v = repr(v)
                yield '{}{}: {}'.format(' '*indent, k, v)


NODEFAULT = object()

class CfgBase(ClassdataStrMixin):
    def __init__(self, data):
        self._data = data
        self._populate()

    def _populate(self):
        pass

    def subkeyname(self, name):
        return join_nonempty('.', self.keyname, name)

    def cfg_get(self, key, defaultdata=NODEFAULT, default=NODEFAULT, cls=None):
        """Get an entry from the config data

        Parameters:
        key         name of the entry to get
        default     default value to return directly if key is not set
        cls         optional class or callable to invoke with data and return result
        defaultdata default data to pass to cls

        default and defaultdata are mutually exclusive.
        defaultdata is only valid if cls is given.
        """
        try:
            value = self._data[key]
        except KeyError:
            if defaultdata is NODEFAULT and default is NODEFAULT:
                raise ConfigError("Missing key: {!r}".format(self.subkeyname(key)))

            if default is not NODEFAULT:
                assert defaultdata is NODEFAULT
                return default

            # Makes no sense to pass defaultdata but not cls
            assert cls is not None
            value = defaultdata

        if cls and value is not None:
            # Ensure unprocessed input data is of the expected type
            exp_type = cls.data_type
            if not isinstance(value, exp_type):
                self.invalid_type(key, value, exp_type)
            value = cls(data=value, name=key, parentnode=self)

        return value

    def cfg_get_path(self, key, default=NODEFAULT):
        """Get a path entry from the config data

        Parameters:
        key     name of the entry to get
        """
        val = self.cfg_get(key, default=default)
        if val is None:
            return None

        p = Path(val)

        if not p.is_absolute():
            # If the path is relative, it is taken relative to the
            # directory containing the config file
            p = self.cfgpath.parent / p

        return p.resolve()

    def raise_for_key(self, key, message):
        """Raise a ConfigError for the given sub-key"""
        raise ConfigError("{}: {}".format(self.subkeyname(key), message))

    def invalid_type(self, key, value, exp=None):
        msg = "Invalid type: {}".format(type(value).__name__)
        if exp:
            if isinstance(exp, tuple):
                expstr = '{' + ', '.join(t.__name__ for t in exp) + '}'
            elif isinstance(exp, type):
                expstr = exp.__name__
            else:
                assert False
            msg += "  Expected: {}".format(expstr)
        self.raise_for_key(key, msg)


class CfgRoot(CfgBase):
    def __init__(self, data, cfgpath):
        self._cfgpath = cfgpath
        super().__init__(data)

    @property
    def cfgpath(self):
        return self._cfgpath

    @property
    def keyname(self):
        return ''


class CfgNode(CfgBase):
    data_type = dict

    def __init__(self, data, name, parentnode):
        assert name != None
        self._name = name
        assert parentnode != None
        self._parentnode = parentnode

        super().__init__(data)

    @property
    def cfgpath(self):
        return self._parentnode.cfgpath

    @property
    def keyname(self):
        return join_nonempty('.', self._parentnode.keyname, self._name)


class CfgDict(CfgNode, dict):
    def _get_dict_for_str(self):
        return self


class CfgList(CfgNode, list):
    data_type = list

    def _get_str_lines(self, indent=0):
        for i, v in enumerate(self):
            k = '[{}]'.format(i)
            get_child = getattr(v, '_get_str_lines', None)
            if get_child:
                yield '{}{}:'.format(' '*indent, k)
                yield from get_child(indent+2)
            else:
                yield '{}{}: {!r}'.format(' '*indent, k, v)


class DurationConfig:
    data_type = str

    def __init__(self, data, name, parentnode):
        assert isinstance(data, str)
        self.__orig_str = data

        try:
            self.dt = self.parse(data)
        except ValueError as e:
            parentnode.raise_for_key(name, str(e))

    @staticmethod
    def parse(s):
        parts = s.split()
        if len(parts) != 2:
            raise ValueError("Invalid duration (too many words): {}".format(parts))

        n = int(parts[0])
        units = parts[1].lower().rstrip('s')

        mul = {
            'second':   1,
            'minute':   60,
            'hour':     60 * 60,
            'day':      60 * 60 * 24,
            'week':     60 * 60 * 24 * 7,
            'year':     60 * 60 * 24 * 365,
        }.get(units)
        if mul is None:
            raise ValueError("Invalid units: {}".format(units))

        return timedelta(seconds=n*mul)

    def __str__(self):
        return self.__orig_str


################################################################################
# adman config

class LdapAuthConfigFactory(type):
    def __call__(cls, data, name, parentnode, **kwargs):
        if cls is not LdapAuthConfig:
            return type.__call__(cls, data=data, name=name, parentnode=parentnode, **kwargs)

        # Factory mode

        # Kind of overkill to construct this object just to access one key...
        o = CfgNode(data=data, name=name, parentnode=parentnode)

        mode = o.cfg_get('mode')
        subcls = {
            'gssapi': GssapiLdapAuthConfig,
        }.get(mode)

        if not subcls:
            o.raise_for_key('mode', "Unrecognized mode: {}".format(mode))
        return subcls(data=data, name=name, parentnode=parentnode, mode=mode)


class LdapAuthConfig(CfgNode, metaclass=LdapAuthConfigFactory):
    def __init__(self, data, name, parentnode, mode):
        self.mode = mode
        super().__init__(data=data, name=name, parentnode=parentnode)


def all_or_none(*args):
    nset = sum(bool(x) for x in args)
    return nset in (0, len(args))

class GssapiLdapAuthConfig(LdapAuthConfig):
    def _populate(self):
        self.username = self.cfg_get('krb_username', default=None)
        self.keytab   = self.cfg_get_path('krb_keytab', default=None)
        self.cache    = self.cfg_get_path('krb_cache', default=None)

        if not all_or_none(self.username, self.keytab, self.cache):
            raise ConfigError("If any of the ldap_auth.krb_* args are set, all of them must be set")







class PasswordExpConfig(CfgNode):
    def _populate(self):
        if not self._parentnode.smtp:
            self.raise_for_key('', "smtp not configured")

        # days
        days = self.cfg_get('days')
        if isinstance(days, int):
            self.days = [days]
        elif isinstance(days, list):
            self.days = days
        else:
            self.invalid_type('days', days, (int, list))
        self.days.sort(reverse=True)

        # template
        path = self.cfg_get_path('template_file')
        try:
            f = open(path, 'r')
        except OSError as e:
            self.raise_for_key('template_file', "Error reading template: {}".format(e))

        with f:
            self.template = f.read()


class SmtpConfig(CfgNode):
    def _populate(self):
        self.email_from = self.cfg_get('email_from')

        # Default to sending mail via SMTP server running on this host
        self.host = self.cfg_get('host', default='localhost')
        self.port = self.cfg_get('port', default=0)

        self.username = self.cfg_get('username', default=None)
        self.password = self.cfg_get('password', default=None)
        g = (self.username, self.password)
        if sum(bool(x) for x in g) not in (0, len(g)):
            self.raise_for_key(None, "If username or password are set, both must be set")

        self.encryption = self.cfg_get('encryption', default="").lower()
        if not self.encryption in ("", "ssl", "starttls"):
            self.raise_for_key('encryption', 'Invalid value: {}'.format(self.encryption))


def RangeConfig(data, name, parentnode):
    o = CfgNode(data=data, name=name, parentnode=parentnode)
    return range(o.cfg_get('min'), o.cfg_get('max'))

RangeConfig.data_type = dict      # XXX TODO: See isinstance check in CfgBase.cfg_get()


class Container(CfgNode):
    default_scope = 'subtree'

    def __init__(self, data, name, parentnode):
        if data is None:
            data = {}
        elif isinstance(data, dict):
            pass
        else:
            parentnode.invalid_type(name, data)

        super().__init__(data=data, name=name, parentnode=parentnode)

        self.scope = self.cfg_get('scope', default=self.default_scope)
        if not self.scope in ('subtree', 'one'):
            self.raise_for_key('scope', "Invalid scope: {}".format(self.scope))


class ContainerConfigDict(CfgDict):
    value_class = Container

    # all cfg_get() must use defaults if you use this!
    dummy_class = Container

    def _populate(self):
        assert issubclass(self.value_class, Container)
        for container, d in self._data.items():
            self[container] = self.value_class(data=d, name=container, parentnode=self)

    def iterate_containers(self):
        if len(self) == 0:
            # Not configured => search everything
            assert issubclass(self.dummy_class, Container)
            dummy = self.dummy_class({}, 'dummy', self)
            yield (None, dummy)
        else:
            for container, d in self.items():
                yield (container, d)

    def _get_dict_for_str(self):
        return dict(self.iterate_containers())


class UpnSuffixConfig(Container):
    def __init__(self, data, name, parentnode):
        if isinstance(data, str):
            data = dict(suffix=data)
        elif isinstance(data, dict):
            pass
        else:
            parentnode.invalid_type(name, data)

        super().__init__(data=data, name=name, parentnode=parentnode)

    def _populate(self):
        super()._populate()
        self.suffix = self.cfg_get('suffix')


class UpnSuffixesConfig(ContainerConfigDict):
    value_class = UpnSuffixConfig


class IdAssignConfig(CfgNode):
    def _populate(self):
        self.uid_range = self.cfg_get('uid_range', cls=RangeConfig)
        self.gid_range = self.cfg_get('gid_range', cls=RangeConfig)
        self.computers = self.cfg_get('computers', default=True)
        self.only = self.cfg_get('only', defaultdata={}, cls=ContainerConfigDict)


class UserdirConfig(CfgNode):
    def _populate(self):
        self.basepath = self.cfg_get('basepath')
        self.only = self.cfg_get('only', defaultdata={}, cls=ContainerConfigDict)
        self.owner = self.cfg_get('owner', default=None)
        self.group = self.cfg_get('group', default=None)
        self.acl = self.cfg_get('acl', default=[])
        self.subdirs = self.cfg_get('subdirs', defaultdata=[], cls=UsersubdirConfig)


class UserdirsConfig(CfgList):
    def _populate(self):
        for i, ud in enumerate(self._data):
            self.append(UserdirConfig(data=ud, name=str(i), parentnode=self))

class UserSubdirConfig(CfgNode):
    def _populate(self):
        self.name = self.cfg_get('name')
        self.acl = self.cfg_get('acl', default=[])

class UsersubdirConfig(CfgList):
    def _populate(self):
        for i, d in enumerate(self._data):
            self.append(UserSubdirConfig(data=d, name=str(i), parentnode=self))


class StaleAcctsConfig(CfgNode):
    def _populate(self):
        self.email_to = self.cfg_get('email_to', default=None)
        if self.email_to and not self._parentnode.smtp:
            self.raise_for_key('email_to', "smtp not configured")

        # Global settings/defaults
        self.older_than = self.cfg_get('older_than', cls=DurationConfig)
        self.disable = self.cfg_get('disable', default=False)

        def cont(key):
            return self.cfg_get(key, defaultdata={}, cls=StaleAcctsContainerConfigDict)
        self.users = cont('users')
        self.computers = cont('computers')


class StaleAcctsContainer(Container):
    def _populate(self):
        g = self._parentnode._parentnode

        self.older_than = self.cfg_get('older_than', cls=DurationConfig, default=g.older_than)
        self.disable = self.cfg_get('disable', default=g.disable)


class StaleAcctsContainerConfigDict(ContainerConfigDict):
    value_class = StaleAcctsContainer
    dummy_class = StaleAcctsContainer


class Config(CfgRoot):
    def __init__(self, data, path):
        cfgpath = Path(path).resolve(strict=True)
        super().__init__(data=data, cfgpath=cfgpath)

    def _populate(self):
        self.domain = self.cfg_get('domain')

        self.changelog_path = self.cfg_get_path('changelog', default=None)

        self.id_assign = self.cfg_get('id_assign', cls=IdAssignConfig, default=None)

        self.ldap_auth = self.cfg_get('ldap_auth', cls=LdapAuthConfig)

        self.userdirs = self.cfg_get('userdirs', defaultdata=[], cls=UserdirsConfig)

        self.upn_suffixes = self.cfg_get('upn_suffixes', defaultdata={}, cls=UpnSuffixesConfig)
        
        self.smtp = self.cfg_get('smtp', default=None, cls=SmtpConfig)

        self.pwexp = self.cfg_get('password_expiry_notification',
                default=None, cls=PasswordExpConfig)

        self.stale_accounts = self.cfg_get('stale_accounts', default=None, cls=StaleAcctsConfig)


    @classmethod
    def load(cls, path):
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
        except (IOError, yaml.YAMLError) as e:
            raise ConfigError(e)

        return cls(data, path)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('config')
    ap.add_argument('--debug', action='store_true')
    args = ap.parse_args()

    try:
        cfg = Config.load(args.config)
    except ConfigError as e:
        if args.debug:
            raise
        raise SystemExit("Config error: {}".format(e))

    print(cfg)
