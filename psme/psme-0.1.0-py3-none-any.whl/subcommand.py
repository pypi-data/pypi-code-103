import argparse

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseSubcommand(ABC):
    @abstractmethod
    def name(self):
        """The name of the subcommand, recommended to be a single, kebab-cased word."""
        pass

    @abstractmethod
    def register_args(self, subparser: argparse.ArgumentParser):
        """Registers the arguments for this given subcommand."""
        pass

    @abstractmethod
    def run(self, args: Dict[str, Any]):
        """Runs the subcommand with the passed arguments."""
        pass
