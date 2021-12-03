import movdata.base
import movdata.utils
import datetime as dt
from osgeo import ogr


class Geofence:
    """
    A polyline geometry representing a virtual fenceline
    ogr_geometry: can be anything but geofencing works on the intersection of a line with the input geoemtry
    """
    def __init__(self, ogr_geometry=None, fence_name='', unique_id='', warn_level=''):
        self._ogr_geometry = ogr_geometry
        self._fence_name = fence_name
        self._unique_id = unique_id
        self._warn_level = warn_level

    @property
    def name(self):
        return str(self._fence_name)

    @property
    def ogr_geometry(self):
        return self._ogr_geometry

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def warn_level(self):
        return self._warn_level


class GeofenceAnalysisParams(movdata.base.AnalysisParams):
    """
    A class to hold parameters needed for the geofence calculation.

    geofences: a list of geofences to run against each trajectory
    geofenceregions: a list of regions to test containment before/after a detected geofence crossing
    """

    def __init__(self, geofences=None, regions=None):
        self._geofences = geofences or []
        self._regions = regions or []

    @property
    def geofences(self):
        return self._geofences

    @property
    def regions(self):
        return self._regions


class GeofenceAnalysisResult(movdata.base.AnalysisResult):
    """ A class to hold the results of a geofence analysis"""

    def __init__(self, geofence_crossings=None):
        self._geofence_crossings = geofence_crossings or []

    @property
    def geofence_crossings(self):
        return self._geofence_crossings

    def add_crossing(self, geofence_crossing=None):
        if geofence_crossing is not None:
            self._geofence_crossings.append(geofence_crossing)


class GeofenceCrossing:

    """ Class to store the result of a single geofence crossing"""

    def __init__(self, subject_id='', subject_speed=0.0, subject_travel_heading=0.0,
                 estimated_cross_fix=None, geofence_id='', warn_level='',
                 start_region_ids=None, end_region_ids=None):
        self._subject_id = subject_id
        self._est_cross_fix = estimated_cross_fix
        self._start_region_ids = start_region_ids or []
        self._end_region_ids = end_region_ids or []
        self._geofence_id = geofence_id
        self._warn_level = warn_level
        self._subject_speed_kmhr = subject_speed
        self._subject_heading = subject_travel_heading

    @property
    def subject_id(self):
        return self._subject_id

    @property
    def subject_speed_kmhr(self):
        return self._subject_speed_kmhr

    @property
    def subject_heading(self):
        return self._subject_heading

    @property
    def est_cross_fix(self):
        return self._est_cross_fix

    @property
    def start_region_ids(self):
        return self._start_region_ids

    @property
    def end_region_ids(self):
        return self._end_region_ids

    @property
    def geofence_id(self):
        return self._geofence_id

    @property
    def warn_level(self):
        return self._warn_level


class GeofenceAnalysis:

    @classmethod
    def calc_crossings(cls, geofence_analysis_params=None, trajectories=None):
        """
        Run the crossings analysis using the input fences/regions against the various
        :param geofence_analysis_params:
        :param trajectories:
        :return:
        """

        trajectories = trajectories or []

        # Test to make sure the calculation parameters are not None and the correct type
        assert type(geofence_analysis_params) is GeofenceAnalysisParams

        # Create the output analysis result object
        result = GeofenceAnalysisResult()

        # Set the start time of the analysis
        result.analysis_start = dt.datetime.utcnow()

        for traj in trajectories:
            assert type(traj) is movdata.base.Trajectory

            subject_id = traj.relocs.subject_id
            trajsegs = traj.traj_segs

            for trajseg in trajsegs:
                fences = geofence_analysis_params.geofences
                for fence in fences:
                    assert type(fence) is Geofence

                    # Attempt the intersection of the trajectory segment with the fence
                    intersect_pnts = trajseg.ogr_geometry.Intersection(fence.ogr_geometry)

                    # intersect_pnts can either be None, POINT, or MULTIPOINT
                    _intersectPnts = []

                    # TODO better way to asses ogr geometry type?
                    if intersect_pnts.GetGeometryName() == 'POINT':
                        _intersectPnts.append(intersect_pnts)
                    else:
                        _intersectPnts = intersect_pnts

                    for pnt in _intersectPnts:

                        # Create a GeoPoint at the crossing OGR point
                        crossing_geopoint = movdata.base.GeoPoint(x=pnt.GetX(), y=pnt.GetY())

                        segment_distance_to_crossing = \
                            trajseg.start_fix_geopoint.dist_to_point(pnt)

                        segment_length = trajseg.length_km * 1000.0

                        fractional_distance = 0.0
                        if segment_length > 0.0:
                            fractional_distance = segment_distance_to_crossing / segment_length

                        # Estimate the time of the break based on the fractional timespan
                        fractional_time = fractional_distance * (trajseg.end_fix.fixtime - trajseg.start_fix.fixtime)
                        crossing_time = trajseg.start_fix.fixtime + fractional_time

                        # Create an estimated geofence cross fix
                        estimated_cross_fix = movdata.base.Fix(crossing_geopoint, crossing_time)

                        # Determine containment of the subject before and after the crossing
                        containment_before = GeofenceAnalysis.asses_containment(trajseg.start_fix_geopoint,
                                                                                geofence_analysis_params.regions)

                        containment_after = GeofenceAnalysis.asses_containment(trajseg.end_fix_geopoint,
                                                                               geofence_analysis_params.regions)

                        # Create the output fence crossing result
                        crossing = GeofenceCrossing(subject_id=subject_id,
                                                    subject_speed=trajseg.speed_kmhr,
                                                    subject_travel_heading=trajseg.heading,
                                                    estimated_cross_fix=estimated_cross_fix,
                                                    geofence_id=fence.unique_id,
                                                    warn_level=fence.warn_level,
                                                    start_region_ids=containment_before,
                                                    end_region_ids=containment_after)

                        # Add this given crossing to the result
                        result.add_crossing(crossing)

        # TODO: Sort the crossings chronologically

        # Set the end time of the analysis
        result.analysis_end = dt.datetime.utcnow()

        return result

    @classmethod
    def equator_fence(cls):
        """ Create a virtual fence around the equator that can be used for testing"""

        equatorFenceSeg = ogr.Geometry(type=ogr.wkbLineString)
        equatorFenceSeg.AssignSpatialReference(movdata.base.SRS.WGS84())
        equatorFenceSeg.AddPoint(0, 0, 0)
        equatorFenceSeg.AddPoint(90, 0, 0)
        equatorFenceSeg.AddPoint(180, 0, 0)
        equatorFenceSeg.AddPoint(270, 0, 0)
        equatorFenceSeg.AddPoint(0, 0, 0)

        #Wrap the Linestring into a Multilinestring for kicks
        equatorFence = ogr.Geometry(type=ogr.wkbMultiLineString)
        equatorFence.AssignSpatialReference(movdata.base.SRS.WGS84())
        equatorFence.AddGeometry(equatorFenceSeg)

        return equatorFence

    @classmethod
    def asses_containment(cls, geopoint=None, regions=None):
        return movdata.utils.assess_containment(geopoint=geopoint, regions=regions)