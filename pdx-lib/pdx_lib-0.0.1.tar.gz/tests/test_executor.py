from pdx import Session
from pdx import Executor

import unittest


class TestExecutor(unittest.TestCase):
    """
    Test running command line commands
    """

    def test_executor(self):
        """
        Test running command line commands
        """
        # Run a successful command
        exe = Executor.Executor("ls {0}".format(Session.user_home))
        self.assertTrue(exe is not None, "Executor returned null")
        self.assertTrue(exe.command is not None, "Executor command was not generated")
        self.assertTrue(type(exe.command) is list, "Executor command was not converted to a list")
        self.assertTrue(exe.return_code is not None, "Executor has no return code")
        self.assertTrue(exe.return_code == 0, "Executor is not 0")
        self.assertTrue('Desktop' in exe.get_output(), "No Desktop in home directory?")
        self.assertTrue(exe.get_stderr() == "", "There should be no error")

        # Run a unsuccessful command
        exe = Executor.Executor("ls some-fake-directory-or-file")
        print(exe.return_code)
        print(exe.output)
        print(exe.stderr)
        self.assertTrue(exe.return_code is not None, "Executor has no return code (x2)")
        self.assertTrue(exe.return_code != 0, "Executor is not 0 despite error")
        self.assertTrue(exe.get_output() == "", "There should be no output")
        self.assertTrue("No such file or directory" in exe.get_stderr(), "Should say 'No such file or directory'")


if __name__ == '__main__':
    unittest.main()
