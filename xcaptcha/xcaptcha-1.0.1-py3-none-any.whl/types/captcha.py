from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class CAPTCHA():
    """Container class for generated CAPTCHA data."""
    image: np.ndarray
    masks: Dict[str, np.ndarray]
    solution: str
