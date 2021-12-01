"""
Module for shell interaction with git.
"""

import subprocess


class GitInteraction:
    """
    Class to allow git shell commands to be run.
    """

    CONFIG = 1

    @staticmethod
    def execute_bash_git_cmd(cmd_type, parameter):
        """
        Execute a specified git sub-command with the given parameters.

        :param cmd_type: int
            One of the command types specified by this class.
        :param parameter: str
            The parameter(s) for the git sub-command.
        :return: str
            The errors if any occurred or None.
        """
        if cmd_type == GitInteraction.CONFIG:
            sub_command = "config"
        else:
            raise ValueError("The command type has to be one defined by the GitInteraction class.")
        git_cmd_process = subprocess.Popen(f"git {sub_command} {parameter}", shell=True, stdout=subprocess.PIPE)
        (output, error) = git_cmd_process.communicate()
        git_cmd_process.wait()
        return error

    @staticmethod
    def get_git_config_credential_set_username_parameter_string(username):
        """
        Concatenate the username with the git config sub-command parameters.
        :param username: str
            The username to use.
        :return: str
            The string '--local credential.${{remote}}.username <username>' where <username> is replaced with
            the passed parameter.
        """
        return f"--local credential.${{remote}}.username {username}"
