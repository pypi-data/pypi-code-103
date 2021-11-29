import subprocess
from pdx import Console
import os


class Executor:
    """Execute command-line processes via subprocess"""
    console_instance = Console.get()
    run_from_path = None
    command = None
    return_code = None
    output = None
    stderr = None

    def get_output(self):
        return self.output.decode('utf-8').strip()

    def get_stderr(self):
        return self.stderr.decode('utf-8').strip()

    def get_all_output(self):
        return "{0}\n{1}".format(self.get_output(), self.get_stderr())

    def run(self):
        """Run a command"""
        self.console_instance.trace("Executor.run", self.command)

        # If no command was given, exit with error
        if self.command is None or (len(self.command) == 0):
            self.console_instance.put_error("No command was specified")
            return

        # If running from a specified path, cd now
        start_dir = None
        if self.run_from_path is not None:
            start_dir = os.getcwd()
            os.chdir(self.run_from_path)

        # Run the command
        try:

            # Run command
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            (self.output, self.stderr) = process.communicate()
            self.return_code = process.returncode
            del process

        except Exception as ee:
            self.console_instance.put_error(ee)
            self.console_instance.put_error("Error running command {0}".format(self.command))

        # Return to start directory (if applicable)
        if start_dir is not None:
            os.chdir(start_dir)
        del start_dir

    def __init__(self, command=None, run_from_path=None):

        # Save the given command, if applicable
        if type(command) is list:
            self.command = command
        elif type(command) is str:
            self.command = command.split()

        # If command needs to be run from a specified path
        self.run_from_path = run_from_path

        # ToDo: Decide: Run it now if command was given?
        if self.command is not None:
            self.run()
