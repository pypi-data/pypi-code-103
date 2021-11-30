"A Rofi script for autorandr"

__version__ = "0.1.0"

from rofi import Rofi
import subprocess

virtual_profiles = [
        "autochange",
        "common",
        "horizontal",
        "vertical",
        "clone-largest",
        ]


def get_all_user_profiles():
    profiles = []
    output = subprocess.check_output(['autorandr'])
    for line in output.decode('utf-8').split('\n'):
        if line:
            profiles.append(line)
    return profiles


def main():
    profiles = virtual_profiles + get_all_user_profiles()
    rofi = Rofi(matching="fuzzy", rofi_args=["-sort"])
    profile = rofi.generic_entry("what profile?", options=profiles)
    if not profile:
        return
    if profile == "autochange":
        subprocess.call(['autorandr', '--change'])
    subprocess.call(['autorandr', '--load', profile.split(' ')[0]])


if __name__ == "__main__":
    main()
