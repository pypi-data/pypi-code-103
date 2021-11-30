"""
Subclass of the BaseCredContainer used for reading secrets from bitwarden password manager.
This class wraps the bitwarden CLI.  See:  https://bitwarden.com/help/article/cli/#using-an-api-key
Note that only the Enterprise version of bitwarden can (supported) hit the REST API.  
In contrast, the API key that can be found under the "My Account" page can be used to log into the cli tool

"""
from cred_manage.flat_file import FlatFileCredContainer
from cred_manage.base_cred_container import CredContainerBase
import json
import getpass
import os
import subprocess
import uuid
from shutil import which

def make_bitwarden_container(api_key_flat_file:str = '/.credentials/bw_api.json'):
    """
    Factory function to return a BitwardenCredContainer object, instantiated using data
    read from a flat file.See 'View API Key' button at https://vault.bitwarden.com/#/settings/account

    Args:
        api_key_flat_file (str): The flat file that contains the API details.

    Returns:
        BitwardenCredContainer
    """

    # Validate that the api key flat file actually exists
    if not os.path.isfile(api_key_flat_file):
        raise FileNotFoundError(f"Cannot read the bitwarden API key out of the file '{api_key_flat_file}' because it does not exist!")
    
    # Read the contents of the flat file
    file_cred_obj = FlatFileCredContainer(
        file_path=api_key_flat_file,
        allow_broad_permissions=False) # This is very stubborn about reading a file that isn't locked down properly
    file_contents = file_cred_obj.read()
    j = json.loads(file_contents)

    o = BitwardenCredContainer(**j)
    return o



class BitwardenCredContainer(CredContainerBase):
    """
    A credential container for interacting with bitwarden

    Args:
        CredContainerBase ([type]): [description]
    """

    def __init__(self, client_id:str = None, client_secret:str = None, session_key:str = None, **kwargs) -> None:
        """
        Init method for the BitwardenCredContainer

        Args:
            client_id (string): Username (email address)
            client_secret (string): Password (Hashed, as would be returned by the has_password function)
            
            session_key (string):  If passed, should correspond with a currently valid session key that corresponds with the '--session' 
                for any command and/or the BW_SESSION environment variable.  Ultimately, this is the value we're after for any subsequent
                interactions with the cli.  Thus, if supplied (and valid) this is really the only arg we need
        """

        # We won't get far at all if the bw tool isn't installed.
        which_bw = which('bw')
        if which_bw is None:
            raise FileNotFoundError(f"This program wraps the bitwarden cli tool, 'bw', but it doesn't seem to be installed (or is not on PATH).  Please fix that and try again.  See:  https://bitwarden.com/help/article/cli/")

        # We also need that bw needs to be at least a specific version
        minimum_bw_version="1.18.1"
        valid_version_installed = self._check_bw_version_is_valid(minimum_required_version=minimum_bw_version)
        if valid_version_installed is False:
            raise FileNotFoundError(f"The 'bw' command line is installed, but the version is too old.  Version {minimum_bw_version} or greater is required.  Please upgrade using your OS package manager.  Type 'bw --version' to check your version")

        # Pin client id and client secret to self
        self.client_id = client_id
        self.client_secret = client_secret
        self.session_key = session_key

        # Just for a stab in the dark , see if BW_SESSION is set and if so, set the value to self.session_key
        # If it's invalid, it's not a big deal because get_auth_status (which wraps get_bitwarden_status) will return 'locked'
        if 'BW_SESSION' in os.environ:
            self.session_key = os.getenv('BW_SESSION')

        # Do validations
        if session_key is None:
            # Then we've got to have the client id and secret
            if self.client_id is None or self.client_secret is None:
                raise ValueError(f"If not instantiating with a session key, client_id and client_secret arguments must be supplied")
        
        # Pin other arbitrary stuff to self
        for k in kwargs.keys():
            if not hasattr(self, k):
                setattr(self, k, kwargs[k])

        # Set environment variables that the BW CLI looks for to skip prompt for credentials
        os.environ['BW_CLIENTID'] = self.client_id
        os.environ['BW_CLIENTSECRET'] = self.client_secret

        # Get context about email address
        if not hasattr(self, 'email_address'):
            self.email_address = input("Bitwarden account email: ")
            print("If you instantiated via a JSON config file, you can avoid this message in the future by adding the key 'email_address'")

        # Do the login flow.  This will ultimately pin the value for self.session_key if we didn't have a valid one already
        if self._get_auth_status() != 'unlocked':
            self._do_auth_and_unlock_flow()

        # At this point we should be unlocked for sure.  If not, we've failed miserably
        if self._get_auth_status() != 'unlocked':
            raise ValueError(f"The bitwarden vault should be unlocked now using the session key but it still isn't.  Something bad happened.  There might be a bug in this program.  Please troubleshoot.\nSession Key: {self.session_key}")

        # Load the vault and pin it to self.  Note that this will pin the vault with all passwords redacted
        self.vault_contents = None
        self._load_vault()  # Sets self.vault_contents

    def _check_bw_version_is_valid(self, minimum_required_version:str):
        """
        Checks the version of bitwarden.  We need 1.18.1 or higher to leverage reading password out of environment variables via --passwordenv
        This method does not use the _do_bw_command() helper function because that passes the session key which we may not have yet

        Args:
            minimum_required_version (str): A minimum required version string.  Like "1.18.1"

        Raises:
            ValueError: If the 'bw --version' command results in an error for some reason

        Returns:
            [Boolean]: A flag telling us if the installed version is recent enough or not
        """

        # Get the bitwarden version from the command line. 
        # We're purposely avoiding the _do_bw_command() method here.  
        cmd = "bw --version"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return_code = result.returncode
        std_out = result.stdout.decode('utf-8')
        std_err = result.stderr.decode('utf-8')
        if return_code != 0:
            raise ValueError(f"The command '{cmd}' resulted in a non-zero exit code of {return_code}.\n{std_err}")
        else:
            bw_env_string = std_out.strip()

        # Parse the installed version number
        bw_version_parts = bw_env_string.split('.')
        
        major = int(bw_version_parts[0]) if len(bw_version_parts) >= 1 else 0
        minor = int(bw_version_parts[1]) if len(bw_version_parts) >= 2 else 0
        patch = int(bw_version_parts[2]) if len(bw_version_parts) >= 3 else 0

        # Parse the necessary version number
        required_bw_version_parts = minimum_required_version.split(".")
        required_major = int(required_bw_version_parts[0]) if len(required_bw_version_parts) >= 1 else 0
        required_minor = int(required_bw_version_parts[1]) if len(required_bw_version_parts) >= 2 else 0
        required_patch = int(required_bw_version_parts[2]) if len(required_bw_version_parts) >= 3 else 0

        # Is it up to snuff?
        if major >= required_major and minor >= required_minor and patch >= required_patch:
            valid_version = True
        else:
            valid_version = False
        
        return valid_version
        
    def _do_auth_and_unlock_flow(self):
        """
        Gently guides us through the necessary steps to get the vault into an unlocked state
        We need to go from 'unauthenticated' --> 'locked' --> 'unlocked'
        """

        auth_status = self._get_auth_status()

        # Bail out if we're already unlocked
        if auth_status == 'unlocked':
            return
        
        # We've got some auth and/or unlocking to do. Put the password into a randomly named environment variable
        rand_variable_name = str(uuid.uuid1()).upper()
        os.environ[rand_variable_name] = getpass.getpass("Bitwarden Master Password: ")

        try:
            while auth_status != 'unlocked':
                
                auth_status = self._get_auth_status()
                
                if auth_status == 'unauthenticated':
                    # Let's get authenticated
                    self._log_in(password_environemt_variable=rand_variable_name)

                elif auth_status == 'locked':
                    # We are authenticated (That is, bitwarden is pointing to our account), but the vault is locked
                    self._unlock(password_environemt_variable=rand_variable_name) # This method pins session_key to self
                elif auth_status == 'unlocked':
                    # We are authenticated and the vault is unlocked.  We can interact with it now
                    print("The vault is now unlocked.")
                    break
                else:
                    raise ValueError(f"There is no handling for the status '{auth_status}'")
        finally:
            del os.environ[rand_variable_name] # Implicitly calls unsetenv


    def _log_in(self, password_environemt_variable:str):
        """
        Walks is through the login process.  For details, see 'bw login --help'

        Args:
            password_environemt_variable (string): The name of an environment variable which contains our master password
        """

        client_secret = self.client_secret
        email = self.email_address

        # Now log in and point to the environment variable
        print ("Logging into Bitwarden...")
        cmd = f"bw login {self.email_address} --passwordenv {password_environemt_variable} --apikey {self.client_secret}"
        self._do_bw_command(command=cmd)

    def _unlock(self, password_environemt_variable:str):
        """
        Unlocks the vault after having previously logged in.  This action returns a session key

        Args:
            password_environemt_variable (string): The name of an environment variable which contains our master password
        """
        
        print ("Unlocking Bitwarden Vault...")
        cmd = f"bw unlock --passwordenv {password_environemt_variable} --raw"  #The raw flag simply prints the session key that we should use for subsequent requests
        session_key = self._do_bw_command(command=cmd)
        self.session_key = session_key  # This can be set in the env var BW_SESSION or passed with a '--session' argument with any bw command    

    def _get_bitwarden_status(self):
        """
        Issues the 'bitwarden status' command, which returns a JSON object we can use to tell if we're logged in or not
        """

        # Do we already have a session key?
        if self.session_key is not None and self.session_key != '':
            session_key_part = f" --session '{self.session_key}'"
        else:
            session_key_part = ""

        cmd = f"bw status{session_key_part}"
        ret_val = self._do_bw_command(command=cmd)
    
        return json.loads(ret_val)

    def _get_auth_status(self):
        """
        Returns the authentication status which according to 'bw status --help' should be one of these:
            "unauthenticated", "locked", "unlocked"
        """

        return self._get_bitwarden_status()['status']
        

    def _retrieve_session_key(self):
        """
        Issues the command 'bw login --raw' which causes authentication to happen and returns a session key to be used for subsequent requests
        """

        # Get the status
        self._get_bitwarden_status()

        command = "bw login --raw"
        result = self._do_bw_command(command=command)

        print(f"Instantiated {type(self)} for username (email address) {self.username}")
        

    def get_cred(self, guid:str):
        """
        A wrapper around the get_credentials_by_guid method.
        Why?  Because this method is defined in the superclass and is intended to be overridden.
        That's why.  Of course, it's perfectly fine to just call get_credentials_by_guid
        Args:
            guid (str): The Guid which we care to seek

        Returns:
            [dict]: Dict Containing the username and password in question
        """

        return self.get_credentials_by_guid(guid=guid) # Raises exceptions as needed

    def set_cred(self):
        return super().set_cred()
    
    def delete_cred(self):
        return super().delete_cred()

    def _load_vault(self, force_reload=False):
        """
        Gets the entire vault, removes all passwords and pins it to self for some client side interrogation

        Args:
            force_reload (bool, optional): If True, causes a refresh from bw if the vault is already pinned to self. Defaults to False.

        Returns:
            [dict]: A dictionary with the complete contents of the vault and given value at the path i['login']['password'] will be removed
        """

        # Short circuit?
        if force_reload is False and self.vault_contents is not None:
            return self.vault_contents

        # Get everything in the vault
        print("Synchronizing Vault")
        self._do_bw_command('bw sync')
        print("Getting all vault items.  Passwords will be redacted.")
        vault_items_as_string = self._do_bw_command('bw list items')
        vault_items = json.loads(vault_items_as_string)
        
        # Just to be safe.  Get rid of the vault as string.
        vault_items_as_string = ''
        del vault_items_as_string

        # Drop all passwords from the json blob, just for good measure.  If we actually want a password, we'll get it from the vault again
        for i in vault_items:
            login = i.get('login')
            if login is not None:
                if type(login) is dict and 'password' in login.keys():
                    login['password'] = '<password removed>'

        # Just to be safe, again.  
        ret_val = vault_items.copy()
        vault_items = {}
        del vault_items

        self.vault_contents = ret_val
        return ret_val

    

    def _do_bw_command(self, command:str, raise_exceptions_on_non_zero=True):
        """
        Helper method.  Does a bitwarden cli command and passes the results back
        Args:
            command (string):  The command to pass to the bw cli
            raise_exceptions_on_non_zero (bool, optional): Controls exception raising if the command returns a non-zero code. Defaults to True.
        """

        session_key_part = f'--session "{self.session_key}"'
        cmd = command
        if session_key_part not in cmd:
            cmd = f"{cmd} {session_key_part}"

        result = subprocess.run(cmd, shell=True, capture_output=True)
        return_code = result.returncode
        std_out = result.stdout.decode('utf-8')
        std_err = result.stderr.decode('utf-8')

        # Raise an exception as necessary
        if return_code != 0 and raise_exceptions_on_non_zero is True:
            raise Exception(f"The bw cli returned a non-0 exit code for the command: '{cmd.replace(self.session_key, '<session_key>')}'\n{std_err}")

        return std_out

    def print_items(self):
        """
        Prints the ID and Name of each item from the vault.  Useful mostly for figuring out the GUID of a given object
        """


        vault_contents = self.vault_contents
        for item in vault_contents:
            object_type = item['object']
            object_id = item['id']
            object_name = item['name']

            s = f"Object ID: {object_id}\tObject Type: {object_type}\tObject Name: {object_name}"
            
            if object_type != 'item':
                raise ValueError(f"Encountered a non 'item' object type in the vault.  This is unexpected. {s}")

            print(s)

    def get_vault_item_by_guid(self, guid:str):
        """
        Gets the item (JSON object) for a given GUID from the vault
        been redacted previously

        Args:
            item_guid (str): [description]
        """

        # Load the vault that is pinned to self
        if self.vault_contents is None:
            self._load_vault()

        # Try to find the item within the vault pinned to self.  This saves an unnecessary trip to to BW over the internet if it isn't there
        sought_item = None
        for item in self.vault_contents:
            if item['id'] == guid:
                sought_item = item
                break
        
        # Raise an exception if we didn't find the item
        if sought_item is None:
            raise ValueError(f"The item with GUID {guid} was not found in the vault.")

        item_with_password = json.loads(self._do_bw_command(f"bw get item {guid}"))

        return item_with_password

    def get_credentials_by_guid(self, guid:str):
        """
        Returns the username and password (beneath the 'login' key) for a given item from the vault
        This function simply wraps get_vault_item_by_guid, which will raise exceptions is the item is not in the vault
        Args:
            guid (str): The GUID for the item we want to retreive credentials for
        """
        
        item_with_password = self.get_vault_item_by_guid(guid=guid)
        login = item_with_password['login']
        username = login['username']
        password = login['password']

        return dict(username=username, password=password)

    def get_username_by_guid(self, guid:str):
        """
        Returns the username for a given vault item by GUID.  Since we'll have the vault (without passwords) pinned to self already
        We can just read that rather than pinging bitwarden again

        Args:
            guid (str): [description]
        """
        # Load the vault that is pinned to self
        if self.vault_contents is None:
            self._load_vault()

        # Try to find the item within the vault pinned to self.  This saves an unnecessary trip to to BW over the internet if it isn't there
        sought_item = None
        for item in self.vault_contents:
            if item['id'] == guid:
                sought_item = item
                break
        
        # Raise an exception if we didn't find the item
        if sought_item is None:
            raise ValueError(f"The item with GUID {guid} was not found in the vault.")

        return sought_item['login']['username']

    def get_password_by_guid(self, guid:str):
        """
        Returns the password for a given item by GUID.  Wraps the get_credentials_by_guid method which in turn wraps get_vault_item_by_guid
        (which raises exceptions if something is missing)

        Args:
            guid (str): [description]
        """

        creds = self.get_credentials_by_guid(guid=guid)

        return creds['password']
