from typing import Dict

from piter.config import config
from piter.env.env import Env

ENVIRONMENTS: Dict[str, Env] = {name: Env(name) for name in config.env.keys()}
