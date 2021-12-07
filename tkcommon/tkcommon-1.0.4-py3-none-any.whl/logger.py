import watchtower, logging


def get_logger(name, level="INFO"):
    """common formated logger

    :param name: name of the logger
    :type name: str
    :param level: level of the logger(INFO,ERROR,DEBUG,WARNING,FATAL)
    :type level: str
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    channel = logging.StreamHandler()
    channel.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(levelname)-4s %(asctime)-4s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )
    channel.setFormatter(formatter)
    logger.addHandler(channel)
    logger.addHandler(watchtower.CloudWatchLogHandler())
    return logger
