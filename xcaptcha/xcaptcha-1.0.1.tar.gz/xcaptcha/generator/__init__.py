from typing import Callable, List, Tuple
import numpy as np

from .captcha_generator import CAPTCHAGenerator


def generate_captchas(charset: str, min_size: Tuple[int, int], max_size: Tuple[int, int],
                      min_length: int, max_length: int, fonts: List[str]) -> CAPTCHAGenerator:
    """
    Creates an infinite iterable of CAPTCHA objects.

    The min/max size parameters describe the range of CAPTCHA sizes
    to be generated, in (rows, cols) format, while the transformations
    describe the obfuscation to apply to the image. The min/max length
    parameters describe the number of characters that should be included
    in the CAPTCHA sequence.
    """

    # Validation
    assert(min_length >= 0)
    assert(min_length < max_length)

    assert(len(charset) > 0)
    assert(len(fonts) > 0)

    assert(min_size[0] > 0)
    assert(min_size[1] > 0)
    assert(max_size[0] > 0)
    assert(max_size[1] > 0)

    return CAPTCHAGenerator(charset, min_size, max_size, min_length, max_length, fonts)
