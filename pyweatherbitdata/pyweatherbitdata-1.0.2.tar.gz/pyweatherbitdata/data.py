"""Dataclasses for weatherbit."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BaseDataDescription:
    """A class describing base data for the Weather location."""

    key: str

    city_name: str
    latitude: float
    longitude: float
    country_code: str
    timezone: str


@dataclass
class AlertDescription:
    """A class describing a Severe Weather Alert."""

    key: str

    title: str | None = None
    en_description: str | None = None
    loc_description: str | None = None
    severity: str | None = None
    effective_utc: str | None = None
    ends_utc: str | None = None
    expires_utc: str | None = None
    onset_utc: str | None = None
    uri: str | None = None
    regions: list | None = None


@dataclass
class ObservationDescription:
    """A class describing current weather data."""

    key: str

    utc_time: str | None = None
    city_name: str | None = None
    temp: float | None = None
    app_temp: float | None = None
    pres: float | None = None
    humidity: int | None = None
    slp: float | None = None
    clouds: int | None = None
    solar_rad: float | None = None
    wind_spd: float | None = None
    wind_spd_kmh: float | None = None
    wind_spd_knots: float | None = None
    wind_cdir: str | None = None
    wind_dir: int | None = None
    dewpt: float | None = None
    pod: str | None = None
    weather_icon: str | None = None
    weather_code: int | None = None
    weather_text: str | None = None
    vis: float | None = None
    precip: float | None = None
    snow: float | None = None
    uv: float | None = None
    uv_description: str | None = None
    aqi: float | None = None
    aqi_level: str | None = None
    dhi: float | None = None
    dni: float | None = None
    ghi: float | None = None
    elev_angle: int | None = None
    h_angle: int | None = None
    timezone: str | None = None
    sunrise: str | None = None
    sunset: str | None = None
    is_night: bool | None = None
    beaufort_value: int | None = None
    beaufort_text: str | None = None
    alert_count: int | None = 0
    alerts: list[AlertDescription] = field(default_factory=list)


@dataclass
class ForecastDetailDescription:
    """A class describing forecast details weather data."""

    key: str

    utc_time: str | None = None
    temp: float | None = None
    max_temp: float | None = None
    min_temp: float | None = None
    app_max_temp: float | None = None
    app_min_temp: float | None = None
    humidity: int | None = None
    pres: float | None = None
    slp: float | None = None
    clouds: int | None = None
    wind_spd: float | None = None
    wind_gust_spd: float | None = None
    wind_cdir: str | None = None
    wind_dir: int | None = None
    dewpt: float | None = None
    pop: int | None = None
    condition: str | None = None
    weather_icon: str | None = None
    weather_text: str | None = None
    vis: float | None = None
    precip: float | None = None
    snow: float | None = None
    uv: float | None = None
    ozone: float | None = None


@dataclass
class ForecastDescription:
    """A class describing forecast weather data."""

    key: str

    utc_time: str | None = None
    city_name: str | None = None
    temp: float | None = None
    max_temp: float | None = None
    min_temp: float | None = None
    app_max_temp: float | None = None
    app_min_temp: float | None = None
    humidity: int | None = None
    pres: float | None = None
    slp: float | None = None
    clouds: int | None = None
    wind_spd: float | None = None
    wind_gust_spd: float | None = None
    wind_cdir: str | None = None
    wind_dir: int | None = None
    dewpt: float | None = None
    pop: int | None = None
    condition: str | None = None
    weather_icon: str | None = None
    weather_text: str | None = None
    vis: float | None = None
    precip: float | None = None
    snow: float | None = None
    uv: float | None = None
    ozone: float | None = None
    forecast: list[ForecastDetailDescription] = field(default_factory=list)


@dataclass
class BeaufortDescription:
    """A class that describes beaufort values."""

    value: int
    description: str
