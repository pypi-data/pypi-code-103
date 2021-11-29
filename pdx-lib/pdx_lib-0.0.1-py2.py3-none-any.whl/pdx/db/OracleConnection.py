from pdx.db import ConnectionHolder
from pdx import Session
from pdx import Encryptor
from pdx import Console
from pdx import utility_service

import cx_Oracle
import hashlib
import getpass
import os


class OracleConnection:
    sid = None
    SID = None
    username = None
    cx = None
    connection_attempts = 0

    def is_production(self):
        """Is this a connection to the production database? (True/False)"""
        return self.sid == 'oprd'

    def is_active(self):
        """Is this connection still active? (True/False)"""
        if self.cx is None:
            return False

        try:
            self.cx.ping()
        except cx_Oracle.DatabaseError:
            return False

        return True

    def close(self):
        """Close this connection and remove it from the ConnectionHolder"""
        try:
            self.cx.close()
        finally:
            self.cx = None
            del ConnectionHolder.connections[self.get_holder_id()]

    @staticmethod
    def get_password_file(username, sid):
        """Determine the location of the encrypted password file"""
        base_dir = os.path.join(Session.pdx_home, 'config', 'db')
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)   # Create the directory, if needed

        # File name is a hash of username and sid
        hl = hashlib.new('ripemd160')
        hl.update(str.encode("{0}-{1}.dat".format(username, sid)))
        file_name = hl.hexdigest()

        return os.path.join(base_dir, file_name)

    def get_holder_id(self):
        """Get the ID of the connection used in the ConnectionHolder"""
        return "{0}-{1}".format(self.username, self.sid)

    def connect(self):
        """Establish a connection"""
        # Can only connect if on the PSU network
        if not utility_service.is_on_psu_network():
            Console.get().put_error("Must be on PSU network to connect to Oracle")
            return

        self.connection_attempts += 1
        password = None
        password_source = None

        # If this connection already exists, use it
        cx_id = self.get_holder_id()
        if cx_id in ConnectionHolder.connections:
            self.cx = ConnectionHolder.connections[cx_id]

            # Verify that the saved connection is still active
            if not self.is_active():
                self.cx = None
                del ConnectionHolder.connections[cx_id]

        # If not saved, or is inactive, create a new connection
        if self.cx is None:

            # Determine password file
            pwd_file = self.get_password_file(self.username, self.sid)

            # Decrypt password, if it exists
            if os.path.exists(pwd_file):
                password = Encryptor.Encryptor().decrypt_from_file(pwd_file)
                password_source = 'file'

            # Otherwise, if not running in auto-mode, ask user to enter a password
            elif not Session.auto_mode:
                try:
                    password = getpass.getpass("Oracle password for {0}@{1}: ".format(self.username, self.sid))
                    password_source = 'input'
                except KeyboardInterrupt:
                    Console.get().put_error("Oracle connection canceled by user.")
                    password = None

            # If auto-running with no saved password, then password cannot be obtained
            else:
                Console.get().put_warning("No password could be obtained for {0}".format(self.username))

            # Connect if password was provided
            if password:
                try:
                    dsn_str = cx_Oracle.makedsn("{0}.banner.pdx.edu".format(self.sid), "1521", self.SID)
                    self.cx = cx_Oracle.connect(user=self.username, password=password, dsn=dsn_str)

                    # Test if connection succeeded (raises an error if not)
                    self.cx.ping()

                    # if user had to manually enter their password, encrypt it for future use
                    if password_source == 'input':
                        Encryptor.Encryptor().encrypt_to_file(password, pwd_file)

                    # Save the connection to avoid re-connecting to the same username/sid
                    ConnectionHolder.connections[cx_id] = self.cx

                except cx_Oracle.DatabaseError:
                    self.cx = None
                    Console.get().put_error("Error connecting to the database")

                    # If password came from file, delete the file to prevent repeated failures
                    if password_source == 'file':
                        os.unlink(pwd_file)

                        # Attempt connection again.  User will be prompted for password.
                        if self.connection_attempts == 1 and not Session.auto_mode:
                            self.connect()

                finally:
                    # Overwrite the password variable and delete it
                    password = '                '
                    del password

    # ---------------------------------------------------------------
    # CONSTRUCTOR
    # ---------------------------------------------------------------
    def __init__(self, sid, username=None):
        # Process sid
        self.sid = sid.lower().strip() if sid is not None else None
        self.SID = sid.upper().strip() if sid is not None else None
        if self.sid not in get_sid_list():
            Console.get().put_error("Invalid database instance: {0}".format(self.sid))

        # Process username
        self.username = username.lower() if username and username != "" else Session.username

        # Connect
        self.connect()


def get_sid_list():
    return ['oprd', 'devl', 'test', 'stage']


def get_sqlplus_connection_string(sid, username=None):
    Console.get().trace('get_sqlplus_connection_string', [sid, username])

    # Get a regular cx_Oracle connection
    # This will prompt user for a password if needed
    oracle = OracleConnection(sid, username)

    # Start the connection string
    cx_string = oracle.username

    # Decrypt password, if it exists
    pwd_file = oracle.get_password_file(oracle.username, oracle.sid)
    if os.path.exists(pwd_file):
        cx_string += "/{0}".format(Encryptor.Encryptor().decrypt_from_file(pwd_file))

    # Create the TNS info
    dsn_str = cx_Oracle.makedsn("{0}.banner.pdx.edu".format(sid.lower()), "1521", sid.upper())
    cx_string += "@{0}".format(dsn_str)

    return """sqlplus "{0}" """.format(cx_string)
