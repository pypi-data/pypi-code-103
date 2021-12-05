import logging
import os
from pprint import pformat
import smbc
import string

from .assign import AssignerBase
from .smbacl import *

logger = logging.getLogger(__name__)


def get_subdirs(smbdir):
    for e in smbdir.getdents():
        if e.smbc_type != smbc.DIR:
            continue
        if e.name in ('.', '..'):
            continue
        yield e.name


class NoneTemplate(string.Template):
    """Template that passes through None templates"""
    def substitute(self, *args, **kwargs):
        if self.template is None:
            return None
        return super().substitute(*args, **kwargs)


class TemplatedSecurityDescriptor:
    """Represents a security descriptor that accepts templated strings"""
    def __init__(self, owner=None, group=None, acl=None):
        self.owner_tmpl = NoneTemplate(owner)
        self.group_tmpl = NoneTemplate(group)
        self.acl_tmpls = [NoneTemplate(ace) for ace in (acl or [])]

    def substitute(self, **kw):
        """Get an SmbSecurityDesc for a given user"""

        return SmbSecurityDesc(
            owner = self.owner_tmpl.substitute(**kw),
            group = self.group_tmpl.substitute(**kw),
            acl = [
                SmbAce.parse(a.substitute(**kw)) for a in self.acl_tmpls
            ],
        )


class UserdirCreator(AssignerBase):
    def __init__(self, ad, onchange=None):
        super().__init__(ad, onchange=onchange)

        # Create samba client context
        self.ctx = smbc.Context()
        self.ctx.optionUseKerberos = True
        self.ctx.optionFallbackAfterKerberos = False
        self.ctx.optionNoAutoAnonymousLogin = True


    def create_userdirs(self, basepath, tsd, container, scope='subtree', subdirs=None):
        """Create directories for users

        basepath: Base UNC path in which to create a directory per user
        tsd: TemplatedSecurityDescriptor to substitute and apply to the new directory
        container: The domain container to limit the user directory creation, or None
        scope: The scope to search container
        subdirs: A tuple of (name, tsd) subdirectories to create
        """
        if subdirs is None:
            subdirs = []

        logger.info("Creating user directories in {} for container {} (scope: {})"
                .format(basepath, container, scope))

        if not basepath.startswith('//'):
            raise ValueError("basepath must start with //")
        baseuri = 'smb:' + basepath

        basedir = self.ctx.opendir(baseuri)

        curdirs = set(get_subdirs(basedir))
        logger.debug("Current directories:\n" + pformat(curdirs))

        usernames = set(u.sAMAccountName for u in self.get_users(rdn=container, scope=scope))
        logger.debug("Current users:\n" + pformat(usernames))

        users_without_dirs = usernames - curdirs
        logger.debug("Users without dirs:\n" + pformat(users_without_dirs))
        
        dirs_without_users = curdirs - usernames
        logger.debug("Directories without users:\n" + pformat(dirs_without_users))

        for user in users_without_dirs:
            # Make user dir
            self._mkdir(
                uri = os.path.join(baseuri, user),
                sd = tsd.substitute(user=user),
            )

            # Create subdirectories
            for subdir_name, subdir_tsd in subdirs:
                self._mkdir(
                    uri = os.path.join(baseuri, user, subdir_name),
                    sd = subdir_tsd.substitute(user=user),
                )

    def _mkdir(self, uri, sd):
        logger.info("Making directory: {}".format(uri))
        self.ctx.mkdir(uri)

        # Get the current security descriptor
        v = self.ctx.getxattr(uri, smbc.XATTR_ALL_SID)
        logger.info("Got security descriptor: {}".format(v))
        new_sd = SmbSecurityDesc.parse(v)

        # Merge the template information into the descriptor
        new_sd.update(sd)

        # Replace the entire descriptor
        logger.info("Setting security descriptor: {}".format(str(new_sd)))
        self.ctx.setxattr(uri, smbc.XATTR_ALL_SID, str(new_sd), 0)

        self.onchange(message="Created directory: {}".format(uri))
