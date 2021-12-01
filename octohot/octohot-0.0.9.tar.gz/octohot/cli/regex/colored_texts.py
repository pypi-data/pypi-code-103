class Colors:
    PINK = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    TERMINATE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def warning(self, msg, bold=False, underline=False):
        bold = self.BOLD if bold else ''
        underline = self.UNDERLINE if underline else ''
        return bold + underline + self.YELLOW + str(msg) + self.TERMINATE

    def success(self, msg, bold=False, underline=False):
        bold = self.BOLD if bold else ''
        underline = self.UNDERLINE if underline else ''
        return bold + underline + self.GREEN + str(msg) + self.TERMINATE

    def primary(self, msg, bold=False, underline=False):
        bold = self.BOLD if bold else ''
        underline = self.UNDERLINE if underline else ''
        return bold + underline + self.BLUE + str(msg) + self.TERMINATE

    def fail(self, msg, bold=False, underline=False):
        bold = self.BOLD if bold else ''
        underline = self.UNDERLINE if underline else ''
        return bold + underline + self.RED + str(msg) + self.TERMINATE

    def bold(self, msg):
        return self.BOLD + str(msg) + self.TERMINATE

    def underline(self, msg):
        return self.UNDERLINE + str(msg) + self.TERMINATE

    def header_pink(self, msg):
        return self.PINK + str(msg) + self.TERMINATE
