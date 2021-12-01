"""Units-related configuration variables.
"""


OPERATOR = {
    '*': 'times',
    '-': 'times',
    '/': 'per',
}

PREFIX = {
    'k': 'kilo',
    'm': 'milli',
    'M': 'mega',
}

UNIT_ANALOG = {
    '%': 'pct',
    'acre': 'acre',
    'Acre': 'acre',
    'cfs': 'cfs',
    'ft': 'ft',
    'hr': 'hr',
    'W': 'watt',
}


# CONVERSIONS

# kWh to Btu.
# Wikipedia: British thermal unit
# Accessed: 07/09/2020
# https://en.wikipedia.org/wiki/British_thermal_unit#As_a_unit_of_power
Btu_per_kWh = 3412.142

# Cubic feet natural gas to Btu.
# U.S. E.I.A.: What are Ccf, Mcf, Btu, and therms? How do I convert
# natural gas prices in dollars per Ccf or Mcf to dollars per Btu or
# therm?
# Accessed: 07/09/2020
# https://www.eia.gov/tools/faqs/faq.php?id=45&t=8
#
# NOTE: Normally, 1037 Btu/cf natural gas would be used. This number is
# used instead to be consistent with previous results obtained with
# EAGERS.
Btu_per_Mcf_natgas = 1_000_000  # _ are thousands separators: PEP 378.

# Thousand cubic feet natural gas to kWh.
# With 1,000,000 Btu/Mcf and 3,412.142 Btu/kWh: 293.07 kWh/Mcf
kWh_per_Mcf_natgas = Btu_per_Mcf_natgas / Btu_per_kWh

# MMBtu to kWh.
kWh_per_MMBtu_natgas = 293.15
