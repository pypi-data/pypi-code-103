"""This module contains some useful functions which can be used throughout 
the project.
"""

import os
import time
import click
import logging
from rich import print
from typing import Any, Callable, Tuple, Union, Dict, Optional
from ruamel.yaml import YAML, yaml_object
from itertools import cycle
from shutil import get_terminal_size
from pathlib import Path
from easydict import EasyDict as edict
from collections import OrderedDict
from jais.__init__ import JAIS_CWD, ROOT_DIR


__all__ = [
    # Configuration handlers
    'load_config', 'save_config',

    # Functions
    'get_recent_githash', 'get_logger', 'get_device', 'install_rich',
    'load_default_configs',

    # Classes
    'SpinCursor',

    # Decorators
    'show_exec_time',
]

# ======================= CONFIGURATION HANDLERs ===========================

# * When using the decorator, which takes the YAML() instance as a parameter,
# * the yaml = YAML() line needs to be moved up in the file -- *yaml docs*
yaml = YAML(typ='safe', pure=True)
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)

@yaml_object(yaml)
class JoinPath:
    """Custom tag `!join` loader class to join strings for yaml file."""

    yaml_tag = u'!joinpath'

    def __init__(self, joined_string):
        self.joined_string = joined_string

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.joined_string}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        seq = constructor.construct_sequence(node)
        fullpath = Path('/'.join([str(i) for i in seq])).resolve()
        if len(str(fullpath.name).split(".")) == 1:  # This is a directory
            fullpath.mkdir(parents=True, exist_ok=True)
            # Create a empty .gitkeep file to keep the empty folder structure
            # in git repo
            if len(list(fullpath.glob("**/*"))) == 0:
                (fullpath/".gitkeep").touch(mode=0o666, exist_ok=True)
        return str(fullpath)


@yaml_object(yaml)
class RootDirSetter:
    """Custom tag `!rootdir` loader class for yaml file."""

    yaml_tag = u'!rootdir'

    def __init__(self, path):
        self.path = path

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.path}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        return str(ROOT_DIR)


@yaml_object(yaml)
class CWDSetter:
    """Custom tag `!cwd` loader class for yaml file."""
 
    yaml_tag = u'!cwd'  # Current Working Directory

    def __init__(self, path):
        self.path = path

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.path}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        return str(JAIS_CWD)


@yaml_object(yaml)
class HomeDirSetter:
    """Custom tag `!homedir` loader class for yaml file."""

    yaml_tag = u'!homedir'

    def __init__(self, path):
        self.path = path

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.path}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        return str(Path.home())


def load_config(path: Union[str, Path], pure: bool = False) -> dict:
    """config.yaml file loader.

    This function converts the config.yaml file to `dict` object.

    Args:
        path: .yaml configuration filepath
        pure: If True, just load the .yaml without converting to EasyDict
            and exclude extra info.

    Returns:
        `dict` object containing configuration parameters.

    Example:
        .. code-block:: python

            config = load_config("../config.yaml")
            print(config["project_name"])
    """

    path = str(Path(path).absolute().resolve())
    # * Load config file
    with open(path) as file:
        config = yaml.load(file)

    if pure == False:  # Add extra features
        # Convert dict to easydict
        config = edict(config)
    return config


def save_config(config_dict: Dict, path: Union[str, Path] = None,
                saveas_ordered: bool = True, force_overwrite: bool = False,
                file_extension: str = 'yaml') -> None:
    """save `dict` config parameters to `.yaml` file

    Args:
        config_dict: parameters to save.
        path: path/to/save/auto_config.yaml.
        saveas_ordered: save as collections.OrderedDict on Python 3 and 
            `!!omap` is generated for these types.
        file_extension: default `.yaml`

    Returns: 
        nothing

    Example:
        .. code-block:: python

            config = {"Example": 10}
            save_config(config, "../auto_config.yaml")
    """

    if path is None:  # set default path if not given
        path = config_dict.paths.output_dir
        path = f"{path}/modified_config.{file_extension}"
    else:
        path = str(Path(path).absolute().resolve())
        # Check if the path given is the original config's path
        if (config_dict.original_config_filepath == path) and \
           (not force_overwrite):
            msg = f"""
            Error while saving config file @ {path}.
            Cannot overwrite the original config file
            Choose different save location.
            """
            raise ValueError(msg)

    # converting easydict format to default dict because
    # YAML does not processes EasyDict format well.
    cleaned_dict = {
        k: edict_to_dict_converter(v)
        for k, v in config_dict.items()
    }
    # print("cleaned_dict =", cleaned_dict)

    # Fix order
    if saveas_ordered:
        cleaned_dict = OrderedDict(cleaned_dict)

    # Save the file to given location
    with open(path, 'w') as file:
        yaml.dump(cleaned_dict, file)

    print(f"config saved @ {path}")


def edict_to_dict_converter(x: Union[Dict, Any]) -> Union[Dict, Any]:
    """Recursive function to convert given dictionary's datatype
    from edict to dict.

    Args:
        x (dict or other): nested dictionary

    Returns: x (same x but default dict type)
    """
    if not isinstance(x, dict):
        return x

    # Recursion for nested dicts
    ndict = {}
    for k, v in x.items():
        v1 = edict_to_dict_converter(v)
        ndict[k] = v1
    return ndict


# ============================== CLASSES ==============================
class SpinCursor:
    """A waiting animation when program is being executed. 

        `reference source (stackoverflow) <https://stackoverflow.com/questions/22029562/python-how-to-make-simple-animated-loading-while-process-is-running>`_ 

        Args:
            desc : The loader's description. Defaults to "Loading...".
            end : Final print. Defaults to "Done!".
            cursor_type : Set the animation type. Choose one out of
                'bar', 'spin', or 'django'.
            timeout : Sleep time between prints. Defaults to 0.1.

        Example:
            Using *with* context:

            .. code-block:: python

                with SpinCursor("Running...", end=f"done!!"):
                    subprocess.run(['ls', '-l'])
                    time.sleep(10)

            Using normal code:

            .. code-block:: python

                cursor = SpinCursor("Running...", end=f"done!!")
                cursor.start()
                subprocess.run(['ls', '-l'])
                time.sleep(10)
                cursor.stop()

        Returns: 
            Nothing
        """

    def __init__(self, desc: str = "Loading...", end: str = "Done!", cursor_type: str = "bar", timeout: float = 0.1) -> None:
        from threading import Thread
        self.desc = desc
        self.end = end
        self.timeout = timeout

        self._thread = Thread(target=self._animate, daemon=True)

        if cursor_type == 'bar':
            self.steps = [
                "[=     ]",
                "[ =    ]",
                "[  =   ]",
                "[   =  ]",
                "[    = ]",
                "[     =]",
                "[    = ]",
                "[   =  ]",
                "[  =   ]",
                "[ =    ]",
            ]
        elif cursor_type == 'spin':
            self.steps = ['|', '/', '-', '\\']
        elif cursor_type == 'django':
            self.steps = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
        else:
            raise NotImplementedError("choose one [`spin`, `bar`, `django`].")

        self.done = False

    def start(self) -> object:
        """Start the animation. See example above."""
        self._thread.start()
        return self

    def _animate(self) -> None:
        for c in cycle(self.steps):
            if self.done:
                break
            print(click.style(f"\r{self.desc} {c}",
                  fg='yellow'), flush=True, end="")
            time.sleep(self.timeout)

    def __enter__(self) -> None:
        self.start()

    def stop(self) -> None:
        """Stop animation. See example above."""
        self.done = True
        cols = get_terminal_size((80, 20)).columns
        print("\r" + " " * cols, end="", flush=True)
        print(click.style(f"\r{self.end}", fg='green'), flush=True)

    def __exit__(self, exc_type, exc_value, tb):
        # handle exceptions with those variables ^
        self.stop()


# ============================== DECORATORS ==============================
def show_exec_time(func: Callable) -> Any:
    """Display the execution time of a function.

        This decorator is suited to large programs that takes
            more than a second to run.

        Example:

            .. code-block:: python

                @show_exec_time
                def take_a_break(timeout=10):
                    time.sleep(timeout)

                >>> take_a_break()
                >>> >> Completed in 00h:00m:10s <<
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()

        # Run the given function
        results = func(*args, **kwargs)

        end_time = time.time()

        hrs = (end_time - start_time) // 3600
        rem = (end_time - start_time) % 3600
        mins = rem // 60
        secs = rem % 60

        hrs = str(round(hrs)).zfill(2)
        mins = str(round(mins)).zfill(2)
        secs = str(round(secs)).zfill(2)

        print(f"\n>> Completed in {hrs}h:{mins}m:{secs}s <<\n")

        return results
    return wrapper


# ============================= FUNCTIONS ==============================
def get_recent_githash():
    """Get the recent commit git hash"""
    import subprocess
    proc = subprocess.Popen(["git", "rev-parse", "HEAD"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return proc.stdout.read().strip().decode('ascii')


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
        import coloredlogs
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


def get_device():
    """Get torch device instance and available GPU IDs"""
    from torch.cuda import device_count
    from torch import device
    cuda_ids = [0] if device_count() == 1 else list(range(device_count()))
    return device(f"cuda:{cuda_ids[0]}"), cuda_ids


def install_rich(verbose: bool = False):
    """Enable Rich to override Python """
    from rich import pretty, traceback
    from rich import print
    import click
    pretty.install()
    # If you are working with a framework (click, django etc),
    # you may only be interested in seeing the code from your own
    # application within the traceback. You can exclude framework
    # code by setting the suppress argument on Traceback, install,
    # and Console.print_exception, which should be a list of modules
    # or str paths.
    traceback.install(show_locals=False, suppress=[click])
    if verbose:
        print("[cyan]Rich set to override print and tracebacks.")


def load_default_configs() -> Tuple[edict, logging.Logger]:
    """Load jais package configuration settings and logger"""
    install_rich(verbose=False)
    # Load configurations
    CNF = load_config(f"{ROOT_DIR}/configs/default.yaml")

    # Set logger settings
    LOG_FILENAME = os.getenv('JAIS_LOG_FILENAME')
    if LOG_FILENAME is None:
        LOG_FILENAME = f"{CNF.log.filename_prefix}@{time.time()}.log"
        os.environ['JAIS_LOG_FILENAME'] = LOG_FILENAME

    LOG = get_logger(name=CNF.log.name, 
                     logs_dir=CNF.paths.logs_dir,
                     log_filename=LOG_FILENAME,
                     logs_conf_filepath=f"{ROOT_DIR}/configs/logs.conf",
                     keep_n_recent_logs=CNF.log.keep_n_recent_logs
                     )

    return CNF, LOG
