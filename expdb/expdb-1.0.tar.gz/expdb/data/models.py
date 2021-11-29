"""Dataclass for exporting binary files"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from typing import List, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class BinExport():
    """Dataclass for exporting tables in binary format"""
    database: str
    table: str
    columns: Tuple[any]
    rows: List[Tuple[any]]
    timestamp: str = str(datetime.now())
