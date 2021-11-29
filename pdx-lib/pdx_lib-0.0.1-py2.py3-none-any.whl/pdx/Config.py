import os
import getpass

# Get user's home directory
user_home = os.path.expanduser('~')
pdx_home = os.path.join(user_home, '.pdx-lib')

# Config values are saved in ~/.pdx-lib/config.
# The file name is the config name, and the file content is the config value.


def get_config_value(config_name, default_value=None):
    config_file = os.path.join(pdx_home, 'config', config_name)
    if os.path.isfile(config_file):
        try:
            content = None
            with open(config_file, 'r') as f_in:
                content = f_in.read().strip()
            if content != "":
                return content
        except Exception as ee:
            content = None

    # If no value was returned from file, return default value
    return default_value


def set_config_value(config_name, config_value):
    config_file = os.path.join(pdx_home, 'config', config_name)
    try:
        with open(config_file, 'w') as f_config:
            f_config.write(config_value)

    except Exception as ee:
        return False


# Allow user to specify username and email other than computer login name
username = get_config_value('username', getpass.getuser())
user_email = get_config_value('user_email', "{0}@pdx.edu".format(username))

# Default database (i.e. for unit tests)
default_sid = get_config_value('default_sid', 'test')
alternate_sid = get_config_value('alternate_sid', 'stage')

# ToDo: Allow user to override colors, or disable altogether
disable_color = False
color_dict = {
    "gray":        '\033[1;30m',
    "red":         '\033[1;31m',
    "green":       '\033[1;32m',
    "yellow":      '\033[1;33m',
    "blue":        '\033[1;34m',
    "magenta":     '\033[1;35m',
    "cyan":        '\033[1;36m',
    "white":       '\033[1;37m',
    "crimson":     '\033[1;38m',
    "red_h":       '\033[1;41m',
    "green_h":     '\033[1;42m',
    "gold_h":      '\033[1;43m',
    "blue_h":      '\033[1;44m',
    "magenta_h":   '\033[1;45m',
    "cyan_h":      '\033[1;46m',
    "gray_h":      '\033[1;47m',
    "crimson_h":   '\033[1;48m',
    "reset":       '\033[1;m',
}

# Assign colors to logging levels
color_dict["error"] = color_dict["red"]
color_dict["warning"] = color_dict["magenta"]
color_dict["warn"] = color_dict["warning"]
color_dict["info"] = color_dict["blue"]
color_dict["success"] = color_dict["green"]
color_dict["debug"] = color_dict["gray"]
