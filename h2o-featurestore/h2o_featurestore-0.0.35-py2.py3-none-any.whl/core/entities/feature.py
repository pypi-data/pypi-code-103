from .. import CoreService_pb2 as pb
from ..utils import Utils

CATEGORICAL = pb.FeatureType.Categorical
NUMERICAL = pb.FeatureType.Numerical
TEMPORAL = pb.FeatureType.Temporal
TEXT = pb.FeatureType.Text


class Feature:
    def __init__(self, feature):
        self._feature = feature

    @property
    def name(self):
        return self._feature.name

    @property
    def version(self):
        return self._feature.version

    @property
    def special(self):
        return self._feature.special

    @special.setter
    def special(self, value):
        self._feature.special = value

    @property
    def version_change(self):
        return self._feature.version_change

    @version_change.setter
    def version_change(self, value):
        self._feature.version_change = value

    @property
    def status(self):
        return self._feature.status

    @status.setter
    def status(self, value):
        self._feature.status = value

    @property
    def data_type(self):
        return self._feature.data_type

    @property
    def profile(self):
        return FeatureProfile(self._feature)

    @property
    def description(self):
        return self._feature.description

    @description.setter
    def description(self, value):
        self._feature.description = value

    @property
    def importance(self):
        return self._feature.importance

    @importance.setter
    def importance(self, value):
        self._feature.importance = value

    @property
    def monitoring(self):
        return self._feature.monitoring

    def __repr__(self):
        return Utils.pretty_print_proto(self._feature)


class FeatureProfile:
    def __init__(self, feature):
        self._feature = feature
        self._profile = self._feature.profile

    @property
    def feature_type(self):
        return self._profile.feature_type

    @feature_type.setter
    def feature_type(self, value):
        self._profile.feature_type = pb.FeatureType.Name(value).title()

    @property
    def categorical_statistics(self):
        return self._profile.categorical

    @property
    def statistics(self):
        return self._profile.statistics

    def __repr__(self):
        return Utils.pretty_print_proto(self._profile)


class FeatureStatistics:
    def __init__(self, feature):
        self._feature = feature
        self._stats = self._feature.categorical

    @property
    def max(self):
        return self._stats.max

    @property
    def mean(self):
        return self._stats.mean

    @property
    def median(self):
        return self._stats.median

    @property
    def min(self):
        return self._stats.min

    @property
    def stddev(self):
        return self._stats.stddev

    @property
    def stddev_rec_count(self):
        return self._stats.stddev_rec_count

    @property
    def null_count(self):
        return self._stats.null_count

    @property
    def nan_count(self):
        return self._stats.nan_count

    @property
    def unique(self):
        return self._stats.unique

    def __repr__(self):
        return Utils.pretty_print_proto(self._stats)


class CategoricalStatistics:
    def __init__(self, feature):
        self._feature = feature
        self._categorical = self._feature.categorical

    @property
    def unique(self):
        return self._categorical.unique

    @property
    def top(self):
        return [FeatureTop(top) for top in self._categorical.top]

    def __repr__(self):
        return Utils.pretty_print_proto(self._categorical)


class FeatureTop:
    def __init__(self, feature):
        self._feature = feature
        self._top = self._feature.top

    @property
    def name(self):
        return self._top.name

    @property
    def count(self):
        return self._top.count

    def __repr__(self):
        return Utils.pretty_print_proto(self._top)


class Monitoring:
    def __init__(self, feature):
        self._feature = feature
        self._monitoring = self._feature.monitoring

    @property
    def anomaly_detection(self):
        return self._monitoring.anomaly_detection

    @anomaly_detection.setter
    def anomaly_detection(self, value):
        self._monitoring.anomaly_detection = value

    def __repr__(self):
        return Utils.pretty_print_proto(self._monitoring)
