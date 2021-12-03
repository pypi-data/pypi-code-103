import os
import time
import logging
from typing import Optional, Union
from pathlib import Path
from jais.__init__ import ROOT_DIR


__all__ = [
    'get_logger', 'manage_log_files'
]

def get_logger(name: str,
               logs_dir: Optional[Union[str, Path]] = None,
               log_filename: Optional[Union[str, Path]] = None,
               logs_conf_filepath: Union[str, Path] = None,
               level: Optional[str] = None,
               keep_n_recent_logs: int = 5,
               rich_logger: bool = True,
               colored_logger: bool = False) -> logging.Logger:
    """Create a colored logger with two handlers (stream and file logging)
        from logs.conf

    Args:
        name: name of the logger.
        logs_dir: folder path where logs will be saved. 
            [Default is to save in the current working directory]
        log_filename: Name of the logs file (with extension `.log`).
            [Default name is `logs@<current time>.logs`]
        logs_conf_filepath: Logs configuration filepath. 
            [Default is jais/configs/logs.conf]
        level: override JAISLogger.StreamHandler logging level: 
            ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].
            Default is loaded from the file.
        keep_n_recent_logs: Number of recent log files to keep. 
            New files will overwrite old ones. [Default = 5]
        rich_logger: Use `RichHandler` logger for colored logs
        colored_logger: Use `coloredlogs` logger for colored logs.
            Mutually exclusive to rich_logger.
    Returns:
        Colored logger instance with settings loaded from `configs/logs.conf`
    """
    if (rich_logger == True) and (colored_logger == True):
        _errmsg = "Both `rich_logger` and `colored_logger` cannot be\
             True at the same time."
        raise ValueError(_errmsg)

    import configparser  # To read logs.conf file
    import logging
    import logging.config
    if logs_conf_filepath is None:
        logs_conf_filepath = ROOT_DIR/"configs/logs.conf"
    logs_conf = configparser.RawConfigParser()
    logs_conf.read(logs_conf_filepath)
    if f'logger_{name}' in logs_conf.keys():
        default_level = logs_conf[f'logger_{name}']['level']
    else:
        default_level = 'DEBUG'
    if logs_dir is None:
        logs_dir = Path.cwd()/f"{name}_logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
    else:
        logs_dir = Path(logs_dir)
    if log_filename is None:       
        log_filename = Path(logs_dir)/f"log@{time.time()}.logs"
    logging.config.fileConfig(logs_conf_filepath,
                              defaults={'logfilepath': logs_dir/log_filename},
                              disable_existing_loggers=True)
    # Create logger
    logger = logging.getLogger(name)
    # Override logging level
    if level:
        logger.setLevel(level)
        default_level = level

    if rich_logger:
        # Existing StreamHandler needs to be removed, if present.
        existing_handlers = [
            handler for handler in logger.handlers
            if isinstance(handler, logging.FileHandler)
        ]
        logger.handlers.clear()
        logger.handlers = existing_handlers
        # Add RichHandler
        from rich.logging import RichHandler
        ch = RichHandler(level=default_level,
                         show_time=False,
                         rich_tracebacks=True)
        ch.setLevel(default_level)
        formatter = logging.Formatter('%(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    elif colored_logger:
        try:
            import coloredlogs
        except:
            print('`coloredlogs` not installed. Use `pip install coloredlogs`')
        # StreamLogger format settings for coloredlogs
        stream_fmt = '[%(programname)s - %(levelname)s] %(message)s'
        # Set colored logs
        coloredlogs.install(level=default_level, fmt=stream_fmt, logger=logger)

    manage_log_files(logs_dir=logs_dir, 
                     keep_n_recent_logs=keep_n_recent_logs,
                     file_ext='.log')
    return logger


def manage_log_files(logs_dir: Union[str, Path], 
                     keep_n_recent_logs: int = 5, 
                     file_ext: str = '.log'):
    """Log files rotation handler"""
    # Get log files paths
    log_filespaths = list(Path(logs_dir).glob(f"*{file_ext}"))
    # Function to split the timestamp from filepath
    def get_time_from_filename(x):
        try:
            return float(x.stem.split('@')[-1])
        except ValueError:
            return None
            
    # Sort timestamps
    timestamps = sorted(
        filter(
            lambda x: False if x is None else True, 
            list(map(get_time_from_filename, log_filespaths))
        ),
        reverse=True)
    # Keep only n recent files
    timestamps = timestamps[ : keep_n_recent_logs]
    # Remove old files
    for fp in log_filespaths:
        if get_time_from_filename(fp) not in timestamps:
            os.remove(fp)
