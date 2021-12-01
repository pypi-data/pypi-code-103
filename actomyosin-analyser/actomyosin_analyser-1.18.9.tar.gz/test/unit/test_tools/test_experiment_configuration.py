from tempfile import TemporaryDirectory
import os
from actomyosin_analyser.tools.experiment_configuration import ExperimentConfiguration

MockIterator = None
MockDataReader = None


def test_add_get_result_sub_folder():
    results_dir = TemporaryDirectory()
    exp_conf = ExperimentConfiguration(results_dir.name,
                                       MockDataReader, MockIterator)

    exp_conf['dies'] = 'das'

    assert os.path.join(results_dir.name, 'das') == exp_conf['dies']
