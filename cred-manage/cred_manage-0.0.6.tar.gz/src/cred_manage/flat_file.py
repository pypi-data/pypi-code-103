"""
Subclass of the BaseCredContainer class used for reading secrets from a flat file.
While we all know it is not best practice, IRL to store sensitive things in flat files there may be some cases where it makes sense
(or at least is 'okay'):  Local Development.  Bearer Tokens.  Short-lived / Temporary Secrets.  Passphrases, corresponding with encryption keys, etc.

THINK TWICE BEFORE USING THIS TYPE OF CREDENTIAL CONTAINER IN PRODUCTION APPLICATIONS!
IF THERE IS A BETTER, MORE SUITABLE IMPLEMENTATION, PLEASE USE THAT
"""

import os
import sys
from cred_manage.base_cred_container import CredContainerBase

class FlatFileCredContainer(CredContainerBase):
    """
    A credential container for dealing with credentials stored in flat files
    """

    def __init__(self, file_path:str, allow_broad_permissions=False):
        """
        Init method for the FlatFileCredContainer

        Args:
            file_path (str): A fully qualified path the file which contains the secret
            allow_broad_permissions (bool, optional):  If set to True, will allow instantiation with too-broad of file permissions
        """

        # Validate that the file path is actually a flat file that exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Cannot instantiate {type(self)} container because file doesn't exist: {file_path}")
        
        # Pin file name to self
        self.file_path = file_path

        # Handle the file permissions
        perm_info = self.check_permission_bits()
        perm_msg = perm_info['msg']
        if perm_info['too_broad'] and allow_broad_permissions is False:
            raise Exception(f"Could not instantiate.  The file permissions are too broad!\n{perm_msg}")
        elif perm_info['too_broad'] and allow_broad_permissions is True:
            print(f"Warning!  The file permissions are too broad!\n{perm_msg}", file=sys.stderr)

        self._password = self.get_cred()
    
    def get_cred(self, strip=True) -> str:
        """
        Reads a credential out of a credential file

        Args:
            strip (bool, optional): Causes the str.strip() method to be applied or not. Defaults to True.

        Returns:
            str: The contents of the file
        """
        
        with open(self.file_path, 'r') as f:
            s = f.read()

        if strip:
            s = s.strip()

        return s


    def set_cred(self, new_cred: str, strip=True):
        """
        Sets the credential in the credential file

        Args:
            new_cred ([type]): [description]
            strip (bool, optional): [description]. Defaults to True.
        """
        
        if strip:
            new_cred = new_cred.strip()

        with open(self.file_path, 'w') as f:
            f.write(new_cred)

        self._password = self.get_cred()


    def delete_cred(self):
        """
        Deletes a credential out of a flat file.  The file is not actually deleted, but is populated with an empty string

        Args:
            delete_file (bool, optional): [description]. Defaults to False.
        """

        self.set_cred(new_cred='', strip=True)
        self._password = self.get_cred()

    def check_permission_bits(self) -> dict:
        """
        A function to facilitate helpful messages about permission bits being too broad
        """

        # Lambda for converting a decimal into binary
        dec2bin = lambda some_int : f"{int(some_int):b}".zfill(3)

        perms = oct(os.stat(self.file_path)[0])[-3:]
        owner_perms = dec2bin(some_int=perms[0])
        group_perms = dec2bin(some_int=perms[1])
        world_perms = dec2bin(some_int=perms[2])

        too_broad = False
        msgs = []
        for perm_bits in (owner_perms, group_perms, world_perms):
            r = int(perm_bits[0])
            w = int(perm_bits[1])
            x = int(perm_bits[2])

            if perm_bits is owner_perms:
                if w:
                    msgs.append("To be super-restrictive, consider removing the Write Bit from the Owner Permissions.")
                if x:
                    msgs.append("The user permissions allow the Execute Bit.  Consider removing this.")
            elif perm_bits is group_perms:
                if w or x:
                    too_broad = True
                    msgs.append("The Group Permissions allow Write and/or Execute.")
            elif perm_bits is world_perms:
                if r or w or x:
                    too_broad = True
                    msgs.append("The World Permissions allow for one or more of Read/Write/Execute")
        
        msgs.append(f"The file permissions are {perms}")

        msg = '\n'.join(msgs) if len(msgs) > 0 else None

        ret_val = dict(too_broad=too_broad, msg=msg, perms=perms)

        return ret_val

    def read(self):
        """
        A read method that will return the contents of the file as a string
        """

        ret_val = self.get_cred(strip=False)

        return ret_val
