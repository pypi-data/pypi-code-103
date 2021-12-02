import os
from pathlib import Path

from tcim import cmdlib

base_template = """\
[Desktop Entry]
Name={name}
Comment={comment}
Type=Application
Icon=utilities-terminal"""

term_template = base_template + """
Exec=sh -c "{command}; read"
Terminal=true"""

nokeep_template = base_template + """
Exec=sh -c "{command}"
Terminal=true"""

noterm_template = base_template + """
Exec={command}
Terminal=false"""

desktopfiles_dir = Path.home() / ".cache" / "tcim"
directory_file = cmdlib.tcim_conf_dir / "command-menu.directory"

def get_deleted_commands():
    from_env = os.environ.get("XDG_DATA_HOME")
    if not (from_env and (xdg_data_home := Path(from_env)).is_absolute()):
        xdg_data_home = Path.home() / ".local" / "share"

    installed_commands = set(
        file.name for file in (xdg_data_home / "applications").glob("command-*.desktop")
    )
    new_commands = set(file.name for file in desktopfiles_dir.glob("*.desktop"))
    return installed_commands - new_commands


if not directory_file.exists():
    text = (Path(__file__).resolve().parent / "command-menu.directory").read_text()
    directory_file.write_text(text)

for cmd in cmdlib.cmd_dict.values():
    # populate template
    if not cmd.terminal:
        desktop_str = noterm_template.format(
            name=cmd.name, comment=cmd.comment, command=cmd.command
        )
    elif not cmd.keep:
        desktop_str = nokeep_template.format(
            name=cmd.name, comment=cmd.comment, command=cmd.command
        )
    else:
        desktop_str = term_template.format(
            name=cmd.name, comment=cmd.comment, command=cmd.command
        )
    # save .desktop file
    filename = "command-" + cmd.name.replace(" ","-") + ".desktop"
    (desktopfiles_dir / filename).write_text(desktop_str)

# print deleted commands to pipe them into xdg-desktop-menu uninstall
print(" ".join(get_deleted_commands()))
