"""Model (dataclass) writer
"""

import csv
import os
import logging
from dataclasses import asdict
from typing import Dict, Iterable, Sequence, TextIO, Type

logger = logging.getLogger(__name__)


def get_fieldnames(dclass: Type) -> Sequence[str]:
    """Get fieldnames for a specified dataclass type"""
    if not hasattr(dclass, "__dataclass_fields__"):
        raise ValueError(f"{dclass.__name__} is not a dataclass")
    return [field for field in dclass.__dataclass_fields__.keys() if not field.startswith("__")]


# pylint: disable=too-few-public-methods
class ModelWriter:
    """A model (dataclass) writer

    This class allows you to create a proxy to multiple csv files at once. By calling
    writerow(<dataclass-instance>) ModelWriter will automatically find out
    what output file to choose and will serialize the dataclass instance into
    a valid csv line.
    """

    def __init__(self, output_path: str, models: Sequence[Type]):
        if not all((hasattr(dclass, "__filename__") for dclass in models)):
            raise TypeError("Only models with __filename__ are supported")
        self.models = models
        self.output_path = output_path
        self.handles: Dict[Type, TextIO] = {}
        self.writers: Dict[Type, csv.DictWriter] = {}

    def __enter__(self):
        """Enter context manager"""
        logger.info("Initiating dataclass writer")
        for dclass in self.models:
            path = os.path.join(self.output_path, dclass.__filename__)
            self.handles[dclass] = open(path, "w", encoding="utf-8", newline="")
            self.writers[dclass] = csv.DictWriter(
                self.handles[dclass], fieldnames=get_fieldnames(dclass), dialect=csv.unix_dialect
            )
            self.writers[dclass].writeheader()
            logger.info("Preparing %s for writing dataclass '%s'", path, getattr(dclass, "__name__", str(dclass)))
        return self

    def __exit__(self, *args):
        """Exit context manager"""
        for handle in self.handles.values():
            handle.close()
        logger.info("All files closed")

    def writerow(self, model):
        """Write line using writer associated with dclass"""
        if not self.writers:
            raise TypeError("Context manager was not entered")
        self.writers[model.__class__].writerow(asdict(model))

    def writerows(self, models: Iterable):
        """Writer rows using writer associated with dclass"""
        if not self.writers:
            raise TypeError("Context manager was not entered")
        for item in models:
            self.writerow(item)
