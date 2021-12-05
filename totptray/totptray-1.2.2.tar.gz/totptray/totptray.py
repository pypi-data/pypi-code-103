#!/usr/bin/env python3
"""
Tray icon tool with a TOTP implementation.
Usage:
totptray [title=key]
"""
import sys
import pyperclip
import pystray
import pyotp
from PIL import Image, ImageDraw

from . import __version__

def _create_icon():
    """
    Creates a T-shaped icon.

    :returns: A 64x64 image with "T" in a circle.
    """
    icon_size = 64
    t_width = int(0.3 * icon_size)
    t_height = int(0.4 * icon_size)
    horizontal_margin = int((icon_size - t_width) / 2)
    vertical_margin = int((icon_size - t_height) / 2)

    points = (
        (horizontal_margin, vertical_margin),
        (icon_size - horizontal_margin, vertical_margin),
        (icon_size / 2, vertical_margin),
        (icon_size / 2, icon_size - vertical_margin))

    line_size = int(0.1 * icon_size)
    image = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))

    draw = ImageDraw.Draw(image)
    draw.ellipse([(0, 0), (icon_size, icon_size)], fill="white")
    draw.line(points, fill="black", width=line_size)

    return image

def _copy_code(key):
    """
    Copies a TOTP generated code for the given key to the clipboard.
    :param key: For for which a TOTP code should be generated.
    """
    code = pyotp.TOTP(key).now()
    pyperclip.copy(code)

def _generate_lambda(key):
    """
    Returns a lambda for copying a code for a given key.
    :param key: The key for which the lambda should be generated.
    :returns: Lambda for copying a code for a given key.
    """
    return lambda: _copy_code(key)

def _create_menu(keys):
    """
    Creates a list of menu items for each passed key.
    :param keys: A list of lists with 2 items each. The first item is a label, the second a key.
    :returns: A list of menu items for each passed key.
    """
    assert all(len(key) == 2 for key in keys)
    menu = [pystray.MenuItem(key[0], _generate_lambda(key[1])) for key in keys]
    
    menu.append(pystray.Menu.SEPARATOR)
    menu.append(pystray.MenuItem(f"version: {__version__}", lambda: None, enabled=False ))
    menu.append(pystray.MenuItem("Exit", lambda icon: icon.stop()))
    return menu

def main():
    """
    Creates a tray icon with a menu that allows to copy OTP generated codes.
    """
    assert len(sys.argv) > 1
    assert all(item.count('=') == 1 for item in sys.argv[1:])
    icon = pystray.Icon('totptray', icon=_create_icon(), menu=_create_menu([x.split('=') for x in sys.argv[1:]]))
    icon.run()

if __name__ == '__main__':
    main()
