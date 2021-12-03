# Copyright 2013-2021 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# An experiment loads in a splice setup, and runs a splice session.

# TODO can we run in parallel?

import spliced.schemas
import spliced.utils as utils
import jsonschema
import re


class Experiment:
    def load(self, config_file, validate=True):
        self.config = utils.load_yaml(config_file)
        self.config_file = config_file
        if validate:
            self.validate()

    def validate(self):
        jsonschema.validate(instance=self.config, schema=spliced.schemas.spliced_schema)

    @property
    def package(self):
        return self.config.get("package")

    @property
    def splice(self):
        return self.config.get("splice")

    @property
    def command(self):
        return self.config.get("command")

    @property
    def experiment(self):
        return os.path.basename(self.config_file).split(".")[0]

    @property
    def replace(self):
        return self.config.get("replace") or self.splice
