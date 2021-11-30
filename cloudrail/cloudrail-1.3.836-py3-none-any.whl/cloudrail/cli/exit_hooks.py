import sys


class ExitHooks:
    def __init__(self, exit_callback):
        self.exit_code = None
        self._orig_exit = None
        self.exit_callback = exit_callback

    def hook(self):
        self._orig_exit = sys.exit
        sys.exit = self.exit

    def exit(self, code=0):
        self.exit_code = code
        self.exit_callback(self.exit_code)
        self._orig_exit(code)
