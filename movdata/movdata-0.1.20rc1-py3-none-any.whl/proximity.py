import movdata.base
import movdata.utils
import math
import datetime as dt


class ProximityAnalysisParams(movdata.base.AnalysisParams):
    """
    A class to hold parameters needed for the proximity calculation.
    spatial_features: a list of ogr geometries to run against each trajectory
    """

    def __init__(self, spatial_features=None):
        self._spatial_features = spatial_features or []

    @property
    def spatial_features(self):
        return self._spatial_features


class ProximityAnalysisResult(movdata.base.AnalysisResult):
    """ A class to hold the results of a proximity analysis"""

    def __init__(self, proximity_events=None):
        self._proximity_events = proximity_events or []

    @property
    def proximity_events(self):
        return self._proximity_events

    def add_proximity_event(self, proximity_event=None):
        if proximity_event is not None:
            self._proximity_events.append(proximity_event)


class ProximityEvent:

    """ Class to store the result of a single proximity event"""

    def __init__(self, subject_id='',
                 subject_speed=0.0,
                 subject_travel_heading=0.0,
                 proximity_distance_meters=math.inf,
                 proximal_fix=None,
                 spatial_feature_id='',
                 spatial_feature_name=''):

        self._subject_id = subject_id
        self._proximal_fix = proximal_fix
        self._spatial_feature_id = spatial_feature_id
        self._spatial_feature_name = spatial_feature_name
        self._subject_speed_kmhr = subject_speed
        self._subject_heading = subject_travel_heading
        self._proximity_distance_meters = proximity_distance_meters

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
    def proximal_fix(self):
        return self._proximal_fix

    @property
    def proximity_distance_meters(self):
        return self._proximity_distance_meters

    @property
    def spatial_feature_id(self):
        return self._spatial_feature_id

    @property
    def spatial_feature_name(self):
        return self._spatial_feature_name


class ProximityAnalysis:

    @classmethod
    def calc_proximity_events(cls, proximity_analysis_params=None, trajectories=None):
        """
        :param proximity_analysis_params:
        :param trajectories:
        :return:
        """

        trajectories = trajectories or []

        # Test to make sure the calculation parameters are not None and the correct type
        assert type(proximity_analysis_params) is ProximityAnalysisParams

        # Create the output analysis result object
        result = ProximityAnalysisResult()

        # Set the start time of the analysis
        result.analysis_start = dt.datetime.utcnow()

        for traj in trajectories:
            assert type(traj) is movdata.base.Trajectory

            subject_id = traj.relocs.subject_id

            for seg in traj.traj_segs:
                for sf in proximity_analysis_params.spatial_features:
                    # diff_geo = seg.ogr_geometry.Difference(sf)
                    # if diff_geo is not None:
                    #     if diff_geo.GetGeometryName() == 'LINE':
                    #         pass

                    # Calculate the distance between the traj seg and the spatial feature
                    proximity_dist = seg.ogr_geometry.Distance(sf.ogr_geometry)

                    # Convert the distance from degrees to meters
                    proximity_dist = movdata.utils.degrees_to_km(proximity_dist) * 1000.0

                    # Create the proximity event
                    prox_event = ProximityEvent(
                        subject_id=subject_id,
                        subject_speed=seg.speed_kmhr,
                        subject_travel_heading=seg.heading,
                        proximity_distance_meters=proximity_dist,
                        proximal_fix=seg.start_fix,  # ToDo: figure out the estimated fix interpolated along the seg
                        spatial_feature_id=sf.unique_id,
                        spatial_feature_name=sf.name
                    )

                    # Add this given crossing to the result
                    result.add_proximity_event(prox_event)

        # Set the end time of the analysis
        result.analysis_end = dt.datetime.utcnow()

        return result


