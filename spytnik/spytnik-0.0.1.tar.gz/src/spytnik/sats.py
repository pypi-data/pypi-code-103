import os
from skyfield.api import load


def load_sats(tlefile=None):
    return Sats(tlefile)


class Sats:
    def __init__(self, tlefile=None):
        # Create timescale
        self.ts = load.timescale()

        if tlefile is None:
            tlefile = os.path.join(os.environ["ST_TLEDIR"], "bulk.tle")

        # Load TLEs
        self.tles = load.tle_file(tlefile)
        self.tles_by_name = {sat.name: sat for sat in self.tles}
        self.tles_by_id = {sat.model.satnum: sat for sat in self.tles}

    def names(self):
        return [k for k in self.tles_by_name.keys()]

    def ids(self):
        return [k for k in self.tles_by_id.keys()]

    def sat_by_name(self, name):
        return self.tles_by_name[name]

    def sat_by_id(self, id):
        return self.tles_by_id[int(id)]
