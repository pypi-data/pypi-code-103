"""WeatherBit Data Wrapper."""
from __future__ import annotations

import logging
from typing import Optional

from aiohttp import ClientSession, ClientTimeout, client_exceptions

from pyweatherbitdata.const import (
    BASE_URL,
    DEFAULT_TIMEOUT,
    LANGUAGE_EN,
    UNIT_TYPE_METRIC,
    VALID_LANGUAGES,
    VALID_UNIT_TYPES
)
from pyweatherbitdata.data import (
    AlertDescription,
    BaseDataDescription,
    BeaufortDescription,
    ForecastDescription,
    ForecastDetailDescription,
    ObservationDescription,
)
from pyweatherbitdata.exceptions import RequestError, InvalidApiKey, ResultError, NotInitialized
from pyweatherbitdata.helpers import Calculations, Conversions

_LOGGER = logging.getLogger(__name__)


class WeatherBitApiClient:
    """Base class for WeatherBit Api."""

    req: ClientSession

    def __init__(
        self,
        api_key: str,
        latitude: float,
        longitude: float,
        units: Optional[str] = UNIT_TYPE_METRIC,
        language: Optional[str] = LANGUAGE_EN,
        homeassistant: Optional(bool) = True,
        session: Optional[ClientSession] = None,
    ) -> None:
        """Initialize Api Class."""
        self.api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.units = units
        self.language = language
        self.homeassistant = homeassistant

        if self.units not in VALID_UNIT_TYPES:
            self.units = UNIT_TYPE_METRIC
        self._is_metric = self.units is UNIT_TYPE_METRIC

        if self.language not in VALID_LANGUAGES:
            self.language = LANGUAGE_EN

        if session is None:
            session = ClientSession()
        self.req = session
        self.cnv = Conversions(self.units, self.homeassistant)
        self.calc = Calculations()

        self._station_data: BaseDataDescription = None
        self._is_night = False

    @property
    def station_data(self) -> BaseDataDescription:
        """Return Station Data."""
        return self._station_data

    async def initialize(self) -> None:
        """Initialize data tables."""
        endpoint = f"{BASE_URL}/current?lat={self.latitude}&lon={self.longitude}&key={self.api_key}"
        endpoint += f"&lang={self.language}&units=M"
        data = await self._async_request("get", endpoint)

        if data is None:
            raise ResultError("Data returned from WeatherBit. But empty or in unexpected format.") from None

        base_data = data["data"][0]
        entity_data = BaseDataDescription(
            key=base_data["station"],
            country_code=base_data["country_code"],
            city_name=base_data["city_name"],
            latitude=base_data["lat"],
            longitude=base_data["lon"],
            timezone=base_data["timezone"],
        )
        self._station_data = entity_data
        self._is_night = True if base_data["pod"] == "n" else False

    async def update_sensors(self) -> None:
        """Update sensor data."""
        if self.station_data is None:
            raise NotInitialized("Station Data have not been initialized.") from None

        endpoint = f"{BASE_URL}/current?lat={self.latitude}&lon={self.longitude}&key={self.api_key}"
        endpoint += f"&lang={self.language}&units=M&include=alerts"
        data = await self._async_request("get", endpoint)

        if data is None:
            raise ResultError("Data returned from WeatherBit. But empty or in unexpected format.") from None

        try:
            base_data = data["data"][0]
            beaufort: BeaufortDescription = self.calc.beaufort(base_data["wind_spd"])
            entity_data = ObservationDescription(
                key=self.station_data.key,
                utc_time=self.cnv.utc_from_timestamp(base_data["ts"]),
                city_name=base_data["city_name"],
                temp=self.cnv.temperature(base_data["temp"]),
                app_temp=self.cnv.temperature(base_data["app_temp"]),
                humidity=base_data["rh"],
                pres=self.cnv.pressure(base_data["pres"]),
                slp=self.cnv.pressure(base_data["slp"]),
                clouds=base_data["clouds"],
                solar_rad=base_data["solar_rad"],
                wind_spd=self.cnv.windspeed(base_data["wind_spd"]),
                wind_spd_kmh=self.cnv.windspeed_kmh(base_data["wind_spd"]),
                wind_spd_knots=self.cnv.windspeed_knots(base_data["wind_spd"]),
                wind_cdir=self.calc.wind_direction(base_data["wind_dir"]),
                wind_dir=base_data["wind_dir"],
                beaufort_value=beaufort.value,
                beaufort_text=beaufort.description,
                dewpt=self.cnv.temperature(base_data["dewpt"]),
                pod=base_data["pod"],
                weather_icon=base_data["weather"]["icon"],
                weather_code=base_data["weather"]["code"],
                weather_text=base_data["weather"]["description"],
                vis=self.cnv.distance(base_data["vis"]),
                precip=self.cnv.rain(base_data["precip"]),
                snow=self.cnv.rain(base_data["snow"]),
                uv=base_data["uv"],
                uv_description=self.calc.uv_description(base_data["uv"]),
                aqi=base_data["aqi"],
                aqi_level=self.calc.aqi_level(base_data["aqi"]),
                dhi=base_data["dhi"],
                dni=base_data["dni"],
                ghi=base_data["ghi"],
                elev_angle=base_data["elev_angle"],
                h_angle=base_data["h_angle"],
                timezone=base_data["timezone"],
                sunrise=base_data["sunrise"],
                sunset=base_data["sunset"],
                is_night=self._is_night,
            )

            alert_items = data["alerts"]
            alert_count = 0
            for item in alert_items:
                en_alert, loc_alert = self.cnv.alert_descriptions(item["description"])
                alert_item = AlertDescription(
                    key=self.station_data.key,
                    title=item["title"],
                    en_description=en_alert,
                    loc_description=loc_alert,
                    severity=item["severity"],
                    effective_utc=item["effective_utc"],
                    ends_utc=item["ends_utc"],
                    expires_utc=item["expires_utc"],
                    onset_utc=item["onset_utc"],
                    uri=item["uri"],
                    regions=item["regions"],
                )
                entity_data.alerts.append(alert_item)
                alert_count += 1

            entity_data.alert_count = alert_count
            return entity_data

        except Exception as e:
            _LOGGER.error("An error occured. Error message is %s", str(e))

    async def update_forecast(self) -> None:
        """Update forecast data."""
        if self.station_data is None:
            raise NotInitialized("Station Data have not been initialized.") from None

        endpoint = f"{BASE_URL}/forecast/daily?lat={self.latitude}&lon={self.longitude}&key={self.api_key}"
        endpoint += f"&lang={self.language}&units=M"
        data = await self._async_request("get", endpoint)

        if data is None:
            raise ResultError("Data returned from WeatherBit. But empty or in unexpected format.") from None
        try:
            base_data = data["data"][0]
            entity_data = ForecastDescription(
                key=self.station_data.key,
                utc_time=self.cnv.utc_from_timestamp(base_data["ts"]),
                city_name=data["city_name"],
                temp=base_data["temp"],
                max_temp=base_data["max_temp"],
                min_temp=base_data["min_temp"],
                app_max_temp=base_data["app_max_temp"],
                app_min_temp=base_data["app_min_temp"],
                humidity=base_data["rh"],
                pres=base_data["pres"],
                slp=base_data["slp"],
                clouds=base_data["clouds"],
                wind_spd=base_data["wind_spd"],
                wind_gust_spd=base_data["wind_gust_spd"],
                wind_cdir=self.calc.wind_direction(base_data["wind_dir"]),
                wind_dir=base_data["wind_dir"],
                dewpt=base_data["dewpt"],
                pop=base_data["pop"],
                weather_icon=base_data["weather"]["icon"],
                condition=self.cnv.condition_from_code(base_data["weather"]["code"], self._is_night),
                weather_text=base_data["weather"]["description"],
                vis=base_data["vis"],
                precip=base_data["precip"],
                snow=base_data["snow"],
                uv=base_data["uv"],
                ozone=base_data["ozone"],
            )

            base_data = data["data"]
            for item in base_data:
                forecast_data = ForecastDetailDescription(
                    key=self.station_data.key,
                    utc_time=self.cnv.utc_from_timestamp(item["ts"]),
                    temp=item["temp"],
                    max_temp=item["max_temp"],
                    min_temp=item["min_temp"],
                    app_max_temp=item["app_max_temp"],
                    app_min_temp=item["app_min_temp"],
                    humidity=item["rh"],
                    pres=item["pres"],
                    slp=item["slp"],
                    clouds=item["clouds"],
                    wind_spd=item["wind_spd"],
                    wind_gust_spd=item["wind_gust_spd"],
                    wind_cdir=item["wind_dir"],
                    wind_dir=item["wind_dir"],
                    dewpt=item["dewpt"],
                    pop=item["pop"],
                    weather_icon=item["weather"]["icon"],
                    condition=self.cnv.condition_from_code(item["weather"]["code"], False),
                    weather_text=item["weather"]["description"],
                    vis=item["vis"],
                    precip=item["precip"],
                    snow=item["snow"],
                    uv=item["uv"],
                    ozone=item["ozone"],
                )
                entity_data.forecast.append(forecast_data)

            return entity_data

        except Exception as e:
            _LOGGER.error("An error occured. Error message is %s", e.__class__)
            return None

    async def load_unit_system(self) -> None:
        """Return unit of meassurement based on unit system."""
        density_unit = "kg/m^3" if self._is_metric else "lb/ft^3"
        distance_unit = "km" if self._is_metric else "mi"
        length_unit = "m/s" if self._is_metric else "mph"
        length_km_unit = "km/h" if self._is_metric else "mph"
        pressure_unit = "hPa" if self._is_metric else "inHg"
        precip_unit = "mm" if self._is_metric else "in"

        units_list = {
            "none": None,
            "density": density_unit,
            "distance": distance_unit,
            "length": length_unit,
            "length_km": length_km_unit,
            "pressure": pressure_unit,
            "precipitation": precip_unit,
            "precipitation_rate": f"{precip_unit}/h",
        }

        return units_list

    async def _async_request(
        self,
        method: str,
        endpoint: str,
    ) -> dict:
        """Make a request against the API."""
        use_running_session = self.req and not self.req.closed

        if use_running_session:
            session = self.req
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        try:
            async with session.request(method, endpoint) as resp:
                resp.raise_for_status()
                data = await resp.json()

                return data

        except client_exceptions.ClientError as err:
            if "403" in str(err):
                raise InvalidApiKey("The API Key used is not valid. Try again with a new key.") from None
            raise RequestError(f"Error requesting data from WeatherBit: {err}") from None

        finally:
            if not use_running_session:
                await session.close()
