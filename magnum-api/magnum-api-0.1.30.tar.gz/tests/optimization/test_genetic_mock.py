import pandas as pd

from tests.resource_files import create_resources_file_path


def test_optimize_mock():
    # arrange
    design_variables_path = create_resources_file_path('resources/optimization/mock/optim_input_enlarged_BA.csv')
    design_variables_df = pd.read_csv(design_variables_path)
    print(design_variables_df.head())