from io import StringIO
from contextlib import redirect_stdout


def exec_and_capture_output(cmd, **exec_kwargs):
    """
    A basic wrapper for `exec` command.
    Executes a python command and returns the output
    """
    f = StringIO()
    with redirect_stdout(f):
        exec(cmd, **exec_kwargs)
        output = f.getvalue()
        return output
