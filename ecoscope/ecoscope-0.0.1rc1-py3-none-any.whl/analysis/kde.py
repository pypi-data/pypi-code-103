import logging
import os
import typing
from dataclasses import dataclass

from movdata import kde_range, raster, base

logger = logging.getLogger(__name__)


@dataclass
class KDERange:
    multirelocation: base.MultiRelocations
    output_dir: typing.Union[str, bytes, os.PathLike]
    pixel_size: float = 250.
    crs: typing.Any = 'EPSG:8857'
    nodata_value: float = 0.
    smooth_param: float = 0.0
    max_sd: float = 3.0
    prob_dens_cut_off: float = 1E-15
    expansion_factor: float = 1.

    def __post_init__(self):
        # assert type(self.multirelocation) == base.Relocations
        self.raster_profile = raster.RasterProfile(crs=self.crs,
                                                   pixel_size=self.pixel_size,
                                                   nodata_value=self.nodata_value
                                                   )
        self.output_raster = {}

        def _calculate_kde_range_(df):
            subject_name = df.subject_id.unique()[0]
            logger.info(f"Calculating KDE Range for subject {subject_name}")

            # replace whitespace with underscore char (_)
            subject_name = subject_name.replace(" ", "_")

            # calculate KDE range
            kde_profile = kde_range.KDEAnalysisProfile(smooth_param=self.smooth_param,
                                                       max_sd=self.max_sd,
                                                       prob_dens_cut_off=self.prob_dens_cut_off,
                                                       raster_profile=self.raster_profile,
                                                       expansion_factor=self.expansion_factor,
                                                       output_path=os.path.join(self.output_dir, f'{subject_name}.tif'))
            kde_range.KDEAnalysis.calculate_kde_range(kde_profile, df)
            self.output_raster[str(subject_name)] = os.path.join(self.output_dir, f'{subject_name}.tif')

        self.multirelocation.df().groupby('subject_id').apply(_calculate_kde_range_)
