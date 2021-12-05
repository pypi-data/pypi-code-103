import os
import typing
from movdata.percentile_area import PercentileArea, PercentileAreaProfile


def get_percentile_area(percentile_levels: typing.List,
                        raster_path: typing.Union[str, bytes, os.PathLike],
                        subject_id: str = ''):
    percentile_profile = PercentileAreaProfile(percentile_levels=percentile_levels,
                                               input_raster=raster_path,
                                               subject_id=subject_id)
    return PercentileArea.calculate_percentile_area(profile=percentile_profile)
