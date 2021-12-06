from importlib.resources import path as fpath
from typing import Optional

def file_path(filename: str, subpackage: Optional[str]=None) -> str:
    """
    Returns the absolute path of a file associated with a package or subpackage.
    """

    subpackage_path = f"{__package__}{f'.{subpackage}' if subpackage else ''}"

    return str(fpath(subpackage_path, filename))

WIDTH = 750
"""
It is recommended to leave it with '750' as its value
"""

HEIGHT = 700
"""
It is recommended to leave it with '700' as its value
"""

GUI_SPACE = 250
"""
How much space of WIDTH the GUI will use when in-game
"""

SUB_MENU_RIGHT = (WIDTH * 0.29), (HEIGHT // 2), (WIDTH * 0.96), (HEIGHT - 10)
"""
Dimensions for a Menu that has its sub-menu to its RIGHT.
"""

SUB_MENU_LEFT = (WIDTH * 0.066666), (HEIGHT * 0.195714), (WIDTH * 0.766666), (HEIGHT * 0.964285)
"""
Dimensions for a Menu that has its sub-menu to its LEFT.
"""

PROFILES_CHANGER = "Change Profile Name"
"""
Name of button that renames color profiles.
"""

PROFILES_DELETER = "Delete this Profile"
"""
Name of button that deletes the current color profile.
"""

DEFAULT_THEME = "DEFAULT"
"""
Default hidden theme that every new created theme uses as template.
"""

NEW_THEME = "NEW_THEME"
"""
Name template for newly created themes.
"""

EXITING_DELAY = 30
"""
How much time the game waits when the 'EXIT' action is left pressed.
"""

DEBUG_LINES = True
"""
Adds additional information on DEBUG action in process_action function (main module).
"""

SPECIAL_CHARS = '<', "/\\", "\\/", '^', 'v', '+'
"""
These chars will have their name mangled when processed.
"""

DEBUG_TEXT = """player_hitbox: ({player_x1}, {player_y1}), ({player_x2}, {player_y2})
center_hitbox: {hitbox_center}
Shooting Cooldown: {shooting_cooldown}
Invulnerability Cooldown: {inv_cooldown}

Power: {power_level}

Player Stats:
Health: {health}
Hardness: {hardness}
Speed: {speed}

enemies_in_screen: {enemies}
bullets_in_screen: {bullets}
"""

GAME_TITLE = """

░██████╗████████╗░█████╗░██████╗░  ░██████╗██╗░░░░░░█████╗░██╗░░░██╗███████╗██████╗░
██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  ██╔════╝██║░░░░░██╔══██╗╚██╗░██╔╝██╔════╝██╔══██╗
╚█████╗░░░░██║░░░███████║██████╔╝  ╚█████╗░██║░░░░░███████║░╚████╔╝░█████╗░░██████╔╝
░╚═══██╗░░░██║░░░██╔══██║██╔══██╗  ░╚═══██╗██║░░░░░██╔══██║░░╚██╔╝░░██╔══╝░░██╔══██╗
██████╔╝░░░██║░░░██║░░██║██║░░██║  ██████╔╝███████╗██║░░██║░░░██║░░░███████╗██║░░██║
╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝  ╚═════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝
"""

OPTIONS_TITLE = """

░█████╗░██████╗░████████╗██╗░█████╗░███╗░░██╗░██████╗
██╔══██╗██╔══██╗╚══██╔══╝██║██╔══██╗████╗░██║██╔════╝
██║░░██║██████╔╝░░░██║░░░██║██║░░██║██╔██╗██║╚█████╗░
██║░░██║██╔═══╝░░░░██║░░░██║██║░░██║██║╚████║░╚═══██╗
╚█████╔╝██║░░░░░░░░██║░░░██║╚█████╔╝██║░╚███║██████╔╝
░╚════╝░╚═╝░░░░░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚══╝╚═════╝░
"""

CONTROLS_TITLE = """

░█████╗░░█████╗░███╗░░██╗████████╗██████╗░░█████╗░██╗░░░░░░██████╗
██╔══██╗██╔══██╗████╗░██║╚══██╔══╝██╔══██╗██╔══██╗██║░░░░░██╔════╝
██║░░╚═╝██║░░██║██╔██╗██║░░░██║░░░██████╔╝██║░░██║██║░░░░░╚█████╗░
██║░░██╗██║░░██║██║╚████║░░░██║░░░██╔══██╗██║░░██║██║░░░░░░╚═══██╗
╚█████╔╝╚█████╔╝██║░╚███║░░░██║░░░██║░░██║╚█████╔╝███████╗██████╔╝
░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░╚══════╝╚═════╝░
"""

PROFILES_TITLE = """

██████╗░██████╗░░█████╗░███████╗██╗██╗░░░░░███████╗░██████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝██║██║░░░░░██╔════╝██╔════╝
██████╔╝██████╔╝██║░░██║█████╗░░██║██║░░░░░█████╗░░╚█████╗░
██╔═══╝░██╔══██╗██║░░██║██╔══╝░░██║██║░░░░░██╔══╝░░░╚═══██╗
██║░░░░░██║░░██║╚█████╔╝██║░░░░░██║███████╗███████╗██████╔╝
╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚═╝░░░░░╚═╝╚══════╝╚══════╝╚═════╝░
"""

PLAYER_SPRITE = file_path("star_player.gif", "sprites.player")

PLAYER_DAMAGED_SPRITE = file_path("star_player_damaged.gif", "sprites.player")

KEYS_PATH = file_path("keys.txt")

PROFILES_PATH = file_path("color_profiles.txt")

LEVEL_PATH = file_path("level_{level}.txt", "levels")

LOG_PATH = file_path("thestarthatslays.log")