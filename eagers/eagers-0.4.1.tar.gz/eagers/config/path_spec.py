"""Path specifications."""

import pathlib
from typing import Dict

from .user import USER_DIR


# Suffixes.
CSV_SUFFIX = '.csv'
EPW_SUFFIX = '.epw'
HDF5_SUFFIX = '.h5'

# Paths.
TLD_ABSPATH = pathlib.Path(__file__).parents[2]
EXCEL_INTERFACE_PROJECT_HELP = (
    TLD_ABSPATH / 'eagers' / 'read' / 'excel_interface_project_help.txt'
)
DEMO_FILES_DIR = TLD_ABSPATH / 'eagers' / 'demo_files'
USER_DIR_PATH = pathlib.Path(USER_DIR).expanduser()
BUILDPLUS_DIR_PATH = USER_DIR_PATH.parents[0]/'buildingplus-user'
USER_DIR_DATA_RETRIEVAL = USER_DIR_PATH / 'data_retrieval'
USER_DIR_HYDRO_DATA = USER_DIR_PATH / 'hydro_data'
USER_DIR_SIMRESULTS = USER_DIR_PATH / 'simulation_results'
USER_DIR_DATASETS = USER_DIR_PATH / 'data_sets'
USER_DIR_HDF5_DATASETS = USER_DIR_DATASETS / 'hdf5'
USER_DIR_HDF5_NODEDATA_DATASETS = USER_DIR_HDF5_DATASETS / 'nodedata'
USER_DIR_HDF5_WEATHER_DATASETS = USER_DIR_HDF5_DATASETS / 'weather'
USER_DIR_HDF5_OTHER_DATASETS = USER_DIR_HDF5_DATASETS / 'other'
USER_DIR_ENERGYPLUS_WEATHER = USER_DIR_PATH / 'eplus_weather'
BUILDPLUS_DIR_ENERGYPLUS_WEATHER = BUILDPLUS_DIR_PATH / 'eplus_weather'
USER_DIR_PROJECTS = USER_DIR_PATH / 'projects'
USER_DIR_TESTDATA = USER_DIR_PATH / 'test_data'
AUTO_CREATED_DIRS = [
    USER_DIR_DATA_RETRIEVAL,
    USER_DIR_HYDRO_DATA,
    USER_DIR_SIMRESULTS,
    USER_DIR_DATASETS,
    USER_DIR_HDF5_NODEDATA_DATASETS,
    USER_DIR_HDF5_WEATHER_DATASETS,
    USER_DIR_HDF5_OTHER_DATASETS,
    USER_DIR_ENERGYPLUS_WEATHER,
    USER_DIR_PROJECTS,
    USER_DIR_TESTDATA,
]
USER_DIR_LOCATION: Dict[str, pathlib.Path] = dict(
    data_retrieval=USER_DIR_DATA_RETRIEVAL,
    hydro_data=USER_DIR_HYDRO_DATA,
    simulation_results=USER_DIR_SIMRESULTS,
    data_sets=USER_DIR_DATASETS,
    hdf5=USER_DIR_HDF5_DATASETS,
    nodedata=USER_DIR_HDF5_NODEDATA_DATASETS,
    weather=USER_DIR_HDF5_WEATHER_DATASETS,
    eplus_weather=USER_DIR_ENERGYPLUS_WEATHER,
    projects=USER_DIR_PROJECTS,
    test_data=USER_DIR_TESTDATA,
    buildplus=BUILDPLUS_DIR_PATH
)
