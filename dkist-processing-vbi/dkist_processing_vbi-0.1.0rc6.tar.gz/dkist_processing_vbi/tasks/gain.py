import logging
from typing import Dict

import numpy as np
from astropy.io import fits
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.mixin.intermediate_loaders import IntermediateLoaderMixin
from dkist_processing_vbi.vbi_base import VbiScienceTask


class GainCalibration(VbiScienceTask, IntermediateLoaderMixin):
    """
    Task for computing a single gain frame for each spatial position.

    Note that VBI only ever deals with Solar Gain frames
    """

    def run(self) -> None:
        """
        For each spatial step:
            - Gather input frames
            - Compute average
            - Retrieve corresponding dark calibration frame
            - Subtract dark from average
        - Normalize all arrays by the global mean
        - Write out
        """

        # These will be running totals used to save a pass when computing the full-FOV normalization
        self.total_counts: float = 0.0
        self.total_non_nan_pix: int = 0

        # We'll just stuff the un-normalized arrays in this dictionary to avoid dealing with tags, io, etc.
        # This is OK (tm) because this will be, at most, 9 4k x 4k arrays. This is a lot (~1G), but not too much.
        step_gain_dict: dict = {}

        for step in range(1, self.num_spatial_steps + 1):
            with self.apm_step(f"retrieving dark frame for step {step}"):
                dark_calibration_array = self.intermediate_dark_array(spatial_step=step)

            with self.apm_step(f"collecting gain frames for step {step}"):
                input_gain_access = self.fits_data_read_fits_access(
                    tags=[
                        VbiTag.input(),
                        VbiTag.frame(),
                        VbiTag.spatial_step(step),
                        VbiTag.task("GAIN"),
                    ],
                    cls=VbiL0FitsAccess,
                )
                input_gain_arrays = (obj.data for obj in input_gain_access)

            with self.apm_step(f"averaging arrays from step {step}"):
                averaged_gain_array = average_numpy_arrays(input_gain_arrays)
                logging.info(
                    f"average raw gain signal in step {step} = {averaged_gain_array.mean():.3e}"
                )

            with self.apm_step(f"subtracting dark from average gain for step {step}"):
                dark_subtracted_gain_array = next(
                    subtract_array_from_arrays(
                        arrays=averaged_gain_array, array_to_subtract=dark_calibration_array
                    )
                )

            self.total_non_nan_pix += np.sum(~np.isnan(dark_subtracted_gain_array))
            self.total_counts += np.nansum(dark_subtracted_gain_array)
            step_gain_dict[step] = dark_subtracted_gain_array

        with self.apm_step("normalizing gain arrays"):
            normalized_array_dict = self.normalize_fov(step_gain_dict)

        with self.apm_step("writing gain arrays to disk"):
            self.write_gain_calibration(normalized_array_dict)

    def normalize_fov(self, step_gain_dict: Dict[int, np.ndarray]) -> Dict[int, np.ndarray]:
        """
        Compute the global mean of the *entire* FOV and divide each spatial step by this mean
        """
        fov_mean = self.total_counts / self.total_non_nan_pix
        logging.info(f"full FOV mean = {fov_mean:.3e}")
        for k in step_gain_dict:
            step_gain_dict[k] = step_gain_dict[k] / fov_mean

        return step_gain_dict

    def write_gain_calibration(self, gain_array_dict: Dict[int, np.ndarray]) -> None:
        """
        Apply correct tags to each spatial step and write to disk
        """
        for step, data in gain_array_dict.items():
            hdul = fits.HDUList([fits.PrimaryHDU(data=data)])
            self.fits_data_write(
                hdu_list=hdul,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.frame(),
                    VbiTag.task("GAIN"),
                    VbiTag.spatial_step(step),
                ],
            )
