# -*- coding: utf-8 -*-
__studio__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import Model


class StudioVolume(Model):
    """A model object representing the link between studio and volume."""

    def __init__(self, *args, **kwargs):
        """Creates a new StudioVolume object.

        :key str studio: The identifier of the Studio.
        :key str volume: The identifier of the Volume.
        """
        logging.debug("args: %s, kwargs: %s", args, kwargs)

        super().__init__(*args, **kwargs)

        self.studio = kwargs["studio"]
        self.volume = kwargs["volume"]
