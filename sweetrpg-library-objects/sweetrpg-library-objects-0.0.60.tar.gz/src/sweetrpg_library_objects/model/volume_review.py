# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import Model


class VolumeReview(Model):
    """A model object representing the link between volume and review."""

    def __init__(self, *args, **kwargs):
        """Creates a new VolumeReview object.

        :key str volume: The identifier of the Volume.
        :key str review: The identifier of the Review.
        """
        logging.debug("args: %s, kwargs: %s", args, kwargs)

        super().__init__(*args, **kwargs)

        self.volume = kwargs["volume"]
        self.review = kwargs["review"]
