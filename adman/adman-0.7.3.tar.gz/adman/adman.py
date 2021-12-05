import ldap
import logging

from .ldapfilter import Filter, BitAndFilter, UserAccountControl
from .ldapobj import LdapObject, IntAttr, StrAttr, SIDAttr, FILETIMEAttr
from .locate import get_domain_ldap_servers
from .util import single_or

from ldap.filter import escape_filter_chars


logger = logging.getLogger(__name__)

################################################################################
# LDAP Filters

BASE_USER_FILTER = Filter('objectClass=user')

USER_SEARCH_FILTER = (
    BASE_USER_FILTER
    & Filter('objectCategory=Person')
    & ~Filter('sAMAccountName=krbtgt*')
)

COMPUTER_SEARCH_FILTER = (
    BASE_USER_FILTER
    & Filter('objectCategory=Computer')
)

GROUP_SEARCH_FILTER = Filter('objectClass=group')

DISABLED_USER_FILTER = BitAndFilter('userAccountControl', UserAccountControl.ACCOUNTDISABLE)


################################################################################
# LDAP connection things

def get_dc_info(l):
    attrs = ['defaultNamingContext', 'dnsHostName']
    r = l.search_s('', ldap.SCOPE_BASE, None, attrs)[0]
    dn, attr_vals = r
    return {k: v[0].decode() for k, v in attr_vals.items()}


def ldap_initialize(domain, proto=None):
    uri = ' '.join(get_domain_ldap_servers(domain, proto=proto))

    logger.debug("ldap.initialize(uri={!r})".format(uri))
    return ldap.initialize(uri)


def ldap_connect_gssapi(domain):
    l = ldap_initialize(domain)

    # https://github.com/python-ldap/python-ldap/issues/275
    l.set_option(ldap.OPT_REFERRALS, 0)


    # Perform an anonymous bind first to get server info
    l.simple_bind_s()
    info = get_dc_info(l)

    # Perform a GSSAPI (Kerberos) secure SASL bind
    l.sasl_gssapi_bind_s()

    return l, info


################################################################################
# Main object model

class ADManager:
    def __init__(self, dnsdomain, ldapconn, base=None):
        self.dnsdomain = dnsdomain
        self.ldapconn = ldapconn
        self.base = base


    @classmethod
    def connect(cls, dnsdomain):
        ldapconn, ldapinfo = ldap_connect_gssapi(dnsdomain)
        logger.info("Connected to {dnsHostName} ({defaultNamingContext})".format(**ldapinfo))

        ad = cls(
                dnsdomain = dnsdomain,
                ldapconn = ldapconn,
                base = ldapinfo['defaultNamingContext'],
            )

        return ad


    def _search(self, base_rdn=None, filt=None, attrs=None, scope=None):
        base = self.base
        if base_rdn is not None:
            base = base_rdn + ',' + base

        if filt is not None:
            filt = str(filt)

        if scope is None:
            scope = ldap.SCOPE_SUBTREE

        if isinstance(scope, str):
            # Map scope string to ldap scope
            scope = {
                'subtree':  ldap.SCOPE_SUBTREE,
                'one':      ldap.SCOPE_ONELEVEL,
            }[scope]

        logger.debug("Search base: {}".format(base))
        logger.debug("Search scope: {}".format(scope))
        logger.debug("Search filter: {}".format(filt))
        logger.debug("Search attrs: {}".format(attrs))
        results = self.ldapconn.search_s(base, scope, filt, attrs)

        for dn, attrs in results:
            if dn is None:
                # Filter out referrals
                # https://mail.python.org/pipermail/python-ldap/2014q1/003350.html
                uri = attrs
                logger.debug("Received referral: %s", uri)
                continue
            yield dn, attrs


    def _get_objects(self, cls, basefilt, rdn=None, filt=None, attrs=None, scope=None):
        if attrs is None:
            attrs = cls.default_ldap_attrs()

        f = basefilt
        if filt is not None:    # Append caller filter
            f = f & filt

        objlist = self._search(base_rdn=rdn, filt=f, attrs=attrs, scope=scope)
        for dn, attrvals in objlist:
            yield cls(self, dn, **attrvals)


    def _modify(self, dn, modlist):
        rc = self.ldapconn.modify_s(dn, modlist)
        logger.debug("modify_s({!r}, {!r}) returned {}".format(
            dn, modlist, rc))


    def get_users(self, **kw):
        return self._get_objects(AdUser, USER_SEARCH_FILTER, **kw)

    def get_user_by_uid(self, uid, attrs=None):
        filt = Filter('uidNumber={}'.format(uid))
        return single_or(self.get_users(filt=filt, attrs=attrs), None)


    def get_computers(self, **kw):
        return self._get_objects(AdComputer, COMPUTER_SEARCH_FILTER, **kw)


    def get_groups(self, **kw):
        return self._get_objects(AdGroup, GROUP_SEARCH_FILTER, **kw)

    def get_group_by_gid(self, gid, attrs=None):
        filt = Filter('gidNumber={}'.format(gid))
        return single_or(self.get_groups(filt=filt, attrs=attrs), None)

    def get_group_by_sid(self, sid, attrs=None):
        filt = Filter('objectSid={}'.format(escape_filter_chars(str(sid), 1)))
        return single_or(self.get_groups(filt=filt, attrs=attrs), None)


class AdUser(LdapObject):
    _known_attrs = (
        StrAttr('cn'),
        IntAttr('uidNumber', writable=True),
        IntAttr('gidNumber', writable=True),
        IntAttr('primaryGroupID'),
        SIDAttr('objectSid'),
        StrAttr('userPrincipalName', writable=True),
        StrAttr('mail'),
        StrAttr('sAMAccountName'),
        FILETIMEAttr('pwdLastSet'),
        FILETIMEAttr('PasswordExpiryTime', ldapattr='msDS-UserPasswordExpiryTimeComputed'),
        FILETIMEAttr('lastLogonTimestamp'),
        IntAttr('userAccountControl', writable=True),  # enum UserAccountControl
    )

    @property
    def disabled(self):
        return bool(self.userAccountControl & UserAccountControl.ACCOUNTDISABLE)

    @disabled.setter
    def disabled(self, value):
        if not isinstance(value, bool):
            raise ValueError("bool expected")

        uac = self.userAccountControl
        if value:
            uac |= UserAccountControl.ACCOUNTDISABLE
        else:
            uac &= ~UserAccountControl.ACCOUNTDISABLE
        self.userAccountControl = int(uac)


class AdComputer(AdUser):
    pass

class AdGroup(LdapObject):
    _known_attrs = (
        StrAttr('cn'),
        IntAttr('gidNumber', writable=True),
        SIDAttr('objectSid'),
    )
