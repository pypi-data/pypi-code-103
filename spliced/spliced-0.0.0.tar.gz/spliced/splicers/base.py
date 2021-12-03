# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spliced.logger import logger

import os
import re

class Splicer:
    """
    A splicer can be used to run a splice and make a prediction.
    """

    def predict(self):
        raise NotImplementedError

    def __str__(self):
        return str(self.__class__.__name__)
