# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""
"""

import logging
from sweetrpg_model_core.model.base import Model


class Review(Model):
    """A model object representing a review for a Volume."""

    def __init__(self, *args, **kwargs):
        """Creates a new Review object.

        :key str title: The title of the review.
        :key str text: The text of the review.
        :key str locale: The locale of the review's contents.
        :key str volume: The volume ID to which this review belongs.
        """
        logging.debug("args: %s, kwargs: %s", args, kwargs)

        super().__init__(*args, **kwargs)

        self.title = kwargs.get("title")
        self.text = kwargs.get("text")
        self.locale = kwargs.get("locale")
        self.volume = kwargs.get("volume")
        self.tags = kwargs.get("tags")
