"""For dealing with optional packages.

Decorators:
requires_buildingplus

Functions:
bplus_forecast_dr_capacity
bplus_load_actual_building_data
bplus_load_building
bplus_warm_up_date
bplus_building_warmup
bplus_building_response
bplus_two_way_interp
"""

from functools import wraps

try:
    from building_plus.basic.two_way_interp import two_way_interp
    from building_plus.config.path_spec import USER_DIR_LOCATION as BUILDINGPLUS_UDL
    from building_plus.process.building_response import building_response
    from building_plus.process.building_warmup import building_warmup, warm_up_date
    from building_plus.process.forecast_dr_capacity import forecast_dr_capacity
    from building_plus.process.load_actual_building_data import load_actual_building_data
    from building_plus.read.load_building import load_building
except ImportError:
    _has_buildingplus = False
else:
    _has_buildingplus = True


def requires_buildingplus(func):
    """For functions that require the building_plus module."""
    @wraps(func)
    def requires_buildingplus_wrapper(*args, **kwargs):
        if not _has_buildingplus:
            raise ImportError("building_plus is required for this functionality.")
        return func(*args, **kwargs)
    return requires_buildingplus_wrapper


@requires_buildingplus
def bplus_forecast_dr_capacity(building, observer, weather_forecast, date):
    building_forecast, _, _, _ = forecast_dr_capacity(
        building, observer, weather_forecast, date
    )
    return building_forecast


@requires_buildingplus
def bplus_load_actual_building_data(
    buildings, observer, weather, building_forecast, d_now, resolution_seconds
):
    return load_actual_building_data(
        buildings, observer, weather, building_forecast, d_now, resolution_seconds
    )


@requires_buildingplus
def bplus_load_building(filename):
    return load_building(BUILDINGPLUS_UDL['eplus_buildings'] / filename)


@requires_buildingplus
def bplus_warm_up_date(building, start_date):
    return warm_up_date(building, start_date)


@requires_buildingplus
def bplus_building_warmup(building, weather, start_date):
    return building_warmup(building, weather, start_date, None)


@requires_buildingplus
def bplus_building_response(
    building, observer, weather_now, building_data, dt_now, setpoint, date
):
    return building_response(
        building, observer, weather_now, building_data, dt_now, setpoint, date
    )


@requires_buildingplus
def bplus_two_way_interp(x_point, x_vec, y_vec):
    return two_way_interp(x_point, x_vec, y_vec)
