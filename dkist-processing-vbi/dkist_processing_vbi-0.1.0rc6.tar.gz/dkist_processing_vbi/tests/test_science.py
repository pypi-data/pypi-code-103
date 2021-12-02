import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.science import ScienceCalibration
from dkist_processing_vbi.tests.conftest import ensure_all_inputs_used
from dkist_processing_vbi.tests.conftest import FakeGQLClient
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame
from dkist_processing_vbi.tests.conftest import Vbi122ObserveFrames


@pytest.fixture(scope="function")
def science_calibration_task(tmp_path, recipe_run_id):
    with ScienceCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_science_calibration",
        workflow_version="VX.Y",
    ) as task:
        task._scratch = WorkflowFileSystem(scratch_base_path=tmp_path)
        task.num_steps = 4
        task.num_exp_per_step = 2
        task.testing_num_dsps_repeats = 2
        task.constants[VbiBudName.num_spatial_steps.value] = task.num_steps
        task.constants[BudName.num_dsps_repeats.value] = task.testing_num_dsps_repeats
        task.constants[BudName.spectral_line.value] = "VBI TEST LINE"
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.testing_num_dsps_repeats,
        )
        header_generator = (d.header() for d in ds)
        for s in range(1, task.num_steps + 1):
            dark_cal = np.zeros((10, 10)) + (s * 10)
            dark_hdul = fits.HDUList([fits.PrimaryHDU(data=dark_cal)])
            task.fits_data_write(
                hdu_list=dark_hdul,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.frame(),
                    VbiTag.task("DARK"),
                    VbiTag.spatial_step(s),
                ],
            )

            gain_cal = np.zeros((10, 10)) + (s + 1)
            gain_hdul = fits.HDUList([fits.PrimaryHDU(data=gain_cal)])
            task.fits_data_write(
                hdu_list=gain_hdul,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.frame(),
                    VbiTag.task("GAIN"),
                    VbiTag.spatial_step(s),
                ],
            )

            for e in range(task.num_exp_per_step):
                for d in range(1, task.testing_num_dsps_repeats + 1):
                    header = next(header_generator)
                    data = (np.ones((1, 10, 10)) * (e + 1)) + s + (d * 10)
                    # Multiple by gain
                    data *= gain_cal
                    # Add dark
                    data += dark_cal
                    hdul = generate_214_l0_fits_frame(s122_header=header, data=data)
                    task.fits_data_write(
                        hdu_list=hdul,
                        tags=[
                            VbiTag.input(),
                            VbiTag.task("OBSERVE"),
                            VbiTag.spatial_step(s),
                            VbiTag.dsps_repeat(d),
                            VbiTag.frame(),
                        ],
                    )
        ensure_all_inputs_used(header_generator)
        yield task
        task.scratch.purge()
        task.constants.purge()


def test_science_calibration(science_calibration_task, mocker):
    """
    Given: a set of parsed input observe frames, dark and gain calibrations, and a ScienceCalibration task
    When: the task is run
    Then: the science frames are processed, no exposures are averaged, and the array values are correct
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    science_calibration_task()

    for s in range(1, science_calibration_task.num_steps + 1):
        for d in range(1, science_calibration_task.testing_num_dsps_repeats + 1):
            sci_access_list = list(
                science_calibration_task.fits_data_read_fits_access(
                    tags=[
                        VbiTag.calibrated(),
                        VbiTag.frame(),
                        VbiTag.spatial_step(s),
                        VbiTag.dsps_repeat(d),
                        VbiTag.stokes("I"),
                    ],
                    cls=VbiL0FitsAccess,
                )
            )
            assert len(sci_access_list) == science_calibration_task.num_exp_per_step
            sorted_access = sorted(sci_access_list, key=lambda x: np.mean(x.data))
            for e, obj in enumerate(sorted_access):
                expected_array = (np.ones((10, 10)) * (e + 1)) + s + (d * 10)
                np.testing.assert_equal(expected_array, obj.data)
