import logging

from astropy.io import fits
from dkist_processing_math.arithmetic import divide_fits_access_by_array
from dkist_processing_math.arithmetic import subtract_array_from_fits_access

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.mixin.intermediate_loaders import IntermediateLoaderMixin
from dkist_processing_vbi.vbi_base import VbiScienceTask


class ScienceCalibration(VbiScienceTask, IntermediateLoaderMixin):
    """
    Class for running full science calibration on a set of Observe images
    """

    def run(self) -> None:
        """
        For each spatial position:
            - Collect dark calibration frame
            - Collect gain calibration frame
            For each dsps repeat number:
                - Collect input frames
                - Subtract dark
                - Divide by gain
                - Write out
        """
        logging.info(
            f"Starting science with {self.num_spatial_steps} steps and {self.num_dsps_repeats} repeats"
        )
        for step in range(1, self.num_spatial_steps + 1):
            with self.apm_step(f"retrieving dark calibration for step {step}"):
                dark_calibration_array = self.intermediate_dark_array(spatial_step=step)

            with self.apm_step(f"retrieving gain calibration for step {step}"):
                gain_calibration_array = self.intermediate_gain_array(spatial_step=step)

            for drep in range(1, self.num_dsps_repeats + 1):
                apm_str = f"step {step} and repeat number {drep}"
                with self.apm_step(f"collecting observe frames for {apm_str}"):
                    sci_access = self.fits_data_read_fits_access(
                        tags=[
                            VbiTag.input(),
                            VbiTag.frame(),
                            VbiTag.task("OBSERVE"),
                            VbiTag.dsps_repeat(drep),
                            VbiTag.spatial_step(step),
                        ],
                        cls=VbiL0FitsAccess,
                    )

                with self.apm_step(f"subtracting dark from {apm_str}"):
                    sci_access = subtract_array_from_fits_access(
                        access_objs=sci_access, array_to_subtract=dark_calibration_array
                    )

                with self.apm_step(f"dividing gain from {apm_str}"):
                    sci_access = divide_fits_access_by_array(
                        access_objs=sci_access, array_to_divide_by=gain_calibration_array
                    )

                for i, access_obj in enumerate(sci_access):
                    with self.apm_step(f"updating level 1 headers for {apm_str} and exposure {i}"):
                        processed_hdu_list = fits.HDUList(
                            [fits.PrimaryHDU(data=access_obj.data, header=access_obj.header)]
                        )

                    with self.apm_step(
                        f"writing level 1 data to disk for {apm_str} and exposure {i}"
                    ):
                        logging.info(f"Writing output for {apm_str} and exposure {i}")
                        self.fits_data_write(
                            processed_hdu_list,
                            tags=[
                                VbiTag.calibrated(),
                                VbiTag.frame(),
                                VbiTag.spatial_step(step),
                                VbiTag.dsps_repeat(drep),
                                VbiTag.stokes("I"),
                            ],
                        )
