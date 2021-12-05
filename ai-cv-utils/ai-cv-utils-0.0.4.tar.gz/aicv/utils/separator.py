# -*- coding: utf-8 -*-
###############################################################################
#   Copyright (c) 2021 Gaston Alberto Bertolani
#   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
###############################################################################


import random
from shutil import copyfile
from pathlib import Path
from glob import glob
import os

import click


class Separator(object):

    """
    Separate files in train, test and validation folder
    accoirding to the percentages entered
    """

    def __init__(self, samples_path, train_path,
                 validation_path=False, test_path=False,
                 train_perc=0.0, validation_perc=0.0,
                 test_perc=0.0):
        if not train_path and \
                not validation_path and not test_path:
            raise click.ClickException("Target Path is required")
        if not train_perc and \
                not validation_perc and not test_perc:
            raise click.ClickException("Target Perc is required")
        if validation_perc != 0.0 and not validation_path:
            raise click.ClickException("Validation path is required")
        if test_perc != 0.0 and not test_path:
            raise click.ClickException("Test path is required")
        if train_perc < 0.0 or \
                test_perc < 0.0 or validation_perc < 0.0:
            raise click.ClickException("Percentage must be positive")
        total_perc = train_perc + test_perc + validation_perc
        if total_perc != 100.0:
            raise click.ClickException("Total percentage must be 100%%")
        self.samples_path = samples_path
        self.train_path = train_path
        self.validation_path = validation_path
        self.test_path = test_path
        self.train_perc = train_perc
        self.validation_perc = validation_perc
        self.test_perc = test_perc

    def get_target_path(self, percent):
        perc_lst = [
            (self.train_path, self.train_perc),
        ]
        if self.validation_path:
            perc_lst.append((self.validation_path, self.validation_perc))
        if self.test_path:
            perc_lst.append((self.test_path, self.test_perc))
        perc_lst.sort(key=lambda x: x[1], reverse=True)
        accu = 0.0
        for perc_el in perc_lst:
            accu += (perc_el[1] / 100)
            if percent <= accu:
                return perc_el[0]

    def split_samples(self, format=False, remove_source=False):
        if isinstance(format, str):
            format = format.split(',')
        if (not isinstance(format, list) or
                not isinstance(format, tuple)) and format:
            raise click.ClickException("Invalid Format %s." % format)
        if not format:
            # Get all files
            format = ['*.*']
        map_files = {}
        for ft in format:
            if '*.' not in ft:
                ft = '*.' + ft
            for file_path in glob("%s/%s" % (self.samples_path, ft)):
                fpath = Path(file_path)
                if fpath.stem not in map_files:
                    map_files[fpath.stem] = []
                map_files[fpath.stem].append(fpath.suffix)
        # Random selection and random split
        file_name_lst = list(map_files.keys())
        for i in range(0, len(file_name_lst)):
            file_name = random.choice(file_name_lst)
            file_name_lst.remove(file_name)
            perc = random.random()  # [0, 1]
            folder_path = self.get_target_path(perc)
            for ft in map_files[file_name]:
                copyfile(
                    os.path.join(self.samples_path, file_name + ft),
                    os.path.join(folder_path, file_name + ft),
                )
        click.secho("Done!", fg='green', bold=True, blink=True)
