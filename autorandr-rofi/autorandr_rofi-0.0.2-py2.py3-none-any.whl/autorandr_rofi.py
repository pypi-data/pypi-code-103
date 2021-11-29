"A Rofi script for autorandr"

__version__ = "0.0.2"

from rofi import Rofi
import subprocess
virtual_profiles = [
        "--change",
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
    profiles = get_all_user_profiles()
    profiles.extend(virtual_profiles)
    rofi = Rofi()
    index, _ = rofi.select("what profile?", profiles)
    if index == -1:
        return
    print(index)
    profile = profiles[index]
    if profile == "--change":
        subprocess.call(['autorandr', '--change'])
    else:
        subprocess.call(['autorandr', '--load', profile.split(' ')[0]])


if __name__ == "__main__":
    main()
