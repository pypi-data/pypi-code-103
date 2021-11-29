# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from dateutil.parser import parse as parse_datetime
from PIL import Image
from typing import Callable

def timestamp_similarity (max_delta_time: float=6.) -> Callable[[str, str], bool]:
    """
    Create a similarity function which uses temporal proximity as a proxy measure.

    Parameters:
        max_delta_time (float): Maximum exposure time difference for images to be considered similar, in seconds.

    Returns:
        callable: Pairwise image similarity function returning a boolean.
    """
    def similarity_fn (path_a: str, path_b: str) -> bool:
        # Load images
        image_a = Image.open(path_a)
        image_b = Image.open(path_b)
        # Check sizes
        if image_a.size != image_b.size:
            return False
        # Check timestamps
        timestamp_a = exposure_timestamp(image_a)
        timestamp_b = exposure_timestamp(image_b)
        delta_time = abs(timestamp_a - timestamp_b)
        return timestamp_a > 0 and timestamp_b > 0 and delta_time <= max_delta_time
    return similarity_fn

def exposure_timestamp (image: Image.Image) -> float:
    """
    Get the exposure timestamp from its EXIF metadata.

    If the required EXIF dictionary or tag is not present, `-1` will be returned.
    
    Parameters:
        image (PIL.Image): Exposure.
    
    Returns:
        float: Image timestamp.
    """
    DATETIME_ORIGINAL = 36867
    timestamp = image.getexif().get(DATETIME_ORIGINAL)
    if timestamp:
        timestamp = str(timestamp)
        datetime = parse_datetime(timestamp)
        return datetime.timestamp()
    else:
        return -1