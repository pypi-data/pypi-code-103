import os
import pwd
import FamcyTools

def get_username():
    return pwd.getpwuid(os.getuid())[0]

USERNAME = get_username()
# TODO: in the future, this needs to be more modular
FAMCY_DIR = "/home/%s/.local/share/famcy/%s/venv/lib/python3.7/site-packages/Famcy"
FAMCYTOOLS_DIR = os.path.dirname(FamcyTools.__file__)