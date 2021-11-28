"""NanamiLang STDLib Manager API"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

import os
import urllib.request


def stdlib_remote_path() -> str:
    """NanamiLang STDLib Manager API, remote stdlib path"""

    return 'https://nanamilang.jedi2light.moe/assets/stdlib.nml'


def ensure_stdlib_local_path() -> str:
    """NanamiLang STDLib Manager API, ensure local stdlib path"""

    home = os.path.join(os.environ.get('XDG_DATA_HOME',
                                       os.environ.get('LOCALAPPDATA')), 'nanamilang')

    if not os.path.exists(home):
        os.mkdir(home)

    return os.path.join(home, 'stdlib.nml')


def populate_nanamilang_stdlib() -> bool:
    """NanamiLang STDLib Manager API, populate NanamiLang STDLib from remote to local"""

    remote_path = stdlib_remote_path()
    local_path = ensure_stdlib_local_path()

    return bool(urllib.request.urlretrieve(remote_path, local_path))
