# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from imagehash import whash
from PIL import Image
from typing import Callable

def wavelet_similarity (hamming_threshold: float=0.15) -> Callable[[str, str], bool]:
    """
    Create a similarity function which compares Wavelet-domain hashes between images.

    Parameters:
        hamming_threshold (float): Maximum relative hamming distance between hashes for images to be considered similar, in range [0., 1.].

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
        # Compute hashes
        hash_a = whash(image_a, hash_size=256)
        hash_b = whash(image_b, hash_size=256)
        # Compute delta
        hamming_distance = hash_a - hash_b
        relative_distance = hamming_distance / len(hash_a.hash) ** 2
        return relative_distance <= hamming_threshold
    return similarity_fn