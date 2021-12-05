import os
import numpy as np
from skyfield.api import load, wgs84
import skyfield.timelib


def load_dat_file(datfile, satid):
    t = TraceGroup(datfile, satid)
    t.load_dat_file(datfile)
    return t


# A trace of Point belonging to a single pass of a single sat from a single site and a single optional rsite
class Trace:
    def __init__(self, timestamps, frequencies, fluxes, site, rsite=None):
        # sort timestamps, frequencies and fluxes along timestamps
        sort_indexes = np.argsort([ts.ut1 for ts in timestamps])
        self.timestamps = timestamps[sort_indexes[::]]
        self.frequencies = frequencies[sort_indexes[::]]
        self.fluxes = fluxes[sort_indexes[::]]

        self.site = site
        self.rsite = rsite

        self.start_time = self.timestamps[0]
        self.end_time = self.timestamps[-1]
        self.num_points = len(self.timestamps)

    def calculatePass(self, sat, sites):
        self.az = np.empty(self.num_points)
        self.el = np.empty(self.num_points)
        self.lat = np.empty(self.num_points)
        self.lon = np.empty(self.num_points)

        difference = sat - sites.get_site(self.site)["latlon"]

        for i, ts in enumerate(self.timestamps):
            subpoint = wgs84.subpoint(sat.at(ts))

            self.lat[i] = subpoint.latitude.degrees
            self.lon[i] = subpoint.longitude.degrees

            topocentric = difference.at(ts)
            el, az, d = topocentric.altaz()

            self.az[i] = az.degrees
            self.el[i] = el.degrees


# A set of traces belonging to a single sat, can be from multiple sites and rsites
class TraceGroup:
    def __init__(self, name, satid):
        self.name = name
        self.satid = satid
        self.start_time = None
        self.end_time = None
        self.num_points = 0
        self.num_traces = 0
        self.traces = []
        self.timescale = load.timescale()  # TOREMOVE maybe

    def load_dat_file(self, datfile):
        ts_a = []
        freq_a = []
        flux_a = []
        site = None
        rsite = None
        last_ts = None
        last_site = None
        last_rsite = None

        with open(datfile) as f:
            lines = f.readlines()

        for line in lines:
            fields = line.strip().split(maxsplit=5)

            if not fields[0].startswith("#"):
                ts = self.timescale.ut1_jd(float(fields[0]) + 2400000.5)
                freq = float(fields[1])
                flux = float(fields[2])
                site = int(fields[3])
                rsite = int(fields[4]) if len(fields) > 4 else None

                # Split in traces if site or rsite changes or if there is a time jump of ~1 hour
                if ts_a and (
                    site != last_site
                    or rsite != last_rsite
                    or ts.ut1 > last_ts.ut1 + 0.0417
                ):  # 0.0417 ~1 hour
                    # Use last_(r)site as in case site/rsite changed, it is wrong for the current track added
                    # As we only enter here if ts_a has an element, last_(r)site is always correct
                    self.traces.append(
                        Trace(
                            np.array(ts_a),
                            np.array(freq_a),
                            np.array(flux_a),
                            last_site,
                            last_rsite,
                        )
                    )

                    ts_a = []
                    freq_a = []
                    flux_a = []

                ts_a.append(ts)
                freq_a.append(freq)
                flux_a.append(flux)

                last_ts = ts
                last_site = site
                last_rsite = rsite

        self.traces.append(
            Trace(np.array(ts_a), np.array(freq_a), np.array(flux_a), site, rsite)
        )

        self._recalculate()

    def _recalculate(self, recursive=True):
        self.num_traces = len(self.traces)

        self.num_points = 0

        for t in self.traces:
            self.num_points += t.num_points

            if self.start_time is None or t.start_time.ut1 < self.start_time.ut1:
                self.start_time = t.start_time
            if self.end_time is None or t.end_time.ut1 > self.end_time.ut1:
                self.end_time = t.end_time

    def calculatePasses(self, sat, sites):
        for t in self.traces:
            t.calculatePass(sat, sites)
