from enum import IntEnum, IntFlag
from itertools import chain

# SmbAcl from smbc.xattr is incomplete/unclear

__all__ = [
    'AceAccess',
    'FileAceAccess',
    'DirAceAccess',

    'AceType',
    'AceFlag',

    'SmbAceVal',
    'SmbAce',
    'SmbSecurityDesc',
]

# Unfortunately you cannot extend enumerations
# https://stackoverflow.com/a/41807919
def combine_enum(*bases):
    return [(i.name, i.value) for i in chain(*bases)]


# Reference:
#   <samba-4.0/gen_ndr/security.h>
#   samba/libcli/security/security.h
#   https://docs.microsoft.com/en-us/windows/win32/secauthz/access-mask

class AceAccess(IntFlag):

    ########################################
    # Specific rights
    # Defined in *AceAccess subclasses
    SEC_MASK_SPECIFIC           = 0x0000FFFF

    ########################################
    # Standard rights
    SEC_MASK_STANDARD           = 0x00FF0000
    SEC_STD_DELETE              = 0x00010000
    SEC_STD_READ_CONTROL        = 0x00020000
    SEC_STD_WRITE_DAC           = 0x00040000
    SEC_STD_WRITE_OWNER         = 0x00080000
    SEC_STD_SYNCHRONIZE         = 0x00100000
    # 21-23 undefined
    SEC_STD_REQUIRED            = 0x000F0000
    SEC_STD_ALL                 = 0x001F0000

    ########################################
    # Flags
    SEC_MASK_FLAGS              = 0x0F000000
    SEC_FLAG_SYSTEM_SECURITY    = 0x01000000
    SEC_FLAG_MAXIMUM_ALLOWED    = 0x02000000

    ########################################
    # Generic rights
    SEC_MASK_GENERIC            = 0xF0000000
    SEC_GENERIC_ALL             = 0x10000000
    SEC_GENERIC_EXECUTE         = 0x20000000
    SEC_GENERIC_WRITE           = 0x40000000
    SEC_GENERIC_READ            = 0x80000000


class _FileAceAccess(IntFlag):
    SEC_FILE_READ_DATA          = 0x00000001
    SEC_FILE_WRITE_DATA         = 0x00000002
    SEC_FILE_APPEND_DATA        = 0x00000004
    SEC_FILE_READ_EA            = 0x00000008
    SEC_FILE_WRITE_EA           = 0x00000010
    SEC_FILE_EXECUTE            = 0x00000020
    SEC_FILE_READ_ATTRIBUTE     = 0x00000080
    SEC_FILE_WRITE_ATTRIBUTE    = 0x00000100
    SEC_FILE_ALL                = 0x000001ff

    SEC_RIGHTS_FILE_READ = (
        AceAccess.SEC_STD_READ_CONTROL
      | AceAccess.SEC_STD_SYNCHRONIZE
      | SEC_FILE_READ_DATA
      | SEC_FILE_READ_ATTRIBUTE 
      | SEC_FILE_READ_EA
    )

    SEC_RIGHTS_FILE_WRITE = (
        AceAccess.SEC_STD_READ_CONTROL
      | AceAccess.SEC_STD_SYNCHRONIZE
      | SEC_FILE_WRITE_DATA
      | SEC_FILE_WRITE_ATTRIBUTE
      | SEC_FILE_WRITE_EA
      | SEC_FILE_APPEND_DATA
    )

    SEC_RIGHTS_FILE_EXECUTE = (
        AceAccess.SEC_STD_READ_CONTROL
      | AceAccess.SEC_STD_SYNCHRONIZE
      | SEC_FILE_READ_ATTRIBUTE
      | SEC_FILE_EXECUTE
    )

    SEC_RIGHTS_FILE_ALL = ( AceAccess.SEC_STD_ALL | SEC_FILE_ALL )


FileAceAccess = IntFlag('FileAceAccess', combine_enum(AceAccess, _FileAceAccess))

class _DirAceAccess(IntFlag):
    SEC_DIR_LIST                = 0x00000001
    SEC_DIR_ADD_FILE            = 0x00000002
    SEC_DIR_ADD_SUBDIR          = 0x00000004
    SEC_DIR_READ_EA             = 0x00000008
    SEC_DIR_WRITE_EA            = 0x00000010
    SEC_DIR_TRAVERSE            = 0x00000020
    SEC_DIR_DELETE_CHILD        = 0x00000040
    SEC_DIR_READ_ATTRIBUTE      = 0x00000080
    SEC_DIR_WRITE_ATTRIBUTE     = 0x00000100


DirAceAccess = IntFlag('DirAceAccess', combine_enum(AceAccess, _DirAceAccess))


class AceType(IntEnum):
    # SEC_ACE_TYPE_*
    ACCESS_ALLOWED          = 0
    ACCESS_DENIED           = 1
    SYSTEM_AUDIT            = 2
    SYSTEM_ALARM            = 3
    ALLOWED_COMPOUND        = 4
    ACCESS_ALLOWED_OBJECT   = 5
    ACCESS_DENIED_OBJECT    = 6
    SYSTEM_AUDIT_OBJECT     = 7
    SYSTEM_ALARM_OBJECT     = 8

class AceFlag(IntFlag):
    # SEC_ACE_FLAG_
    OBJECT_INHERIT          = 0x01
    CONTAINER_INHERIT       = 0x02
    NO_PROPAGATE_INHERIT    = 0x04
    INHERIT_ONLY            = 0x08
    INHERITED_ACE           = 0x10
    VALID_INHERIT           = 0x0f
    SUCCESSFUL_ACCESS       = 0x40
    FAILED_ACCESS           = 0x80


class SmbAceVal:
    def __init__(self, type=AceType.ACCESS_ALLOWED, flags=0, mask=0):
        self.type = type
        self.flags = flags
        self.mask = mask

    @classmethod
    def parse(cls, s):
        parts = s.split('/')
        if len(parts) != 3:
            raise ValueError("Must be 3 parts separated by slashes")

        return cls(
            type  = AceType(int(parts[0])),
            flags = AceFlag(int(parts[1])),
            mask  = FileAceAccess(int(parts[2], 16)),
        )


    def __str__(self):
        # libsmbclient expects decimal integers, even though mask is output in
        # hex. See https://bugzilla.samba.org/show_bug.cgi?id=14303
        #return "{}/{}/0x{:08x}".format(
        return "{}/{}/{}".format(
                self.type, self.flags, self.mask)

    def __repr__(self):
        return "<SmbAceVal type={}, flags={}, mask={}>".format(
                str(self.type),
                str(self.flags),
                str(self.mask),
                )

class SmbAce:
    def __init__(self, sid_or_name, value):
        self.sid_or_name = sid_or_name
        self.value = value

        if not isinstance(value, SmbAceVal):
            raise ValueError("value must be SmbAceVal instance")
    
    @classmethod
    def parse(cls, s):
        parts = s.split(':')
        if len(parts) != 2:
            raise ValueError("Must be 2 parts separated by colons")

        return cls(
            sid_or_name = parts[0],
            value = SmbAceVal.parse(parts[1]),
        )

    def __str__(self):
        return "{}:{}".format(self.sid_or_name, self.value)

    def __repr__(self):
        return "<SmbAce sid_or_name={!r}, value={!r}>".format(
                self.sid_or_name, self.value)



class SmbSecurityDesc:
    """A libsmbclient security descriptor

    The format comes from the documentation for smbc_setxattr() where it
    describes setting "system.nt_sec_desc.*" which is a "complete security
    descriptor, with name:value pairs separated by ... commas".
    """

    def __init__(self, revision=1, owner=None, group=None, acl=None):
        self.revision = revision
        self.owner = owner
        self.group = group
        self.acl = acl or []

    @classmethod
    def parse(cls, s):
        """Parse a security desriptor

        This expects the output of getxattr(... "system.nt_sec_desc.*")
        """
        parts = s.split(',')

        kw = dict(acl=[])

        for p in parts:
            k, v = p.split(':', 1)

            if k == 'REVISION':
                kw['revision'] = int(v)
            elif k == 'OWNER':
                kw['owner'] = v
            elif k == 'GROUP':
                kw['group'] = v
            elif k == 'ACL':
                v = SmbAce.parse(v)
                kw['acl'].append(v)

        return cls(**kw)

    def __str__(self):
        comps = []
        def comp(k, v):
            if v is not None:
                comps.append((k, v))

        comp('REVISION', self.revision)
        comp('OWNER', self.owner)
        comp('GROUP', self.group)
        for ace in self.acl:
            comp('ACL', str(ace))

        return ','.join('{}:{}'.format(k, v) for k,v in comps)

    def __repr__(self):
        r = '{}:\n'.format(type(self).__name__)
        r += '  revision: {}\n'.format(self.revision)
        r += '  owner:    {}\n'.format(self.owner)
        r += '  group:    {}\n'.format(self.group)
        r += '  acl:\n'
        for ace in self.acl:
            r += '    {!r}\n'.format(ace)
        return r


    def add_ace(self, ace):
        """Add an ACE to the ACL"""
        assert isinstance(ace, SmbAce)
        self.acl.append(ace)


    def update(self, other):
        """Update this security descriptor with fields from another

        The owner and group fields of this security descriptor are replaced
        with those values from other, if they are set.

        The acl entries from other are appended to this acl.
        """
        assert isinstance(other, type(self))

        if other.owner is not None:
            self.owner = other.owner

        if other.group is not None:
            self.group = other.group

        for ace in other.acl:
            self.add_ace(ace)
