# -*- coding: utf-8 -*-
###############################################################################
#   Copyright (c) 2021 Gaston Alberto Bertolani
#   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
###############################################################################

import click

from utils.remove_background import BackgroundEliminator
from utils.separator import Separator
from utils.yolo_generator import Stage


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def aicv():
    """
    AI CV UTILITIES
    """
    pass


@aicv.command(name='rmbg', context_settings=CONTEXT_SETTINGS,
              short_help='Remove Backgraund of image')
@click.argument('source', required=True, type=click.Path())
@click.argument('target', required=True, type=click.Path())
@click.option('-r', '--no-origin', type=bool,
              help='Remove old images after finish')
@click.option('-g', '--with-groups', type=bool,
              help='Create category folder of image in target folder')
def rmbg(source, target, no_origin=False, with_groups=False):
    """
    Remove Background of image

    SOURCE: Source of image/s (Folder or Image)

    TARGET: Target of image/s (Folder or Image)
    """
    rmb = BackgroundEliminator(
        source,
        save_path=target,
        no_origin=no_origin,
        with_groups=with_groups,
    )
    rmb.remove_background()
    return True


@aicv.command(name='split', context_settings=CONTEXT_SETTINGS,
              short_help='Split files in folders')
@click.argument('source_path', required=True, type=click.Path())
@click.option('-t', '--train', type=click.Path(),
              required=True, help='Path to the "train" folder')
@click.option('-v', '--validation', type=click.Path(),
              required=True, help='Path to the "validation" folder')
@click.option('-x', '--test', type=click.Path(),
              required=True, help='Path to the "test" folder')
@click.option('-T', '--train-perc', type=click.Path(),
              required=False, help='Percent of train folder',
              default=0.0)
@click.option('-V', '--validation-perc', type=click.Path(),
              required=False, help='Percent of validation folder',
              default=0.0)
@click.option('-X', '--test-perc', type=click.Path(),
              required=False, help='Percent of test folder',
              default=0.0)
@click.option('-f', '--format', type=str,
              required=False, help='Format to find files e.g jpg,png,jepg')
@click.option('-r', '--remove', type=bool, default=False,
              required=False, help='Remove Source Files')
def split(source_path, train_path, validation_path, test_path,
          train_perc, validation_perc, test_perc,
          format, remove):
    """
    Searches for files in a certain folder and
    separates them into different folders according
    to a certain percentage

    SOURCE: Source of image/s (Folder or Image)

    """
    sep = Separator(
        source_path, train_path,
        validation_path=validation_path,
        test_path=test_path,
        train_perc=train_perc,
        validation_perc=validation_perc,
        test_perc=test_perc,
    )
    sep.split_samples(
        format=format,
        remove_source=remove,
    )
    return True


@aicv.command(name='yologen', context_settings=CONTEXT_SETTINGS,
              short_help='Generate Stages from images to train')
@click.option('-b', '--background', type=click.Path(),
              required=True, help='Background Path')
@click.option('-s', '--samples', type=click.Path(),
              required=True, help='Path to the "sample" folder')
@click.option('-o', '--output', type=click.Path(),
              required=True, help='Output folder to save images')
@click.option('-q', '--qty', type=int,
              default=1, help='Quantity of stages')
@click.option('-r', '--rgx', type=str,
              help='Regex to get class from image file name')
@click.option('-f', '--format', type=str,
              required=False, help='Format of images',
              default=1.0)
@click.option('-z', '--sample-size', type=float, default=1.0,
              help='Size of samples to paste in background')
@click.option('-d', '--sample-degree', type=int, default=0,
              help='Angle to rotate Sample')
def yologen(background, samples, output, qty, rgx,
            format, sample_size, sample_degree):
    """
    Generate Stages from images to train
    """
    stage = Stage(
        background, samples, output,
        class_rgx=rgx,
        format=format,
        sample_perc_size=sample_size,
        sample_degree=sample_degree,
    )
    stage.generate_random_scenes(num_frames=qty)
    return True


if __name__ == '__main__':
    aicv()
