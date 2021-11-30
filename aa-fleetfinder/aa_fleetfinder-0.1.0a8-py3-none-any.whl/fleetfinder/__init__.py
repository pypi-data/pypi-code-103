"""
init
"""

default_app_config: str = "fleetfinder.apps.FleetFinderConfig"

__title__ = "Fleet Finder"
__version__ = "0.1.0-alpha.8"

__verbose_name__ = "Fleet Finder for Alliance Auth"
__user_agent_name__ = "Fleet-Finder-for-Alliance-Auth"
__user_agent__ = "{verbose_name} v{version} {github_url}".format(
    verbose_name=__user_agent_name__,
    version=__version__,
    github_url="https://github.com/ppfeufer/aa-fleetfinder",
)
