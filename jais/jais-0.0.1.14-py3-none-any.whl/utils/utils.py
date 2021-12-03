import os
import time
import logging
from typing import Tuple
from easydict import EasyDict as edict
from .log import get_logger
from .fileloader import load_yaml
from jais.__init__ import ROOT_DIR

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