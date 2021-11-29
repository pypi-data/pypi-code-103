# flake8: noqa
from yams.buildobjs import *


class equivalent_uri(RelationDefinition):  # type: ignore
    subject = "*"
    object = ("ExternalUri",)
    cardinality = "*?"


class label(RelationDefinition):  # type: ignore
    subject = "*"
    object = "Label"
    cardinality = "*?"


class Label(EntityType):  # type: ignore
    value = String(required=True)  # type: ignore
