from contextlib import contextmanager
import json
import logging

from .ldapobj import LdapObject, IntAttr
from .ldapfilter import Filter
from .util import single

logger = logging.getLogger(__name__)


class DomainState(LdapObject):
    _known_attrs = (
        IntAttr('next_uid', ldapattr='msSFU30MaxUidNumber', writable=True),
        IntAttr('next_gid', ldapattr='msSFU30MaxGidNumber', writable=True),
    )

    @classmethod
    def get(cls, ad):
        # We can't easily know the SFU30 domain name, so for now we'll just assume there's only one.
        rdn = 'CN=ypservers,CN=ypServ30,CN=RpcServices,CN=System'
        f = Filter('objectClass=msSFU30DomainInfo')
        attrs = cls.default_ldap_attrs()

        dn, attrvals = single(ad._search(rdn, f, attrs))
        return cls(ad, dn, **attrvals)

    def __str__(self):
        return 'Next uidNumber: {}\nNext gidNumber: {}'.format(
                self.next_uid, self.next_gid)

    @property
    def complete(self):
        return None not in (self.next_uid, self.next_gid)
