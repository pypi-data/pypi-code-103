import logging

from astropy.io import fits
from dkist_processing_math.statistics import average_numpy_arrays

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.vbi_base import VbiScienceTask


class DarkCalibration(VbiScienceTask):
    """
    Task for calculating a single dark frame for each spatial position
    """

    def run(self) -> None:
        """
        For each spatial step:
            - Gather input frames
            - Compute average
            - Write out
        """

        for step in range(1, self.num_spatial_steps + 1):
            with self.apm_step(f"collecting dark frames for step {step}"):
                input_dark_fits_access = self.fits_data_read_fits_access(
                    tags=[
                        VbiTag.input(),
                        VbiTag.frame(),
                        VbiTag.task("DARK"),
                        VbiTag.spatial_step(step),
                    ],
                    cls=VbiL0FitsAccess,
                )
                input_dark_arrays = (obj.data for obj in input_dark_fits_access)

            with self.apm_step(f"averaging arrays for step {step}"):
                averaged_dark_array = average_numpy_arrays(input_dark_arrays)
                logging.info(
                    f"average dark signal in step {step} = {averaged_dark_array.mean():.3e}"
                )

            with self.apm_step(f"writing dark calibration for step {step}"):
                hdul = fits.HDUList([fits.PrimaryHDU(data=averaged_dark_array)])
                self.fits_data_write(
                    hdu_list=hdul,
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.frame(),
                        VbiTag.task("DARK"),
                        VbiTag.spatial_step(step),
                    ],
                )
