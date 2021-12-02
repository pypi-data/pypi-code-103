from ..base import ArrayField, NumericField, StringField


class FeatureProfile(object):
    feature_type = StringField("features.profile.featureType")


class Feature(object):
    name = StringField("features.name")
    description = StringField("features.description")
    importance = NumericField("features.importance")
    data_type = ArrayField("features.dataTypeHierarchicalPaths")
    profile = FeatureProfile
