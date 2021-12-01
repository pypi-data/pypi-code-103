import logging
import coloredlogs
import colorama

colorama.init(autoreset=True)

logger = logging.getLogger(__name__)

logger_levelname = f"{colorama.ansi.Style.RESET_ALL}{colorama.Back.WHITE}{colorama.Fore.BLACK}[%(levelname)s]{colorama.ansi.Style.RESET_ALL}"

logger_format = f"{logger_levelname} %(asctime)s %(name)s[%(process)d] %(message)s"

coloredlogs.install(fmt=logger_format, level=logging.DEBUG, logger=logger)
