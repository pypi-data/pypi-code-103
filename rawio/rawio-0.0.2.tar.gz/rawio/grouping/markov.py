# 
#   RawIO
#   Copyright (c) 2021 Yusuf Olokoba.
#

from cv2 import findTransformECC, MOTION_TRANSLATION, TERM_CRITERIA_COUNT, TERM_CRITERIA_EPS
from numpy import asarray, eye, float32
from PIL import Image
from sklearn.feature_extraction.image import extract_patches_2d
from typing import Callable

def markov_similarity (min_probability: float=0.8, trials: int=100, patch_size: float=0.1) -> Callable[[str, str], bool]:
    """
    Create a similarity function which estimates a binomial distribution on a Markov random field defined over the image.

    In simple terms, it checks for patch correspondences :/
    We use Evangelidis & Psarakis, 2008 with Monte Carlo simulation to estimate the binomial distribution.

    Parameters:
        min_probability (float): Minimum probability for images to be considered similar, in range [0., 1.].
        trials (int): Number of Monte Carlo trials for estimating the binomial distribution.
        patch_size (float): Relative patch size for ECC trials, in range [0., 1.].

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
        # Load images
        image_a.draft("L", (2560, 1440))
        image_b.draft("L", (2560, 1440))
        image_a = asarray(image_a)
        image_b = asarray(image_b)
        # Extract patches
        SEED = 1
        size = int(min(image_a.shape) * patch_size)
        patches_a = extract_patches_2d(image_a, (size, size), max_patches=trials, random_state=SEED)
        patches_b = extract_patches_2d(image_b, (size, size), max_patches=trials, random_state=SEED)
        # Run Monte Carlo estimation
        IDENTITY = eye(2, 3, dtype=float32)
        CRITERIA = (TERM_CRITERIA_EPS | TERM_CRITERIA_COUNT, 50, 1e-4)
        passes = 0
        for patch_a, patch_b in zip(patches_a, patches_b):
            try:
                findTransformECC(patch_a, patch_b, IDENTITY.copy(), MOTION_TRANSLATION, CRITERIA, None, 5)
                passes += 1
            except:
                pass
        # Check
        estimator = passes / patches_a.shape[0]
        return estimator >= min_probability
    return similarity_fn