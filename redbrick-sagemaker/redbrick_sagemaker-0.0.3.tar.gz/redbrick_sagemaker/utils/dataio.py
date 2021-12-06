"""Helper functions for data io operations."""

import os
from typing import Dict

import imageio
import tqdm

from redbrick_sagemaker.logging import logger


def download_images_from_remote(cache_dir: str, prefix: str, tasks: Dict):
    """
    Download locally preparing for s3 upload for inference.

    Parameters
    -------------
    cache_dir: str
        Where images get cached

    prefix: str
        Sub-folder

    tasks: Dict
        RedBrick AI tasks.
    """
    os.makedirs(os.path.join(cache_dir, prefix), exist_ok=True)
    for task in tqdm.tqdm(tasks):
        # Download, if not already do
        local_path = os.path.join(cache_dir, prefix, str(task["taskId"]) + ".png")
        if os.path.exists(local_path):
            continue

        try:
            image = imageio.imread(task["itemsPresigned"][0])
        except (ValueError, OSError):
            logger.warning("Failed to download %s", task["items"])

        # Write to disk
        try:
            imageio.imwrite(
                os.path.join(local_path),
                image,
            )
        except (ValueError, OSError):
            logger.warning("Failed to download %s", task["items"][0])
