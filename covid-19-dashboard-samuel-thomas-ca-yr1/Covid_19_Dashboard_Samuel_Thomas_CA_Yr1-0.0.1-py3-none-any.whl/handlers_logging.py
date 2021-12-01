"""[A module to create logging file for covid_data_interface]
    [covid_data_handler and news_data_handling]
"""
import logging

# Ceating my logging file for the flask interface
logger_interface = logging.getLogger('Logger_Interface')
logger_interface.setLevel(logging.DEBUG)
filehandler_logger_interface = logging.FileHandler('interface_logging.log')
format_logger_interface = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s')
filehandler_logger_interface.setFormatter(format_logger_interface)
logger_interface.addHandler(filehandler_logger_interface)


# Ceating my logging file for the covid handler
logger_covid_handler = logging.getLogger('logger_covid_handler')
logger_covid_handler.setLevel(logging.DEBUG)
filehandler_logger_covid_handler = logging.FileHandler(
    'logger_covid_handler.log')
format_logger_covid_handler = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s')
filehandler_logger_covid_handler.setFormatter(format_logger_covid_handler)
logger_covid_handler.addHandler(filehandler_logger_covid_handler)

logger_news_handler = logging.getLogger('logger_news_handler')
logger_news_handler.setLevel(logging.DEBUG)
filehandler_logger_news_handler = logging.FileHandler(
    'logger_news_handler.log')
format_logger_news_handler = logging.Formatter(
    '%(asctime)s:%(levelname)s:%(module)s:%(funcName)s:%(lineno)d:%(message)s')
filehandler_logger_news_handler.setFormatter(format_logger_news_handler)
logger_news_handler.addHandler(filehandler_logger_news_handler)
