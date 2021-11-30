import os

try:
    __PYTEAMTV_SETUP__
except NameError:
    __PYTEAMTV_SETUP__ = False

if not __PYTEAMTV_SETUP__:
    from .api import TeamTVApp, TeamTVUser

    def get_team(name: str):
        if 'TEAMTV_TOKEN' in os.environ:
            app = TeamTVUser(os.environ['TEAMTV_TOKEN'])
            return app.get_team(name)


__version__ = "0.0.1"

