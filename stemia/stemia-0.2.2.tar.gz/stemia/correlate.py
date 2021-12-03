from pathlib import Path
from itertools import product

from tqdm import tqdm
import click
import mrcfile
import pandas as pd
import numpy as np

from .functions import cross_correlation, match_pixel_size


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('image1', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.argument('image2', type=click.Path(dir_okay=False, resolve_path=True))
# @click.option('-p', '--percentile', default=0.1, type=float, help='Top scoring percentile to consider good')
#@click.option('-f', '--overwrite', is_flag=True, help='overwrite output if exists')
def main(image1, image2):
    """
    calculate cross correlation values between each pair of 2D slices in image1 and image2
    """
    top = 50
    mrc1 = mrcfile.open(image1)
    mrc2 = mrcfile.open(image2)

    img1, img2 = match_pixel_size(mrc1, mrc2)

    score = []
    combinations = list(product(enumerate(img1), enumerate(img2)))
    score = np.zeros((len(img1), len(img2)))
    try:
        for (i, slice1), (j, slice2) in tqdm(combinations, desc='Progress'):
            cc = cross_correlation(slice1, slice2)
            score[i, j] = cc.max()
    finally:
        np.save('cc_test.npy', score)
