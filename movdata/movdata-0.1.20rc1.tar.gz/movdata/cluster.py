import movdata
import numpy as np

class Cluster:
    """A cluster represents a group of points in both time and space.
    Adds functionality to the base relocs object """

    def __init__(self, relocs=None):
        self._relocs = relocs or movdata.base.Relocations()

    @property
    def centroid(self):
        return self._relocs.centroid

    @property
    def relocs(self):
        return self._relocs

    def add_fix(self, fix):
        self._relocs.add_fix(fix)

    @property
    def cluster_radius(self):
        """ The cluster radius is the largest distance between a point in the relocs and the
        centroid of the relocs"""

        cluster_radius = 0.0
        centroid = self.relocs.centroid
        for pnt in self.relocs.get_fixes():
            #calculate the distance between the centroid and the fix
            this_radius = pnt.geopoint.dist_to_point(centroid)
            if this_radius > cluster_radius:
                cluster_radius = this_radius

        return cluster_radius

    @property
    def cluster_std_dev(self):
        """The cluster standard deviation is the standard deviation of the radii from the centroid
        to each point making up the cluster"""
        _centroid = self.relocs.centroid
        _radii = []
        for _pnt in self.relocs.get_fixes():
            # calculate the distance between the centroid and the fix
            _radii.append(_pnt.geopoint.dist_to_point(_centroid))
        return np.std(_radii)

    def threshold_point_count(self, threshold_dist):
        """Counts the number of points in the cluster that are within a threshold distance of the geographic centre"""
        _clust_count = 0
        _centroid = self.relocs.centroid
        for _pnt in self.relocs.get_fixes():
            # calculate the distance between the centroid and the fix
            _this_radius = _pnt.geopoint.dist_to_point(_centroid)
            if _this_radius <= threshold_dist:
                _clust_count = _clust_count + 1
        return _clust_count

    def apply_threshold_filter(self, threshold_dist_meters=float("Inf")):
        _centroid = self.relocs.centroid
        if _centroid is not None:
            for _f in self.relocs._fixes: #Apply to the underlying array and not to get_fixes() array
                _this_radius = _f.geopoint.dist_to_point(_centroid)
                if _this_radius > threshold_dist_meters:
                    _f.junk_status=True