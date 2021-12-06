# -*- coding: utf-8 -*-
__author__ = "Paul Schifferer <dm@sweetrpg.com>"
"""Type registry.
"""

from ..constants import *
from ..types import *
from sweetrpg_library_objects.api.volume.schema import VolumeAPISchema
from sweetrpg_library_objects.api.author.schema import AuthorAPISchema
from sweetrpg_library_objects.api.publisher.schema import PublisherAPISchema
from sweetrpg_library_objects.api.studio.schema import StudioAPISchema
from sweetrpg_library_objects.api.system.schema import SystemAPISchema
from sweetrpg_library_objects.api.tag.schema import TagAPISchema
from sweetrpg_library_objects.api.review.schema import ReviewAPISchema
from sweetrpg_library_objects.model.volume import Volume
from sweetrpg_library_objects.model.author import Author
from sweetrpg_library_objects.model.publisher import Publisher
from sweetrpg_library_objects.model.system import System
from sweetrpg_library_objects.model.studio import Studio
from sweetrpg_library_objects.model.review import Review
from sweetrpg_library_objects.model.tag import Tag


_types = {
    VOLUME: {
        ENDPOINT_PATH: 'volumes',
        API_SCHEMA_CLASS: VolumeAPISchema,
        OBJECT_CLASS: Volume,
    },
    AUTHOR: {
        ENDPOINT_PATH: 'authors',
        API_SCHEMA_CLASS: AuthorAPISchema,
        OBJECT_CLASS: Author,
    },
    TAG: {
        ENDPOINT_PATH: 'tags',
        API_SCHEMA_CLASS: TagAPISchema,
        OBJECT_CLASS: Tag,
    },
    PUBLISHER: {
        ENDPOINT_PATH: 'publishers',
        API_SCHEMA_CLASS: PublisherAPISchema,
        OBJECT_CLASS: Publisher,
    },
    STUDIO: {
        ENDPOINT_PATH: 'studios',
        API_SCHEMA_CLASS: StudioAPISchema,
        OBJECT_CLASS: Studio,
    },
    SYSTEM: {
        ENDPOINT_PATH: 'systems',
        API_SCHEMA_CLASS: SystemAPISchema,
        OBJECT_CLASS: System,
    },
    REVIEW: {
        ENDPOINT_PATH: 'reviews',
        API_SCHEMA_CLASS: ReviewAPISchema,
        OBJECT_CLASS: Review,
    },
}
