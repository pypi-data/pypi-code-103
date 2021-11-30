from .. import __version__
from . import configure
from . import log
from . import tools
from . import errors
from . import core
from . import content
from . import delivery
from . import pricing
from . import fin_coder_layer

import sys

logger = log.root_logger
logger.debug(f"RD version is {__version__}; Python version is {sys.version}")

try:
    import pkg_resources

    installed_packages = pkg_resources.working_set
    installed_packages = sorted([f"{i.key}=={i.version}" for i in installed_packages])
    logger.debug(
        f"Installed packages ({len(installed_packages)}): "
        f"{','.join(installed_packages)}"
    )
except Exception as e:
    logger.debug(f"Cannot log installed packages, {e}")

logger.debug(f'Read configs: {", ".join(configure._config_files_paths)}')
