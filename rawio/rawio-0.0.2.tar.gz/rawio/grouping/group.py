# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from typing import Callable, List

from .timestamp import exposure_timestamp

def group_exposures (exposure_paths: List[str], similarity_fn: Callable[[str, str], bool], workers: int=8) -> List[List[str]]:
    """
    Group a set of exposures using a similarity function.

    Parameters:
        exposure_paths (list): Paths to exposures to group.
        similarity_fn (callable): Pairwise similarity function returning a boolean.
        workers (int): Number of workers for IO.
    
    Returns:
        list: Groups of exposure paths.
    """
    # Check
    if not exposure_paths:
        return []
    # Trivial case
    if len(exposure_paths) == 1:
        return [exposure_paths]
    # Sort by timestamp # This should preserve order if no timestamps
    paths_with_images = [(path, Image.open(path)) for path in exposure_paths]
    paths_with_images = sorted(paths_with_images, key=lambda pair: exposure_timestamp(pair[1]))
    exposure_paths, _ = list(zip(*paths_with_images))
    # Compute pairwise similarities
    with ThreadPoolExecutor(max_workers=workers) as executor:
        path_pairs = [(exposure_paths[i], exposure_paths[i+1]) for i in range(len(exposure_paths) - 1)]
        similarities = executor.map(lambda pair: similarity_fn(*pair), path_pairs)
        similarities = list(similarities) # Prevent re-evaluation when debugging
    # Group
    groups = []
    current_group = [exposure_paths[0]]
    for i, similar in enumerate(similarities):
        if not similar:
            groups.append(current_group)
            current_group = []
        current_group.append(exposure_paths[i+1])
    groups.append(current_group)
    return groups