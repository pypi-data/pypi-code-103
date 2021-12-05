# Deals with assigning uidNumber / gitNumber values
import ldap
import logging

from contextlib import contextmanager
from copy import copy

from .adman import DISABLED_USER_FILTER
from .ldapfilter import Filter, OrGroup, BitAndFilter
from .util import single


logger = logging.getLogger(__name__)


# We exclude certain users and groups from id assignment.
# See "Automatically assigning uidNumber / gidNumber attributes"
# https://lists.samba.org/archive/samba/2019-June/223499.html
#
# We can also assign uidNumber / gidNumber for computer accounts.
# See "Setting uidNumber for machine accounts"
# https://lists.samba.org/archive/samba/2020-February/228325.html

# Guidance: Exclude Administrator
EXCLUDE_CN_USERS = [
    'Administrator',
    'Guest',
]

# Exclude all groups created at provision time, except those that are the
# primary group of users/computers we want to be visible from unix.
#
# Domain Admins is explicitly excluded to avoid problems with ownership of
# files in Sysvol on Samba DCs:
#  - https://lists.samba.org/archive/samba/2015-February/189287.html
#  - https://lists.samba.org/archive/samba/2020-January/227972.html
EXCLUDE_CN_GROUPS = (
    'Allowed RODC Password Replication Group',
    'Schema Admins',
    'Denied RODC Password Replication Group',
    'Cert Publishers',
    #'Domain Users',
    'Enterprise Admins',
    'DnsAdmins',
    #'Domain Guests',
    'DnsUpdateProxy',
    'Domain Admins',
    'RAS and IAS Servers',
    'Group Policy Creator Owners',
)

CN_COMPUTER_GROUPS = (
    'Domain Computers',
    'Domain Controllers',
    'Enterprise Read-only Domain Controllers',
    'Read-only Domain Controllers',
)


BUILTIN_LOCAL_GROUP = 0x00000001


class AssignmentError(Exception):
    pass


class AssignerBase:
    def __init__(self, ad, onchange=None):
        self.ad = ad
        self.onchange = onchange

        self.user_filt  = ~OrGroup(*(Filter('CN={}'.format(u)) for u in EXCLUDE_CN_USERS))
        self.user_filt &= ~DISABLED_USER_FILTER

    def get_users(self, all_users=False, rdn=None, scope=None):
        filt = None if all_users else self.user_filt
        return self.ad.get_users(filt=filt, rdn=rdn, scope=scope)

    def get_computers(self, rdn=None, scope=None):
        return self.ad.get_computers(rdn=rdn, scope=scope)

    def get_groups(self, all_groups=False, rdn=None, scope=None, include_computer_groups=False):
        if all_groups:
            filt = None
        else:
            # Exclude builtin local groups
            filt = ~BitAndFilter('groupType', BUILTIN_LOCAL_GROUP)

            # Exclude some groups by CN
            exclude_cns = EXCLUDE_CN_GROUPS
            if not include_computer_groups:
                # Also exclude these groups for computers
                exclude_cns += CN_COMPUTER_GROUPS
            filt &= ~OrGroup(*(Filter('CN={}'.format(g)) for g in exclude_cns))

        return self.ad.get_groups(filt=filt, rdn=rdn, scope=scope)


    def _log_change(self, object_type, dn, attribute, value):
        data = dict(
            object_type = object_type,
            dn = dn,
            attribute = attribute,
            value = value,
        )

        message = "Set {attribute}={value} for {object_type} '{dn}'".format(**data)
        logger.info(message)

        if self.onchange:
            self.onchange(message=message)



class PosixIdAssigner(AssignerBase):
    def __init__(self, ad, state, uid_range, gid_range, replace_invalid=False, onchange=None):
        super().__init__(ad=ad, onchange=onchange)

        self.state = state
        self.uid_range = uid_range
        self.gid_range = gid_range
        self.replace_invalid = replace_invalid

        self._validate_next_uid()
        self._validate_next_gid()

        logger.info("Next uidNumber={} in {}".format(self.state.next_uid, self.uid_range))
        logger.info("Next gidNumber={} in {}".format(self.state.next_gid, self.gid_range))


    def _validate_next_uid(self):
        if not self.state.next_uid in self.uid_range:
            raise AssignmentError("Next uidNumber={} is not in uid_range={}".format(
                    self.state.next_uid, self.uid_range))


    def _validate_next_gid(self):
        if not self.state.next_gid in self.gid_range:
            raise AssignmentError("Next gidNumber={} is not in gid_range={}".format(
                    self.state.next_gid, self.gid_range))


    def _ensure_uid_unused(self, uid):
        u = self.ad.get_user_by_uid(uid, ['dn'])   # TODO: How to specify no attrs at all, just dn?
        if u:
            raise AsssignmentError("User with uidNumber={} already exists: {}".format(uid, dn))


    def _ensure_gid_unused(self, gid):
        grp = self.ad.get_group_by_gid(gid, ['dn'])   # TODO: How to specify no attrs at all, just dn?
        if grp:
            raise AssignmentError("Group with gidNumber={} already exists: {}".format(gid, grp.dn))


    def _need_assign_xidNumber(self, objtype, obj, attr, valid_range):
        # Check for existing xidNumber
        xid = getattr(obj, attr, None)
        if xid is None:
            # Doesn't exist; needs assigned
            logger.info("Found {} without {}: {}".format(objtype, attr, obj.dn))
            return True

        # Valid?
        if not xid in valid_range:
            logger.warning("{} {} {} {} not in {}".format(
                objtype, obj.dn, attr, xid, valid_range))
            # Exists but invalid; needs assigned if we're replacing invalid xids
            return self.replace_invalid

        return False


    ##########################################################################
    # High-level wrappers
    def user_assign(self, container=None, scope='subtree'):
        self.assign_user_uidNumbers(container=container, scope=scope)
        self.update_user_gidNumbers(container=container, scope=scope)

    def computer_assign(self, container=None, scope='subtree'):
        self.assign_computer_uidNumbers(container=container, scope=scope)
        self.update_computer_gidNumbers(container=container, scope=scope)


    ##########################################################################
    # User / computer uidNumber
    def assign_user_uidNumbers(self, container=None, scope='subtree'):
        self._assign_uidNumbers(self.get_users(rdn=container, scope=scope), "user")

    def assign_computer_uidNumbers(self, container=None, scope='subtree'):
        self._assign_uidNumbers(self.get_computers(rdn=container, scope=scope), "computer")

    def _assign_uidNumbers(self, users, objtype):
        logger.info("Assigning {} uidNumbers".format(objtype))
        for user in users:
            if self._need_assign_xidNumber(objtype, user, 'uidNumber', self.uid_range):
                self._assign_uidNumber(user, objtype)

    def _assign_uidNumber(self, user, object_type):
        with self.next_uid() as new_uid:
            # TODO: How do we make the LDAP part transactional, too?
            logger.info("Assigning new uidNumber to user %s, assigning %d", user.dn, new_uid)

            self._ensure_uid_unused(new_uid)

            user.uidNumber = new_uid
            user.commit()

            self._log_change(object_type, user.dn, 'uidNumber', new_uid)


    ##########################################################################
    # User / computer gidNumber
    def update_user_gidNumbers(self, container=None, scope='subtree'):
        self._update_gidNumbers(self.get_users(rdn=container, scope=scope), "user")

    def update_computer_gidNumbers(self, container=None, scope='subtree'):
        self._update_gidNumbers(self.get_computers(rdn=container, scope=scope), "computer")

    def _update_gidNumbers(self, users, objtype):
        """Ensure all user/computer gidNumber attributes match their primary group"""
        logger.info("Setting {} gidNumbers".format(objtype))

        for user in users:
            # Construct the group SID from the domain SID and primaryGroupID attr
            # https://support.microsoft.com/en-us/help/297951
            groupsid = copy(user.objectSid)
            groupsid.rid = user.primaryGroupID

            grp = self.ad.get_group_by_sid(groupsid)
            if not grp:
                logger.warning("Couldn't find primary group %s for %s %s",
                        groupsid, objtype, user.dn)
                continue

            group_gidNumber = getattr(grp, 'gidNumber', None)
            if group_gidNumber is None:
                logger.warning("%s %s primary group %s has no gidNumber",
                        objtype, user.dn, grp.dn)
                continue

            user_gidNumber = getattr(user, 'gidNumber', None)
            if user_gidNumber == group_gidNumber:
                # No changes needed
                continue

            logger.info("%s %s gidNumber (%s) does not match their primary group %s gidNumber (%d)",
                    objtype, user.dn, user_gidNumber, groupsid, group_gidNumber)

            user.gidNumber = group_gidNumber
            user.commit()

            self._log_change(objtype, user.dn, 'gidNumber', group_gidNumber)


    ##########################################################################
    # Group gidNumber
    def assign_group_gidNumbers(self, container=None, scope='subtree',
            include_computer_groups=False):
        logger.info("Assigning Group gidNumbers")
        if not include_computer_groups:
            logger.info("Not assigning gidNumbers to computer groups")

        groups = self.get_groups(
                rdn=container, scope=scope,
                include_computer_groups=include_computer_groups)
        for group in groups:
            if self._need_assign_xidNumber('Group', group, 'gidNumber', self.gid_range):
                self._assign_group_gidNumber(group)


    def _assign_group_gidNumber(self, group):
        with self.next_gid() as new_gid:
            # TODO: How do we make the LDAP part transactional, too?
            logger.info("Assigning new gidNumber to group %s: %d", group.dn, new_gid)

            self._ensure_gid_unused(new_gid)

            group.gidNumber = new_gid
            group.commit()

            self._log_change("group", group.dn, 'gidNumber', new_gid)


    ##########################################################################
    # Clear
    def clear_group_gidNumbers(self):
        logger.info("Clearing Group gidNumbers")
        for group in self.get_groups(all_groups=True):
            if getattr(group, 'gidNumber', None) is None:
                continue

            logger.info("Clearing gidNumber for group %s", group.dn)
            group.gidNumber = None
            group.commit()
            self._log_change("group", group.dn, 'gidNumber', None)


    def _clear_user_attr(self, users, objtype, attr):
        for user in users:
            if getattr(user, attr, None) is None:
                continue

            logger.info("Clearing %s for %s %s", attr, objtype, user.dn)
            setattr(user, attr, None)
            user.commit()
            self._log_change(objtype, user.dn, attr, None)


    def clear_user_uidNumbers(self):
        logger.info("Clearing User uidNumbers")
        self._clear_user_attr(self.get_users(all_users=True), 'user', 'uidNumber')


    def clear_user_gidNumbers(self):
        logger.info("Clearing User gidNumbers")
        self._clear_user_attr(self.get_users(all_users=True), 'user', 'gidNumber')


    def clear_computer_uidNumbers(self):
        logger.info("Clearing Computer uidNumbers")
        self._clear_user_attr(self.get_computers(), 'computer', 'uidNumber')

    def clear_computer_gidNumbers(self):
        logger.info("Clearing Computer gidNumbers")
        self._clear_user_attr(self.get_computers(), 'computer', 'gidNumber')

    def clear_all_ids(self):
        self.clear_group_gidNumbers()
        self.clear_user_uidNumbers()
        self.clear_user_gidNumbers()
        self.clear_computer_uidNumbers()
        self.clear_computer_gidNumbers()

    @contextmanager
    def next_uid(self):
        self._validate_next_uid()
        yield self.state.next_uid

        self.state.next_uid += 1
        self.state.commit()


    @contextmanager
    def next_gid(self):
        self._validate_next_gid()
        yield self.state.next_gid

        self.state.next_gid += 1
        self.state.commit()



class UpnAssigner(AssignerBase):
    def __init__(self, ad, onchange=None):
        super().__init__(ad, onchange=onchange)

        self.upn_suffixes = self.get_alt_upn_suffixes()
        self.upn_suffixes.append(self.ad.dnsdomain)
        logger.debug("Domain UPN suffixes: {}".format(self.upn_suffixes))


    def get_alt_upn_suffixes(self):
        r = self.ad._search(
            base_rdn='CN=Partitions,CN=Configuration',
            attrs=['uPNSuffixes'],
            scope=ldap.SCOPE_BASE,
            )

        dn, attrvals = single(r)
        return [s.decode() for s in attrvals.get('uPNSuffixes', [])]   # TODO: encoding?


    def set_user_upn_suffixes(self, container, conf_suffix, scope='subtree'):
        logger.info("Setting UPN suffix to {} for container {} (scope: {})"
                .format(conf_suffix, container, scope))

        # First ensure that suffix is a valid UPN suffix
        if not conf_suffix in self.upn_suffixes:
            raise AssignmentError("UPN suffix '{}' not configured in Domain".format(conf_suffix))

        # Now iterate over all users in that container
        for user in self.get_users(rdn=container, scope=scope):
            username, cur_suffix = user.userPrincipalName.split('@')

            if cur_suffix == conf_suffix:
                continue

            logger.info("UPN {} does not match configured suffix {}".format(
                user.userPrincipalName, conf_suffix))

            new_upn = '@'.join((username, conf_suffix))
            user.userPrincipalName = new_upn
            user.commit()
            self._log_change("user", user.dn, 'userPrincipalName', new_upn)
