import os
from skyfield.api import wgs84


def load_sites(sitefile=None):
    return Sites(sitefile)


class Sites:
    def __init__(self, sitefile=None):
        self.sites = {}

        if sitefile is None:
            sitefile = os.path.join(os.environ["ST_DATADIR"], "data", "sites.txt")

        with open(sitefile) as f:
            lines = f.readlines()
        for line in lines:
            fields = line.strip().split(maxsplit=5)

            if not fields[0].startswith("#"):
                self.sites[int(fields[0])] = {
                    "acronym": fields[1],
                    "name": fields[5],
                    "latlon": wgs84.latlon(
                        float(fields[2]), float(fields[3]), elevation_m=float(fields[4])
                    ),
                }

    def ids(self):
        return [k for k in self.sites.keys()]

    def get_site(self, id=None):
        if id is None:
            id = int(os.environ["ST_COSPAR"])
        return self.sites[int(id)]
