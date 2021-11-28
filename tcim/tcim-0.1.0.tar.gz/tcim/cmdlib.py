from subprocess import Popen, PIPE
from pathlib import Path

class Command:

    TERMINAL = "xterm"

    def __init__(self, name, comment, command):
        self.name = name
        self.comment = comment
        self.command = command

    def __str__(self):
        string = self.name
        if self.comment:
            string += " (" + self.comment + ")"
        return string

    def exec(self):
        # or sh -c instead of eval
        Popen([Command.TERMINAL, '-e', 'eval "' + self.command + '; read"'])


cmd_dict = {}
tcim_conf_dir = Path.home() / ".config" / "tcim"
commandsfile = tcim_conf_dir / "commands.tsv"

if not tcim_conf_dir.exists():
    tcim_conf_dir.mkdir()

# load commands file
if not commandsfile.exists():
    commandstext = (Path(__file__).resolve().parent / "commands.tsv").read_text()
    commandsfile.write_text(commandstext)
else:
    commandstext = commandsfile.read_text()

# populate dict with Command objects
for lst in (line.split("\t") for line in sorted(commandstext.splitlines())):
    try:
        c = Command(*lst)
        cmd_dict[str(c)] = c
    except TypeError:
        print("faulty line in commands.tsv:", lst)
