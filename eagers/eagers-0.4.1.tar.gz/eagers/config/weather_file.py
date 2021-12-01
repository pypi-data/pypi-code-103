# Headers for an EPW file.
EPW_HEADERS = [
    'Year', 'Month', 'Day', 'Hour', 'Minute', 'gibberish', 'Dry-bulb (C)',
    'Dew-point (C)', 'rh (%)', 'Pressure (Pa)', 'ETR (W/m^2)',
    'ETRN (W/m^2)', 'GHInfared (W/m^2)', 'GHI (W/m^2)', 'DNI (W/m^2)',
    'DHI (W/m^2)', 'GH illum (lx)', 'DN illum (lx)', 'DH illum (lx)',
    'Zenith lum (cd/m^2)', 'Wdir (degrees)', 'Wspd (m/s)', 'TotCld (tenths)',
    'OpqCld (tenths)', 'Hvis (m)', 'CeilHgt (m)',
]
# Headers that are actually read from EPW files.
EPW_INTEREST = [
    'GHI (W/m^2)', 'DNI (W/m^2)', 'DHI (W/m^2)', 'Dry-bulb (C)',
    'Dew-point (C)', 'rh (%)', 'Pressure (Pa)', 'Wdir (degrees)',
    'Wspd (m/s)', 'TotCld (tenths)', 'OpqCld (tenths)',
]
# Headers specifying timestamp for EPW files.
EPW_TIMESTAMP = [
    'Year', 'Month', 'Day', 'Hour', 'Minute',
]
# Headers that are actually read from CSV files.
CSV_INTEREST = [
    'GHI (W/m^2)', 'DNI (W/m^2)', 'DHI (W/m^2)', 'Dry-bulb (C)',
    'Dew-point (C)', 'rh (%)', 'Pressure (mbar)', 'Wdir (degrees)',
    'Wspd (m/s)',
]
# Headers specifying timestamp for CSV files.
CSV_TIMESTAMP = [
    'Date (MM/DD/YYYY)', 'Time (HH:MM)',
]
# Header mappings to WeatherTimeSeriesDB attributes.
WTS_ATTR_MAP = {
    'GHI (W/m^2)': 'glo_horz_irr',
    'DNI (W/m^2)': 'dir_norm_irr',
    'DHI (W/m^2)': 'dif_horz_irr',
    'Dry-bulb (C)': 't_dryb',
    'Dew-point (C)': 't_dewp',
    'rh (%)': 'rh',
    'Pressure (Pa)': 'pres_pa',
    'Wdir (degrees)': 'wdir',
    'Wspd (m/s)': 'wspd',
    'TotCld (tenths)': 'tot_cld',
    'OpqCld (tenths)': 'opq_cld',
}
