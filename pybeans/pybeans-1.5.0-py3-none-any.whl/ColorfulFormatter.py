import logging
from colorama import Fore, Back, Style

class ColorfulFormatter(logging.Formatter):

    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.CYAN + " %(levelname)s " + Style.RESET_ALL + " - %(message)s (%(filename)s:%(lineno)d)" + Style.RESET_ALL,
        logging.INFO: Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.WHITE + Back.BLUE + " %(levelname)s " + Style.RESET_ALL + Fore.GREEN + " - %(message)s (%(filename)s:%(lineno)d)" + Style.RESET_ALL,
        logging.WARNING: Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.BLACK + Back.YELLOW + " %(levelname)s " + Style.RESET_ALL + Fore.YELLOW + " - %(message)s (%(filename)s:%(lineno)d)" + Style.RESET_ALL,
        logging.ERROR: Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.WHITE + Back.RED + Style.BRIGHT + " %(levelname)s " + Style.RESET_ALL + Fore.RED + Style.BRIGHT + " - %(message)s (%(filename)s:%(lineno)d)" + Style.RESET_ALL,
        logging.CRITICAL: Style.DIM + "%(asctime)s - %(name)s - " + Style.RESET_ALL + Fore.WHITE + Back.RED + Style.BRIGHT + " %(levelname)s " + Style.RESET_ALL + Fore.RED + Style.BRIGHT + " - %(message)s (%(filename)s:%(lineno)d)" + Style.RESET_ALL,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)