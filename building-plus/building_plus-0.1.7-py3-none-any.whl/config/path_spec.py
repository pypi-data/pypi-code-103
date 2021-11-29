import pathlib

from .user import USER_DIR


# Suffixes.
CSV_SUFFIX = '.csv'
EPW_SUFFIX = '.epw'
HDF5_SUFFIX = '.h5'
IDF_SUFFIX = '.idf'
EIO_SUFFIX = '.eio'


# Paths.
TLD_ABSPATH = pathlib.Path(__file__).parents[2]
DEMO_FILES_DIR = TLD_ABSPATH / 'building_plus' / 'demo_files'
USER_DIR_PATH = pathlib.Path(USER_DIR).expanduser()
USER_DIR_DATA_RETRIEVAL = USER_DIR_PATH / 'data_retrieval'
USER_DIR_EPLUS = USER_DIR_PATH / 'eplus_validation'
USER_DIR_BUILDINGS = USER_DIR_PATH / 'eplus_buildings'
USER_DIR_ENERGYPLUS_WEATHER = USER_DIR_PATH / 'eplus_weather'
AUTO_CREATED_DIRS = [
    USER_DIR_DATA_RETRIEVAL,
    USER_DIR_EPLUS,
    USER_DIR_BUILDINGS,
    USER_DIR_ENERGYPLUS_WEATHER,
]
USER_DIR_LOCATION = dict(
    data_retrieval=USER_DIR_DATA_RETRIEVAL,
    eplus_validation=USER_DIR_EPLUS,
    eplus_buildings=USER_DIR_BUILDINGS,
    eplus_weather=USER_DIR_ENERGYPLUS_WEATHER,
)
