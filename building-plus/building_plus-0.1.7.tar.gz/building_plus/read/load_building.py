from building_plus.read.import_idf import import_idf
from building_plus.read.import_sizes import import_sizes
from building_plus.basic.file_handling import ensure_suffix

def load_building(filename):
    building = import_idf(ensure_suffix(filename, '.idf'))
    building = import_sizes(ensure_suffix(filename, '.eio'), building)
    return building
