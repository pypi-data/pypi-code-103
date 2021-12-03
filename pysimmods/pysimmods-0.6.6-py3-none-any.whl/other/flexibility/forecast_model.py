"""This module contains the :class:`ForecastModel`."""
from datetime import datetime, timedelta, timezone
import numpy as np
from pysimmods.other.flexibility.schedule import Schedule
from pysimmods.util.dateformat import GER

from . import LOG


class ForecastModel:
    """The forecast model for all pysimmods.

    Parameters
    ----------
    model: :class:`.Model`
        An instance of a subclass of the base model class (e.g.,
        :class:`.Battery` model).
    start_date: str or datetime
        An ISO datetime string or a datetime object defining the start
        date.
    step_size: int, optional
        The step size of the model in seconds. Will be used as fallback
        if no step size is provided to the model. Defaults to 900.
    forecast_horizon_hours: float, optional
        The number of hours the model should create a forecast for.
        If the model needs a weather forecast, this weather forecast
        needs to be large enough.

    Attributes
    ----------
    model: :class:`.Model`
        A reference to the model.
    now_dt: :class:`.datetime.datetime`
        The current local time.
    step_size: int
        The step size of the model.
    forecasts: :class:`pandas.DataFrame`
        A dictionary containing forecasts for the inputs of the
        underlying model.
    flexibilities: dict
        A dictionary containing the current flexibilities of the
        underlying model.
    schedule: :class:`.Schedule`
        Contains the current schedule of the model.

    """

    def __init__(
        self,
        model,
        start_date,
        step_size=900,
        forecast_horizon_hours=1,
        flexibility_horizon_hours=3,
        num_schedules=10,
        seed=None,
        unit="kw",
        use_decimal_percent=False,
        priorize_schedule=False,
    ):
        self.model = model
        if isinstance(start_date, str):
            self.now_dt = datetime.strptime(start_date, GER).astimezone(
                tz=timezone.utc
            )
        else:
            self.now_dt = start_date
        self.step_size = step_size
        self.forecasts = None
        self.flexibilities = None

        if use_decimal_percent:
            self._percent_factor = 0.01
        else:
            self._percent_factor = 1.0
        self._priorize_schedule = priorize_schedule
        self._fch_hours = forecast_horizon_hours
        self._num_schedules = num_schedules

        if unit == "mw":
            self._unit_factor = 0.001
            self._pname = "p_mw"
            self._qname = "q_mvar"
        elif unit == "w":
            self.unit_factor = 1000.0
            self._pname = "p_w"
            self._qname = "q_var"
        else:
            self._unit_factor = 1.0
            self._pname = "p_kw"
            self._qname = "q_kvar"

        self.schedule = Schedule(
            self.now_dt,
            self.step_size,
            self._pname,
            self._qname,
            self._fch_hours,
        )

        if seed is not None:
            self._rng = np.random.RandomState(seed)
        else:
            self._rng = np.random.RandomState()

    def step(self):
        """Perform a simulation step of the underlying model.

        Also updates the internal state of the flexibility model.

        """
        # Update the step size
        self._check_inputs()

        setpoint = self._get_setpoint()
        self.set_percent = setpoint
        self.model.step()

        self.schedule.update_row(
            self.now_dt,
            setpoint,
            self.model.p_kw * self._unit_factor,
            self.model.q_kvar * self._unit_factor,
        )
        self._check_schedule()

        self.now_dt += timedelta(seconds=self.step_size)
        self.schedule.now_dt = self.now_dt

    def update_forecasts(self, forecasts):
        if self.forecasts is None:
            self.forecasts = forecasts
        else:
            for col in forecasts.columns:
                if col not in self.forecasts.columns:
                    self.forecasts[col] = np.nan
            for index, _ in forecasts.iterrows():
                if index not in self.forecasts.index:
                    break

            self.forecasts.update(forecasts.loc[:index])
            self.forecasts = self.forecasts.append(forecasts.loc[index:])
            self.forecasts = self.forecasts[~self.forecasts.index.duplicated()]

    def update_schedule(self, schedule):
        self.schedule.update(schedule)

    def _get_setpoint(self):
        try:
            schedule_set = self.schedule.get("target")
        except TypeError:
            schedule_set = None
        try:
            model_set = self.set_percent
        except TypeError:
            model_set = None

        default_set = (
            self.model.default_schedule[self.now_dt.hour]
            * self._percent_factor
        )

        priority = [model_set, schedule_set]

        if self._priorize_schedule:
            priority = priority[::-1]

        priority.append(default_set)

        setpoint = None
        for setval in priority:
            if setval is not None and ~np.isnan(setval):
                setpoint = setval
                break
        else:
            raise ValueError("Setpoint for model %s not set.", self.model)

        return setpoint

    def _check_inputs(self):
        if self.model.inputs.step_size is not None:
            self.step_size = self.model.inputs.step_size
        else:
            self.model.inputs.step_size = self.step_size
        self.model.inputs.now = self.now_dt

        if self.schedule() is None:
            self.schedule.init()

    def _check_schedule(self):

        if self.schedule.reschedule_required():
            self._create_init_schedule()
            self.schedule.prune()

    def _create_init_schedule(self):
        state_backup = self.model.get_state()

        now = self.now_dt + timedelta(seconds=self.step_size)
        periods = int(self._fch_hours * 3_600 / self.step_size)

        for _ in range(periods):
            if not self.schedule.has_index(now):
                self.schedule.update_row(now, np.nan, np.nan, np.nan)
            default_setpoint = (
                self.model.default_schedule[now.hour] * self._percent_factor
            )
            if np.isnan(self.schedule.get("target", now)):
                self.schedule.update_entry(now, "target", default_setpoint)

            try:
                self._perform_step(now, self.schedule.get("target", now))

                self.schedule.update_entry(
                    now, self._pname, self.model.p_kw * self._unit_factor
                )
                self.schedule.update_entry(
                    now, self._qname, self.model.q_kvar * self._unit_factor
                )

            except KeyError:
                # Forecast is missing
                LOG.warning("No forecast provided for model %s.", self.model)
                self.schedule.update_row(now, np.nan, np.nan, np.nan)

            now += timedelta(seconds=self.step_size)

        self.model.set_state(state_backup)

    def _perform_step(self, index, set_percent):
        self.set_percent = set_percent

        if self.forecasts is not None:
            for col in self.forecasts.columns:
                if hasattr(self.model.inputs, col):
                    setattr(
                        self.model.inputs, col, self.forecasts.loc[index, col]
                    )

        self.model.inputs.now = index
        self.model.inputs.step_size = self.step_size
        self.model.step()

    @property
    def inputs(self):
        return self.model.inputs

    @property
    def config(self):
        return self.model.config

    @property
    def state(self):
        return self.model.state

    @property
    def set_percent(self):
        return self.model.set_percent * self._percent_factor

    @set_percent.setter
    def set_percent(self, set_percent):
        self.model.set_percent = set_percent / self._percent_factor
