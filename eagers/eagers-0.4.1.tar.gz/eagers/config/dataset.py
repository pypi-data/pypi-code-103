import datetime as dt


# Types of data sets.
DATASET_TYPES = ('nodedata', 'weather','other')

# HDF5 table descriptions.
DATASET_DESCR = dict(
    nodedata=dict(
        timestamp=dict(col='Time64Col', pos=0),
        e=dict(col='Float64Col', pos=1),
    ),
    weather=dict(
        timestamp=dict(col='Float32Col', pos=0),
        glo_horz_irr=dict(col='Float32Col', pos=1),
        dir_norm_irr=dict(col='Float32Col', pos=2),
        dif_horz_irr=dict(col='Float32Col', pos=3),
        t_dryb=dict(col='Float32Col', pos=4),
        t_dewp=dict(col='Float32Col', pos=5),
        rh=dict(col='Float32Col', pos=6),
        pres_pa=dict(col='Float32Col', pos=7),
        wdir=dict(col='Float32Col', pos=8),
        wspd=dict(col='Float32Col', pos=9),
        tot_cld=dict(col='Float32Col', pos=10),
        opq_cld=dict(col='Float32Col', pos=11),
    ),
    other=dict(timestamp=dict(col='Time64Col', pos=0),
        e=dict(col='Float64Col', pos=1),
        ),
)

# Conversion from shape codes to dimension info field names.
# These provide the mapping between given dimension info field names and
# the letters used in column shape specifications.
#
# ASSUMPTION:
# column_realization(), in util/hdf5.py, assumes that every shape code
# is a single letter.  Be careful when adding new ones to either follow
# the current convention or update it.
SHAPECODE_MAP = dict(
    h='horizon',
    z='zone',
    p='plantloop',  # Largest number of plant water loops at any building.
    t='timer',
)

# Default HDF5 table name.
DEFAULT_TABLENAME = 'hourly'
# Mapping from timestamp resolution to table names.
TIMESTAMP_RESOLUTION_TABLENAMES = {
    dt.timedelta(hours=1): 'hourly',
    dt.timedelta(days=1): 'daily',
}

# Data scrubbing.
SCRUB_LEVEL_ATTR = 'scrub_level'
SCRUB_VERSION_ATTR = 'scrub_version'
SCRUB_LEVELS = {
    'v1': {
        0: 'raw',
        1: 'missing filled',
    },
    'v2': {
        0: 'raw',
        1: 'zeros trimmed',
        2: 'DST removed',
        3: 'missing filled',
        4: 'partitioned',
    }
}
MAX_SCRUB_VERSION = max(int(v[1:]) for v in SCRUB_LEVELS.keys())
NEWEST_SCRUB_LEVELS = SCRUB_LEVELS[f"v{MAX_SCRUB_VERSION}"]
