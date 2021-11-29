from pdx import Session
from pdx import Console
from pdx import Encryptor

import unittest
import os


class TestBasics(unittest.TestCase):
    """
    Test the very basics of pdx-lib
    """

    def test_basics(self):
        """
        Test the very basics of pdx-lib
        """

        # Log file is made up of script name and username. Both must be known.
        self.assertTrue(Session.script_name is not None, "Script name cannot be determined")
        self.assertTrue(Session.username is not None, "Username cannot be determined")

        # Logging should have already started (to expected log file name)
        log_instance = Session.logInstance
        self.assertTrue(log_instance is not None, "Logging did not start as expected")
        self.assertTrue(log_instance.logFileName is not None, "Log file name is unknown")
        self.assertTrue(Session.username in log_instance.logFileName, "Log file name does not include username")
        self.assertTrue(Session.script_name in log_instance.logFileName, "Log file name does not include script name")
        self.assertTrue(os.path.isfile(log_instance.logFilePath), "Log file does not exist")

        # Suppress console output so we can print some errors
        out = Console.get()
        self.assertTrue(out is not None, "Received a NULL console")
        out.suppressConsoleOutput = True

        # Printing errors and warnings should increment error/warning counters
        self.assertTrue(out.numErrors == 0, "No errors should have been encountered yet")
        self.assertTrue(out.numWarnings == 0, "No warnings should have been encountered yet")
        out.put_error('test 1')
        out.put_warning('test 2')
        out.put_error('test 3')
        self.assertTrue(out.numErrors == 2, "Two errors should have been encountered")
        # Warnings are not counted when output is suppressed
        # self.assertTrue(out.numWarnings == 1, "One warning should have been encountered")
        self.assertTrue(out.numWarnings == 0, "One warning should have been suppressed")

        # Restore console output
        out.suppressConsoleOutput = False

    def test_encryption(self):
        """Test encryption, which may be used across multiple modules"""

        # Get an encryption object (which uses your public/private RSA key pair)
        encryptor = Encryptor.Encryptor()
        self.assertTrue(encryptor.rsaKeyPath, "Unable to locate your RSA key.")

        # Encrypt/Decrypt a simple string
        test_value = "Hello World!"
        encrypted_value = encryptor.encrypt(test_value)
        decrypted_value = encryptor.decrypt(encrypted_value)

        # Validate the results
        self.assertTrue(encrypted_value != test_value, "Value was not encrypted")
        self.assertTrue(decrypted_value == test_value, "Value was not correctly decrypted")

    def test_encryption_to_file(self):
        """Test saving encrypted values in binary files"""

        # Get an encryption object (which uses your public/private RSA key pair)
        encryptor = Encryptor.Encryptor()
        self.assertTrue(encryptor.rsaKeyPath, "Unable to locate your RSA key.")

        # Encrypt/Decrypt a simple string into a test file
        test_value = "Hello World!"
        binary_file = os.path.join(Session.pdx_home, 'unit-test', 'e2f.dat')

        # Delete the file is it already exists
        if os.path.exists(binary_file):
            os.unlink(binary_file)

        self.assertFalse(os.path.exists(binary_file), "Unable to remove old encryption test file.")

        # Encrypt to file
        encryptor.encrypt_to_file(test_value, binary_file)
        self.assertTrue(os.path.exists(binary_file), "Encrypted file was not created")

        decrypted_value = encryptor.decrypt_from_file(binary_file)
        self.assertTrue(decrypted_value == test_value, "File was not correctly decrypted.")

        # Encrypt a new value to the same file (to verify it is overwritten)
        test_value2 = "Goodbye World!"
        encryptor.encrypt_to_file(test_value2, binary_file)
        decrypted_value2 = encryptor.decrypt_from_file(binary_file)
        self.assertTrue(decrypted_value2 == test_value2, "Existing encrypted file was not overwritten")

        # Delete the file
        os.unlink(binary_file)


if __name__ == '__main__':
    unittest.main()
