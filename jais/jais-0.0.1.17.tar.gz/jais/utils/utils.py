import os
import time
import logging
from typing import Any, Tuple, Union
from easydict import EasyDict as edict
from rich import print
from .log import get_logger
from .fileloader import load_yaml, load_json
from jais.__init__ import ROOT_DIR


__all__ = [
    'get_cnf', 'set_cnf', 'get_device', 'install_rich', 'load_default_configs',
]

def get_cnf(key: Union[int, tuple, str], verbose: bool = True) -> Any:
    jais_settings_path = ROOT_DIR/'configs/jais_settings.json'
    # Load settings from file or create empty dict
    JAIS_CNF = load_json(jais_settings_path)
    # Add Current Working Directory path to settings
    try:
        value = JAIS_CNF[key]
        if verbose: 
            print(value)
        return value
    except KeyError:
        print(f"[red]`{key}` not found in `{jais_settings_path}`")

def set_cnf(key: Union[int, tuple, str], value: Any, is_path: bool) -> None:
    """Add key:value pair/item to jais_settings.json"""
    from pathlib import Path
    if is_path:
        value = str(Path(value).resolve())
    from jais.utils.fileloader import load_json, save_json
    jais_settings_path = ROOT_DIR/'configs/jais_settings.json'
    # Load settings from file or create empty dict
    JAIS_CNF = load_json(
        jais_settings_path) if jais_settings_path.exists() else {}
    # Add Current Working Directory path to settings
    JAIS_CNF[key] = value
    # Save back
    save_json(JAIS_CNF, jais_settings_path)
    print(f"Added [bold]{key}:{value}[/bold]")


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
    CNF = load_yaml(f"{ROOT_DIR}/configs/default.yaml")

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