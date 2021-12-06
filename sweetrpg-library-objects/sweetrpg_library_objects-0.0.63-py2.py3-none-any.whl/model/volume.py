# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import Model


class Volume(Model):
    """A model object representing an RPG volume (digital or print)."""

    def __init__(self, *args, **kwargs):
        """Creates a new Volume object."""
        logging.debug("args: %s, kwargs: %s", args, kwargs)

        super().__init__(*args, **kwargs)

        self.title = kwargs.get("title")
        self.description = kwargs.get("description")
        self.system = kwargs.get("system")
        self.slug = kwargs.get("slug")
        self.properties = kwargs.get("properties")
        self.publisher = kwargs.get("publisher")
        self.tags = kwargs.get("tags")
        # authors: see AuthorVolume
        # studios: see StudioVolume
        # reviews: see VolumeReview
