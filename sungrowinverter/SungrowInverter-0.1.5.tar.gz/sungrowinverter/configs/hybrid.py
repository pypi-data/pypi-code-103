"""
#
# Sungrow Hybrid Storage Inverter Series
#
# Valid device types:
#    SH3K6 / SH4K6 / SH5K-V13 / SH5K-20     - Residential Hybrid Single Phase Inverter for Low Voltage Battery [48V to 70V]
#    SH4K6-30 / SH5K-30 / SH3K6-30          - Residential Hybrid Single Phase Inverter for Low Voltage Battery [48V to 70V newer version]
#    SH3.6RS / SH4.6RS / SH5.0RS / SH6.0RS  - Residential Hybrid Single Phase Inverter wide battery voltage range [80V to 460V]
#    SH5.0RT / SH6.0RT / SH8.0RT / SH10RT   - Residential Hybrid Three Phase Inverter wide battery voltage range [80V to 460V]
#
# Sungrow hybrid inverter register definitions
"""

from sungrowinverter.configs.common import (
    ModBusRegister,
    OUTPUT_TYPE_CODES,
    TEMP_CELSIUS,
    KILO_WATT_HOUR,
    WATT,
    KILOGRAMS,
    PERCENTAGE,
    VOLTAGE,
    AMPERE,
    HERTZ,
)

SYSTEM_STATE_CODES = {
    0x2: "Stop",
    0x8: "Standby",
    0x10: "Initial Standby",
    0x20: "Startup",
    0x40: "Running",
    0x100: "Falt",
    0x400: "Running in maintain mode",
    0x800: "Running in forced mode",
    0x1000: "Running in off-grid mode",
    0x2501: "Restarting",
    0x4000: "Running in external EMS mode",
}

RUNNING_STATE_BITS = {
    0b00000001: "status_power_generated_from_pv",
    0b00000010: "status_charging",
    0b00000100: "status_discharging",
    0b00001000: "status_load_is_active",
    0b00010000: "status_exporting_power_to_grid",
    0b00100000: "status_importing_power_from_grid",
    0b10000000: "status_power_generated_from_load",
}

EMS_MODE_CODES = {
    0: "Self consumption mode (default)",
    2: "Forced mode (charge/discharge/stop)",
    3: "External EMS mode",
}

COMMAND_CHARGE_CODES = {
    0xAA: "Charge",
    0xBB: "Discharge",
    0xCC: "Stop (defualt)"
}

# the scan register start 1 less than the actual register recorded in specs.
# reason being registers start at 0, document for modbus usually refers to register 1 as the start of registers.
HYBRID_SCAN = {
    "read": [
        {"scan_start": 5000, "scan_range": 50},
        {"scan_start": 12999, "scan_range": 100},
        {"scan_start": 13099, "scan_range": 20},
    ],
    "holding": [
        {"scan_start": 4999, "scan_range": 6},
    ],
}

HYBRID_READ_REGISTERS: tuple[ModBusRegister, ...] = (
    ModBusRegister(5002, "output_type", "U16", table=OUTPUT_TYPE_CODES),
    ModBusRegister(5003, "daily_output_energy", "U16", 0.1, KILO_WATT_HOUR, description="Hybrid active power accumulation (Include PV generation and battery discharge energy)"),
    ModBusRegister(5004, "total_output_energy", "U32", 0.1, KILO_WATT_HOUR, description="Hybrid active power accumulation (Include PV generation and battery discharge energy)"),
    ModBusRegister(5008, "inside_temperature", "U16", 0.1, TEMP_CELSIUS, description="Internal inverter temperature"),
    ModBusRegister(5011, "mppt_1_voltage", "U16", 0.1, VOLTAGE),
    ModBusRegister(5012, "mppt_1_current", "U16", 0.1, AMPERE),
    ModBusRegister(5013, "mppt_2_voltage", "U16", 0.1, VOLTAGE),
    ModBusRegister(5014, "mppt_2_current", "U16", 0.1, AMPERE),
    ModBusRegister(5017, "total_dc_power", "U32", unit_of_measure=WATT, description="PV power that is usable (inverter inefficiency)"),
    ModBusRegister(5019, "grid_voltage", "U16", 0.1, VOLTAGE),
    ModBusRegister(5019, "phase_a_voltage", "U16", 0.1, VOLTAGE, description="Phase A (1-2) voltage is also the grid voltage on a single phase inverter"),
    ModBusRegister(5020, "phase_b_voltage", "U16", 0.1, VOLTAGE),
    ModBusRegister(5021, "phase_c_voltage", "U16", 0.1, VOLTAGE),
    ModBusRegister(5033, "reactive_power", "S32", unit_of_measure="var"),
    ModBusRegister(5035, "power_factor", "U16", 0.001),
    ModBusRegister(5036, "grid_frequency", "U16", 0.1, HERTZ),

    ModBusRegister(13000, "system_state", "U16", table=SYSTEM_STATE_CODES),
    ModBusRegister(13001, "running_state", "U16", transform="BINARY", length=8, table=RUNNING_STATE_BITS),
    ModBusRegister(13002, "daily_pv_generation", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13003, "total_pv_generation", "U32", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13005, "daily_export_power_from_pv", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13006, "total_export_power_from_pv", "U32", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13008, "load_power", "S32", unit_of_measure=WATT),
    ModBusRegister(13010, "export_power", "S32", unit_of_measure=WATT),
    ModBusRegister(13012, "daily_battery_charge_energy_from_pv", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13013, "total_battery_charge_energy_from_pv", "U32", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13015, "co2_reduction", "U32", 0.1, KILOGRAMS),
    ModBusRegister(13017, "daily_direct_energy_consuption", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13018, "total_direct_energy_consuption", "U32", 0.1, KILO_WATT_HOUR),

    ModBusRegister(13020, "battery_voltage", "U16", 0.1, VOLTAGE),
    ModBusRegister(13021, "battery_current", "U16", 0.1, AMPERE),
    ModBusRegister(13022, "battery_power", "U16", 0.1, WATT),
    ModBusRegister(13023, "battery_level", "U16", 0.1, PERCENTAGE),
    ModBusRegister(13024, "battery_state_of_health", "U16", 0.1, PERCENTAGE),
    ModBusRegister(13025, "battery_temperature", "U16", 0.1, TEMP_CELSIUS),
    ModBusRegister(13026, "daily_battery_discharge_energy", "U16", 0.1, KILO_WATT_HOUR, description="Daily energy that was discharged into the grid"),
    ModBusRegister(13027, "total_battery_discharge_energy", "U32", 0.1, KILO_WATT_HOUR, description="Total energy that was discharged into the grid"),
    ModBusRegister(13029, "self_consumption_today", "U16", 0.1, PERCENTAGE),
    ModBusRegister(13034, "total_active_power", "U32", 0.1, WATT),
    ModBusRegister(13036, "daily_import_energy", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13037, "total_import_energy", "U32", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13039, "battery_capacity", "U32", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13040, "daily_charge_energy", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13041, "total_charge_energy", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13045, "daily_export_energy", "U16", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13046, "total_export_energy", "U32", 0.1, KILO_WATT_HOUR),
    ModBusRegister(13102, "maximum_discharging_current", "U16", unit_of_measure=AMPERE),
    ModBusRegister(13102, "maximum_charging_current", "U16", unit_of_measure=AMPERE),
    ModBusRegister(13107, "battery_state_of_charge", "U16", 0.1, PERCENTAGE),
    ModBusRegister(13112, "battery_cycle_count", "U16"),
    ModBusRegister(13112, "cell_voltage_average", "U16", 0.1, VOLTAGE),
    ModBusRegister(13114, "cell_voltage_minimum", "U16", 0.1, VOLTAGE),
    ModBusRegister(13113, "cell_voltage_maximum", "U16", 0.1, VOLTAGE),
    ModBusRegister(13114, "cell_voltage_minimum", "U16", 0.1, VOLTAGE),
    ModBusRegister(13115, "battery_voltage", "U16", 0.01, VOLTAGE),
    ModBusRegister(13116, "cell_temperature_average", "U16", 0.1, TEMP_CELSIUS),
    ModBusRegister(13117, "cell_temperature_minimum", "U16", 0.1, TEMP_CELSIUS),
    ModBusRegister(13118, "cell_temperature_maximum", "U16", 0.1, TEMP_CELSIUS),
)

HYBRID_HOLDING_REGISTERS: tuple[ModBusRegister, ...] = (
    ModBusRegister(5000, "year", "U16"),
    ModBusRegister(5001, "month", "U16"),
    ModBusRegister(5002, "day", "U16"),
    ModBusRegister(5003, "hour", "U16"),
    ModBusRegister(5004, "minute", "U16"),
    ModBusRegister(5005, "second", "U16"),
)