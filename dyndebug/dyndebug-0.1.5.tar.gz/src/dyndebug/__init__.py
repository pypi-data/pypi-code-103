import os
from loguru import logger
from collections.abc import Callable

def Debug(category: str) -> Callable[[str],bool]:
    debug_setting = os.environ.get("DEBUG")

    if debug_setting != None:
        if category in debug_setting:
            logger.debug(f"Including debug for: {category}")
        else:
            logger.debug(f"Not Including debug for: {category}")

    def debug(message:str):
        if debug_setting == None:
            logger.debug(f"{category}:{message}")
            return True
        else:
            if category in debug_setting:
                logger.debug(f"{category}:{message}")
                return True
        return False

    return debug
