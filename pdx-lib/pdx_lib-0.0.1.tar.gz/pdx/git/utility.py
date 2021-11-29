from pdx import Session
from pdx import Console
from pdx import Executor
from datetime import datetime

# Console shared by all commands
out = Console.get()


def run_git_cmd(cmd_list, trace_level="info", suppress_errors=False):
    """Run a Git command via subprocess in the current directory"""
    out.trace("Run Git Command: {0}".format(" ".join(cmd_list)), [], trace_level)
    exe = None
    try:
        # Convert a command string to a command list, if needed
        if type(cmd_list) is str:
            cmd_list = cmd_list.split()

        exe = Executor.Executor(cmd_list)

        # Look for a "fatal" error
        if "fatal" in exe.get_stderr():
            out.log_info("Potential error detected running Git command: {0}".format(" ".join(cmd_list)))

            # Log stdout from the command
            out.log_info(exe.get_output())

            # Print, log, and increment error counter (unless suppressing errors)
            if not suppress_errors:
                out.put_error(exe.get_stderr())

        # Log output for certain commands
        elif cmd_list[1] in ['push', 'pull', 'reset', 'commit', 'merge']:
            out.log(exe.get_all_output(), trace_level)

        # Log other output containing the word error
        elif "error" in exe.get_output():
            out.log(exe.get_all_output(), level=trace_level)

        # If stderr not printed or logged, print it when in debug mode
        elif Session.debug_mode and exe.get_stderr() != "":
            out.put_debug(exe.get_stderr())

    except Exception as ee:
        out.put_error("Error running Git command {0}\n{1}".format(cmd_list, ee))

    return exe


def get_repo_from_url(repo_url):
    """Get repository name from repository URL"""
    offset = repo_url.rfind("/")
    return repo_url[offset+1:].replace('.git', '')


def get_repo_base():
    """Get the base directory of the current Git repo"""
    out.trace("get_repo_root", [])
    repo_base = None

    exe = Executor.Executor("git rev-parse --show-toplevel")
    if exe.return_code == 0:
        repo_base = exe.get_output()
    del exe
    return repo_base


def set_config(config_var, config_value):
    """Set name or email in Git config"""
    out.trace("set_config", [config_var, config_value])

    # Set config value
    exe = run_git_cmd(["git", "config", "user.{0}".format(config_var), config_value])

    return exe.return_code == 0


def get_config(config_var):
    """Get name or email from Git config"""
    out.trace("get_config", [config_var])

    # Get config value
    exe = run_git_cmd(["git", "config", "user.{0}".format(config_var)], trace_level="debug")
    return exe.get_output()


def set_global_config(config_var, config_value):
    """Set name or email in Git config"""
    out.trace("set_config", [config_var, config_value])

    # Set config value
    exe = run_git_cmd(["git", "config", "--global", "user.{0}".format(config_var), config_value])

    return exe.return_code == 0


def get_global_config(config_var):
    """Get name or email from Git config"""
    out.trace("get_config", [config_var])

    # Get config value
    exe = run_git_cmd(["git", "config", "--global", "user.{0}".format(config_var)], trace_level="debug")

    return exe.get_output()


def git_string_to_date(git_date_string):
    """Convert a Git date-string into a date"""
    # Example date:    Thu Jan 5 10:34:23 2017 -0800
    str_format = '%a %b %d %H:%M:%S %Y'
    return datetime.strptime(git_date_string[:-5].strip(), str_format)
