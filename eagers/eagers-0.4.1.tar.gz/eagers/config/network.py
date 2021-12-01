"""Defines network-related constants."""


# Network names, their corresponding abbreviation, what they
# represent:
# Electrical --- E  --- standard 480V AC electrical network
# DirectCurrent --- DC --- 48V DC electrical network
# Transmission1 --- E1 --- 230kV electric transmission (E2, E3, etc
#                             can be additional voltage levels)
# DistrictHeat --- H --- standard 80C supply heating bus
# DistrictCool --- C --- standard 4C supply cooling bus
# Heating2     --- H2 --- Heat a different temperature than
#                         DistrictHeat (H3, H4... as needed)
# CoolingWater --- CW --- Water circulated between chillers and
#                         cooling towers
# Hydro        --- W --- River network with reservoirs and dams
# Hydrogen     --- Hy --- Gaseous hydrogen stream
# LiqHydrogen  --- LH2 --- Liquid hydrogen
NETWORK_NAMES = (
    'electrical', 'direct_current', 'transmission_1',
    'district_heat', 'district_cool', 'heating_2', 'cooling_water',
    'hydro',
    'hydrogen', 'liq_hydrogen',
)
NETWORK_ABBRS = (
    'e', 'dc', 'e1',
    'h', 'c', 'h2', 'cw',
    'w',
    'hy', 'lh2',
)
NETWORK_ABBR_NAME_MAP = dict(zip(NETWORK_ABBRS, NETWORK_NAMES))
NETWORK_NAME_ABBR_MAP = dict(zip(NETWORK_NAMES, NETWORK_ABBRS))

# Mapping between Component outputs and the networks they would export
# to.
OUTPUT_NAMES = (
    'electricity', 'direct_current', None,
    'heat', 'cooling', None, None,
    'hydro',
    'hydrogen', 'liq_hydrogen',
)
OUTPUT_NETWORK_ABBR_MAP = dict(zip(OUTPUT_NAMES, NETWORK_ABBRS))
OUTPUT_NETWORK_NAME_MAP = dict(zip(OUTPUT_NAMES, NETWORK_NAMES))
