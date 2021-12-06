import numpy as np
import pandas as pd
from ovretl.containers_utils.calculate_entity_containers import calculate_shipments_propositions_containers
from pandas.util.testing import assert_frame_equal


def test_calculate_entity_containers():
    containers_df = pd.DataFrame(
        data={
            "container_type": [
                "twenty_foot_reefer",
                "forty_foot_standard",
                "twenty_foot_standard",
                "forty_five_foot_highcube_standard",
                "forty_five_foot_highcube_standard",
            ],
            "hazardous": [True, True, False, False, False],
            "proposition_id": ["0", "0", "1", np.nan, np.nan],
            "shipment_id": [np.nan, np.nan, np.nan, "2", "3"],
        }
    )
    result_should_be = pd.DataFrame(
        data={
            "teus": [3, 1, 2, 2],
            "tc": [2, 1, 1, 1],
            "hazardous": [True, False, False, False],
            "refrigerated": [True, False, False, False],
            "proposition_id": ["0", "1", np.nan, np.nan],
            "shipment_id": [np.nan, np.nan, "2", "3"],
        }
    )
    result = calculate_shipments_propositions_containers(containers_df).reset_index(drop=True)
    assert_frame_equal(result, result_should_be, check_dtype=False, check_like=True)
