from typing import Protocol, Union
from enum import Flag, auto
from datetime import timedelta
from miio.utils import pretty_seconds


class VacuumFeatures(Flag):
    SupportsMop = auto()
    SupportsPercentageFanspeed = auto()
    SupportsPresets = auto()

class VacuumConsumableStatus(Protocol):
    @property
    def main_brush(self) -> timedelta:
        """Main brush usage time."""

    @property
    def main_brush_left(self) -> timedelta:
        """How long until the main brush should be changed."""
        return self.main_brush_total - self.main_brush

    @property
    def side_brush(self) -> timedelta:
        """Side brush usage time."""

    @property
    def side_brush_left(self) -> timedelta:
        """How long until the side brush should be changed."""
        return self.side_brush_total - self.side_brush

    @property
    def filter(self) -> timedelta:
        """Filter usage time."""

    @property
    def filter_left(self) -> timedelta:
        """How long until the filter should be changed."""
        return self.filter_total - self.filter

    @property
    def sensor_dirty(self) -> timedelta:
        """Return ``sensor_dirty_time``"""

    @property
    def sensor_dirty_left(self) -> timedelta:
        return self.sensor_dirty_total - self.sensor_dirty


class Vacuum(Protocol):
    def start(self):
        """Start vacuuming."""

    def pause(self):
        """Pause vacuuming."""

    def stop(self):
        """Stop vacuuming."""

    def status(self):
        """Return status container for the device."""

    def home(self):
        """Return back to base."""

    def find(self):
        """Request vacuum to play a sound to reveal its location."""

    def consumable_status(self) -> 'VacuumConsumableStatus':
        pass

    def clean_history(self) -> 'VacuumCleanSummary':
        pass

    def clean_details(self, id_: int) -> 'VacuumCleanDetails':
        pass

    def set_fan_speed(self, speed: Union['VacuumFanSpeed', int]):
        """Set fan speed."""

    # VacuumFanSpeedPresets could be simply a Dict[str, int]
    def fan_speed_presets(self) -> 'VacuumFanSpeedPresets':
        pass

    def supported_features(self) -> 'VacuumFeatures':
        """A enumflag to indicate available features."""