"""This module configures the monitors depending on how many displays there
are.
"""

from libqtile.config import Screen
from stonecharioteer.qtile.panels import default_top_bar, default_bottom_bar
from stonecharioteer.utils.display import get_display_info


def configure_screens():
    """This function configures the screens based on how many active
    monitors there are currently."""
    displays = get_display_info()

    default_screen = Screen(
        top=default_top_bar,
        bottom=default_bottom_bar,
    )

    screens = [default_screen]
    if len(displays) > 1:
        for display in displays:
            display_name = display["name"]
            if display_name == "eDP":
                continue
            else:
                screen = Screen(bottom=default_bottom_bar)
                screens.append(screen)
    return screens
