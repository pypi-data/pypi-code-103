from __future__ import annotations
import numpy as np
from datetime import datetime
from typing import Union, List, Iterator, Tuple, Any
import matplotlib.pyplot as plt

from randdpy.core.BaseClasses import MeasurementBase, TickedMeasurement, ArrayBase, TickedArrayBase
from randdpy.Utilities.Multiplot import TickedCountsPlotter


class Counts(MeasurementBase):
    """
    Class which stores counts, live and real tick_times and errors for count data.

    Parameters
    ----------
    counts : float
        Number of counts measured within live_time by the detector.
    live_time : float
        Live_time of detector during acquisition.
    real_time : float
        Real_time of detector during acquisition.
    name : str
        Label for the count data.
    comment : str
        Comment to attach to the count data.
    start_time : datetime or None
        Time at which the acquisition started.

    Methods
    -------
    consecutive_addition(other: Counts) -> Counts
        Method which subtracts Counts data from the current Counts data, equivalent to subtracting a subsection of a
        measurement.
    """
    def __init__(self,
                 counts: float,
                 live_time: float,
                 real_time: float,
                 name: str = '',
                 error: Union[float, None] = None,
                 comment: str = '',
                 start_time: Union[datetime, None] = None):
        self.counts = counts
        self._error = error
        super(Counts, self).__init__(live_time=live_time,
                                     real_time=real_time,
                                     name=name,
                                     comment=comment,
                                     start_time=start_time)

    @property
    def error(self) -> float:
        """
        Property which returns the uncertainty in the count data.

        Returns
        -------
        float
        """
        if self._error is None:
            return self.counts**0.5
        else:
            return self._error

    @property
    def count_rate(self) -> float:
        """
        Property which returns the count rate of the measurement. I.e. counts / live_time

        Returns
        -------
        float
        """
        return (self.counts / self.live_time) if self.live_time > 0. else 0.

    def resample(self, scale: float = 1.0) -> Counts:
        """
        Method which returns a new Counts instance with the counts data resampled from a normal distribution from the
        counts and error data, scaled by the 'scale' factor.

        Parameters
        ----------
        scale : float
            Scale factor by which the counts data will be multiplied before resampling.

        Returns
        -------
        Counts
        """
        new_counts = np.random.normal(self.counts*scale, np.sqrt(scale*self.error**2))
        return Counts(new_counts, live_time=self.live_time, real_time=self.real_time, name=self.name,
                      error=np.sqrt(scale*self.error**2), comment=self.comment)

    def subtract_background(self, bg_counts: Counts) -> Counts:
        """
        Function which takes a background Counts object and subtracts it,
        scaled by the correct live time, returning the resultant Counts.

        Parameters
        ----------
        bg_counts : Counts
            Background counts to be subtracted.

        Returns
        -------
        Counts
        """
        return super(Counts, self).subtract_background(bg_counts)

    def consecutive_addition(self, other: Counts) -> Counts:
        """
        Method which adds Counts data to the current Counts data, equivalent to adding two consecutive measurements
        together, adding their counts and live and real times together.

        Parameters
        ----------
        other : Counts
            Counts to add.

        Returns
        -------
        Counts
        """
        counts = Counts(self.counts + other.counts,
                        live_time=self.live_time + other.live_time,
                        real_time=self.real_time + other.real_time,
                        error=(self.error**2 + other.error**2)**0.5,
                        name=self.name)
        return counts

    def simultaneous_addition(self, other: Counts) -> Counts:
        """
        Method which adds Counts data to the current Counts data, equivalent to adding two simultaneous measurements
        together, adding their counts together, scaling 'other' counts to have equal live time.

        Parameters
        ----------
        other : Counts
            Counts to add.

        Returns
        -------
        Counts
        """
        scale = self.live_time / other.live_time
        counts = Counts(self.counts + other.counts * scale,
                        live_time=self.live_time,
                        real_time=self.real_time,
                        error=(self.error**2 + (other.error*scale)**2)**0.5,
                        name=self.name)
        return counts

    def consecutive_subtraction(self, other: Counts) -> Counts:
        """
        Method which subtracts Counts data from the current Counts data, equivalent to subtracting a subsection of a
        measurement.

        Parameters
        ----------
        other : Counts
            Counts to subtract.

        Returns
        -------
        Counts
        """
        counts = Counts(self.counts - other.counts,
                        live_time=self.live_time - other.live_time,
                        real_time=self.real_time - other.real_time,
                        error=(self.error**2 + other.error**2)**0.5,
                        name=self.name)
        return counts

    def simultaneous_subtraction(self, other: Counts) -> Counts:
        """
        Method which subtracts Counts data from the current Counts data, equivalent to subtracting a signal present
        throughout the measurement, e.g. the background.

        Parameters
        ----------
        other : Counts
            Counts to subtract.

        Returns
        -------
        Counts
        """
        scale = self.live_time / other.live_time
        counts = Counts(self.counts - other.counts * scale,
                        live_time=self.live_time,
                        real_time=self.real_time,
                        error=(self.error**2 + (other.error*scale)**2)**0.5,
                        name=self.name)
        return counts

    def __str__(self) -> str:
        return (f"<Counts counts='{self.counts:.1f}' live_time='{self.live_time:.1f}' real_time='{self.real_time:.1f}' "
                f"error='{self.error:.1f}' name='{self.name}'  comment='{self.comment}' />")

    def __eq__(self, other: Counts) -> bool:
        return self.counts == other.counts and self.live_time == other.live_time


class CountsArray(ArrayBase):
    """
    Array of Counts objects, indexed by their 'name' attribute.

    Parameters
    ----------
    counts : List[Counts]
        List of Counts instances. These will become the members of the array.

    Methods
    -------
    consecutive_addition(other: Counts) -> Counts
        Method which subtracts Counts data from the current Counts data, equivalent to subtracting a subsection of a
        measurement.

    Notes
    -----
    Users will probably not need to create CountsArray instances, they will be used after being created inside the
    SMLReader.

    Examples
    --------
    >>> from randdpy import SMLReader
    >>> sml = SMLReader(...)
    >>> # The neutron_foregrounds property of the SMLReader returns a CountsArray
    >>> sml.neutron_foregrounds
    <randdpy.core.Counts.CountsArray at 0x11d391dcd08>
    >>> # The `Counts` instances are referenced by their name attributes:
    >>> sml.neutron_foregrounds['DetN1']
    <randdpy.core.Counts.Counts at 0x11d06ba3608>

    """
    def __init__(self, counts: List[Counts]):
        super(CountsArray, self).__init__(counts)

    def __getitem__(self, item) -> Counts:
        return super(CountsArray, self).__getitem__(item)

    def get(self, item: str, default_val: Any = Counts(0., 0., 0.)) -> Counts:
        return super(CountsArray, self).get(item, default_val)

    def simultaneous_sum(self) -> Counts:
        """
        Method which returns the simultaneous sum of all of the members of the array.

        Returns
        -------
        Counts
        """
        c_sum = Counts(counts=0.,
                       live_time=float(np.mean([c.live_time for c in self.elements.values()])),
                       real_time=float(np.mean([c.real_time for c in self.elements.values()])),
                       name=f'Simultaneously summed counts from ' + ', '.join(self.names))
        for c in self.elements.values():
            c_sum = c_sum.simultaneous_addition(c)
        return c_sum

    def consecutive_sum(self) -> Counts:
        """
        Method which returns the consecutive sum of all of the members of the array.

        Returns
        -------
        Counts
        """
        c_sum = Counts(counts=0., live_time=0., real_time=0.,
                       name=f'Consecutively summed counts from ' + ', '.join(self.names))
        for c in self.elements.values():
            c_sum = c_sum.consecutive_addition(c)
        return c_sum

    def subtract_backgrounds(self, backgrounds: CountsArray) -> CountsArray:
        """
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.

        Parameters
        ----------
        backgrounds : CountsArray

        Returns
        -------
        CountsArray
        """
        return super(CountsArray, self).subtract_backgrounds(backgrounds)

    def consecutive_addition(self, other: CountsArray) -> CountsArray:
        """
        Method which returns the consecutive sum of the CountsArray with another Array.

        Parameters
        ----------
        other : CountsArray
            The Array instance to add to this one.

        Returns
        -------
        CountsArray
        """
        return super(CountsArray, self).consecutive_addition(other)

    def consecutive_subtraction(self, other: CountsArray) -> CountsArray:
        """
        Method which returns the consecutive subtraction of another CountsArray from the Array.

        Parameters
        ----------
        other : Array
            The Array instance to subtract from this one.

        Returns
        -------
        CountsArray
        """
        return super(CountsArray, self).consecutive_subtraction(other)

    def simultaneous_addition(self, other: CountsArray) -> CountsArray:
        """
        Method which returns the simultaneous sum of the CountsArray with another Array.

        Parameters
        ----------
        other : Array
            The Array instance to add to this one.

        Returns
        -------
        CountsArray
        """
        return super(CountsArray, self).simultaneous_addition(other)

    def simultaneous_subtraction(self, other: CountsArray) -> CountsArray:
        """
        Method which returns the simultaneous subtraction of another CountsArray from the Array.

        Parameters
        ----------
        other : Array
            The Array instance to subtract from this one.

        Returns
        -------
        CountsArray
        """
        return super(CountsArray, self).simultaneous_subtraction(other)

    def resample(self, factor: float) -> CountsArray:
        """
        Method which returns a new array with each member resampled after scaling by the factor parameter.

        Parameters
        ----------
        factor : float
            Scale by which the measurements will be scaled before resampling.

        Returns
        -------
        CountsArray
        """
        return super(CountsArray, self).resample(factor)

    def masked_array(self, names: List[str]) -> CountsArray:
        """
        Method which returns a new array consisting only of members with the names in the given list of names.

        Parameters
        ----------
        names : List[str]

        Returns
        -------
        Array
        """
        return super(CountsArray, self).masked_array(names)

    def __str__(self):
        return f"Counts : " + ", ".join([f"{det}:{self[det].counts:.1f}" for det in self.elements])


class TickedCounts(TickedMeasurement):
    """
    Class which contains details about the counts for multiple ticks (sequential short periods of time).

    Attributes
    ----------
    ticks : np.ndarray
        Array of counts for each tick.
    tick_times : np.ndarray
        Array of datetime instances, marking the time at which each tick ended or began.
    live_times : np.ndarray
        Array of floats, labelling the live time for each tick.
    real_times : np.ndarray
        Array of floats, labelling the real time for each tick.
    msg_times : np.ndarray
        Possible array of datetime instances, marking the times at which the tick messages arrived.
    blank_rate : np.ndarray
        Possible array of floats, marking the rate of blanking pulses measured during each tick.
    name : str
        Label for the count data.
    comment : str
        Comment to attach to the count data.
    start_time : datetime or None
        Time at which the acquisition started.

    Methods
    -------
    errors() -> np.ndarray
        Property which returns the uncertainties for each tick.
    get_single_tick(tick_num: int) -> Counts
        Method which returns a single tick's worth of counts, with the appropriate live time and real time.
    sum_ticks(start: datetime = None, end: datetime = None) -> Counts
        Method which returns a Counts instance containing the summed counts for all ticks, or ticks in the range
        start:end.
    resample(scale: float = 1.0) -> TickedCounts
        Method which returns a resampled TickedCounts instance.
    plot(**kwargs) -> Tuple[plt.Figure, plt.Axes]
        Simple generator of variable length windowed spectra, equivalent to a rolling window across the time space.
    simple_windowed_counts(tick_window_width: int = 1, mode: int = 0) -> Iterator[Counts]
        Simple generator of variable length windowed spectra, equivalent to a rolling window across the time space.
    subtract_background(bg_counts: Counts) -> TickedCounts
        Method which subtracts a background signal from each of the ticks, using simultaneous subtraction.
    """
    def __init__(self,
                 ticks: np.ndarray,
                 tick_times: np.ndarray,
                 live_times: np.ndarray,
                 real_times: np.ndarray,
                 name: str = '',
                 msg_times: Union[np.ndarray, None] = None,
                 blank_rate: Union[np.ndarray, None] = None,
                 errors: Union[np.ndarray, None] = None,
                 start_time: Union[np.ndarray, None] = None,
                 comment: str = ''):
        """
        Parameters
        ----------
        ticks : np.ndarray
            Array of counts for each tick.
        tick_times : np.ndarray
            Array of datetime instances, marking the time at which each tick ended or began.
        name : str
            Label for the count data.
        live_times : np.ndarray
            Array of floats, labelling the live time for each tick.
        real_times : np.ndarray
            Array of floats, labelling the real time for each tick.
        msg_times : np.ndarray
            Optional array of datetime instances, marking the times at which the tick messages arrived.
        blank_rate : np.ndarray
            Optional array of floats, marking the rate of blanking pulses measured during each tick.
        errors : np.ndarray
            Optional array of floats, marking the uncertainties of the counts values. If None, defaults to Poisson
            uncertainties.
        start_time : datetime
            Time at which the measurement began.
        comment : str
            Optional string comment to attach to the measurement.
        """

        super().__init__(tick_times=tick_times, live_times=live_times, real_times=real_times, name=name,
                         comment=comment, start_time=start_time)

        self.ticks = ticks
        self.msg_times = msg_times
        self.blank_rate = blank_rate
        self._errors = errors

    @property
    def errors(self) -> np.ndarray:
        """
        Property which returns the uncertainties for each tick.

        Returns
        -------
        np.ndarray
        """
        if self._errors is None:
            return np.abs(self.ticks) ** 0.5
        else:
            return self._errors

    def get_single_tick(self, tick_num: int) -> Counts:
        """
        Method which returns a single tick's worth of counts, with the appropriate live time and real time.

        Parameters
        ----------
        tick_num : int
            The index for the tick to retrieve.

        Returns
        -------
        Counts
        """
        return Counts(counts=self.ticks[tick_num],
                      live_time=self.live_times[tick_num],
                      real_time=self.real_times[tick_num],
                      error=self.errors[tick_num],
                      name=self.name + (' ' if len(self.name) > 0 else '') + f'Tick {tick_num}',
                      comment=self.comment)

    def sum_ticks(self, start: Union[datetime, None] = None, end: Union[datetime, None] = None) -> Counts:
        """
        Method which returns a Counts instance containing the summed counts for all ticks, or ticks in the range
        start:end.

        Parameters
        ----------
        start : Union[datetime, None]
            The start time from which to sum the ticks. If None, sums from the first tick in the sequence.
        end : Union[datetime, None]
            The end time up to which to sum the ticks. If None, sums up to the last tick in the sequence.

        Returns
        -------
        Counts
        """
        t_mask = np.ones(self.tick_times.size, dtype=bool)
        if start is not None:
            t_mask = np.logical_and(t_mask, self.tick_times >= start)
        if end is not None:
            t_mask = np.logical_and(t_mask, self.tick_times < end)
        counts = Counts(self.ticks[t_mask].sum(axis=0),
                        live_time=self.live_times[t_mask].sum(axis=0),
                        real_time=self.real_times[t_mask].sum(axis=0),
                        name=self.name, comment=self.comment,
                        error=None if self._errors is None else np.sqrt(np.square(self.errors[t_mask]).sum()),
                        start_time=self.start_time if start is None else start)
        return counts

    def resample(self, scale: float = 1.0) -> TickedCounts:
        """
        Method which returns a resampled TickedCounts instance.

        Parameters
        ----------
        scale : float
            Factor by which to multiply the TickedCounts instance before resampling.

        Returns
        -------
        TickedCounts
        """
        new_ticks = np.random.poisson(self.ticks*scale)
        return TickedCounts(new_ticks, self.tick_times, name=self.name, live_times=self.live_times*scale,
                            real_times=self.real_times, msg_times=self.msg_times, blank_rate=self.blank_rate,
                            errors=self.errors, start_time=self.start_time)

    def plot(self, other: List[TickedCounts] = None, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """
        Method which plots the TickedCounts as a function of time, returning the figure and axes.

        Parameters
        ----------
        other: List[TickedCounts]
            Other TickedCounts to plot together

        Returns
        -------
        Tuple[plt.Figure, plt.Axes]
        """
        if other is None:
            other = []
        return TickedCountsPlotter(ticked_counts=[self, *other], **kwargs).plot()

    def simple_windowed_counts(self, tick_window_width: int = 1, mode: int = 0) -> Iterator[Counts]:
        """
        Simple generator of variable length windowed spectra, equivalent to a rolling window across the time space.
        Modes:
        0 - windows are always full. For a TickedSpectrum with N ticks, there will be N - tick_window_width + 1
        spectra yielded.
        1 - windows are always at least half full. For a TickedSpectrum with N ticks, there will be N spectra
        yielded.
        2 - windows are always at least one tick full. For a TickedSpectrum with N ticks, there will be
        N + tick_window_width - 1 spectra yielded.

        Parameters
        ----------
        tick_window_width : int
            width of the window, in ticks. Default: 1.
        mode : int
            sets the mode of the rolling window. default: 0.

        Returns
        -------
        Iterator[Counts]
        """
        if mode == 0:
            for i in range(self.ticks.shape[0] - tick_window_width + 1):
                yield Counts(self.ticks[i:i+tick_window_width].sum(axis=0), name=self.name,
                             error=np.sqrt(np.square(self.errors[i:i+tick_window_width]).sum(axis=0)),
                             comment=self.comment, live_time=self.live_times[i:i+tick_window_width].sum(),
                             real_time=self.real_times[i:i+tick_window_width].sum(),
                             start_time=self.tick_times[i])
        elif mode == 1:
            for i in range(-int(tick_window_width / 2), self.ticks.shape[0] - int(tick_window_width / 2)):
                yield Counts(self.ticks[max(i, 0):i+tick_window_width].sum(axis=0), name=self.name,
                             error=np.sqrt(np.square(self.errors[max(i, 0):i+tick_window_width]).sum(axis=0)),
                             comment=self.comment, live_time=self.live_times[max(i, 0):i+tick_window_width].sum(),
                             real_time=self.real_times[max(i, 0):i+tick_window_width].sum(),
                             start_time=self.tick_times[max(i, 0)])
        elif mode == 2:
            for i in range(-tick_window_width+1, self.ticks.shape[0]):
                yield Counts(self.ticks[max(i, 0):i+tick_window_width].sum(axis=0), name=self.name,
                             error=np.sqrt(np.square(self.errors[max(i, 0):i+tick_window_width]).sum(axis=0)),
                             comment=self.comment, live_time=self.live_times[max(i, 0):i+tick_window_width].sum(),
                             real_time=self.real_times[max(i, 0):i+tick_window_width].sum(),
                             start_time=self.tick_times[max(i, 0)])

    def subtract_background(self, bg_counts: Counts) -> TickedCounts:
        """
        Method which subtracts a background signal from each of the ticks, using simultaneous subtraction.

        Note: Since ticks are short (~0.2s) the noise in the counts is often of the order of the counts themselves, and
        hence the background subtracted counts are often negative.

        Parameters
        ----------
        bg_counts : Counts
            Counts instance containing information about the background count rate.

        Returns
        -------
        TickedCounts
        """
        return self.simultaneous_subtraction(bg_counts)

    def _simultaneous_op_counts(self, other: Counts, add: bool):
        """
        Not sure why you'd want to do this, but it makes logical sense, so here it is.

        Parameters
        ----------
        other : Counts

        Returns
        -------
        TickedCounts
        """
        scale = self.live_times / other.live_time
        return TickedCounts(ticks=self.ticks + (1. if add else -1.)*other.counts * scale,
                            tick_times=self.tick_times,
                            name=self.name,
                            live_times=self.live_times,
                            real_times=self.real_times,
                            msg_times=self.msg_times,
                            blank_rate=self.blank_rate,
                            errors=np.sqrt(self.errors ** 2 + other.error ** 2 * scale),
                            start_time=self.start_time)

    def _simultaneous_op_ticked_counts(self, other: TickedCounts, add: bool):
        """
        Simultaneous sum of two CountsArrays.

        Parameters
        ----------
        other : TickedCounts

        Returns
        -------
        TickedCounts
        """
        if self.n_ticks != other.n_ticks:
            self.log.warning(f'Simultaneous Sum: {self.name} has {self.n_ticks} ticks, but {other.name} has '
                             f'{other.n_ticks} ticks. The longer measurement will be shortened.')
        n_ticks = min(self.n_ticks, other.n_ticks)
        scale = self.live_times[:n_ticks] / other.live_times[:n_ticks]
        return TickedCounts(ticks=self.ticks[:n_ticks] + (1. if add else -1.)*other.ticks[:n_ticks] * scale,
                            tick_times=self.tick_times[:n_ticks],
                            name=self.name,
                            live_times=self.live_times[:n_ticks],
                            real_times=self.real_times[:n_ticks],
                            msg_times=None if self.msg_times is None else self.msg_times[:n_ticks],
                            blank_rate=None if self.blank_rate is None else self.blank_rate[:n_ticks],
                            errors=np.sqrt(self.errors[:n_ticks] ** 2 + other.errors[:n_ticks] ** 2 * scale),
                            start_time=self.start_time)

    def simultaneous_addition(self, other: Union[Counts, TickedCounts]):
        """
        Method which simultaneously adds a measurement to the TickedCounts.

        Parameters
        ----------
        other : Counts or TickedCounts
            Signal to be added.

        Returns
        -------
        TickedCounts
        """
        if isinstance(other, Counts):
            return self._simultaneous_op_counts(other, add=True)
        else:
            return self._simultaneous_op_ticked_counts(other, add=True)

    def simultaneous_subtraction(self, other: Union[Counts, TickedCounts]):
        """
        Method which simultaneously subtracts a signal from the TickedCounts. E.g. background subtraction.

        Parameters
        ----------
        other : Counts
            Signal to be subtracted.

        Returns
        -------
        TickedCounts
        """
        if isinstance(other, Counts):
            return self._simultaneous_op_counts(other, add=False)
        else:
            return self._simultaneous_op_ticked_counts(other, add=False)

    def consecutive_addition(self, other: TickedCounts) -> TickedCounts:
        """
        Method which consecutively sums two TickedCounts instances into a new TickedCounts instance.

        Parameters
        ----------
        other : TickedCounts
            TickedCounts instance to sum onto the end of this TickedCounts instance.

        Returns
        -------
        TickedCounts
        """
        if isinstance(other, Counts):
            raise TypeError('Consecutive addition between TickedCounts and Counts instances makes no real sense...')
        return TickedCounts(ticks=np.concatenate((self.ticks, other.ticks)),
                            tick_times=np.concatenate((self.tick_times, other.tick_times)),
                            live_times=np.concatenate((self.live_times, other.live_times)),
                            real_times=np.concatenate((self.real_times, other.real_times)),
                            name=self.name,
                            msg_times=None if self.msg_times is None or other.msg_times is None else np.concatenate(
                                (self.msg_times, other.msg_times)
                            ),
                            blank_rate=None if self.blank_rate is None or other.blank_rate is None else np.concatenate(
                                (self.blank_rate, other.blank_rate)
                            ),
                            errors=None if self._errors is None and other._errors is None else np.concatenate(
                                (self.errors, other.errors)
                            ),
                            start_time=self.start_time,
                            comment=self.comment)


class TickedCountsArray(TickedArrayBase):
    """
    Array of TickedCounts instances.

    Attributes
    ----------
    elements : OrderedDict[str, Measurement]
        OrderedDict, mapping measurements by their names.

    Methods
    -------
    tick_times() -> Array[datetime]
        Property which returns a list of datetime instances labelling the time at which each tick occurred.
    n_ticks() -> int
        Property which returns the number of ticks in the first member of the array.
    n_ticks_all() -> List[int]
        Property which, like n_ticks, returns the number of ticks, but returns a list of values for each member, in
        case you suspect they may not all contain equal numbers.
    names() -> List[str]
        Property which returns a list of the measurement names which are keys to the mapping.
    number_of_members() -> int
        Property which returns the number of members of the array.
    start_times() -> List[datetime]
        Property which returns a list of datetime instances which give the times at which each member of the array
        began to be collected.
    contains_all(names: List[str]) -> bool
        Method which returns True if all the strings in the argument match the names of elements in the array.
    names_match(other: ArrayBase) -> bool
        Method which returns True if all the names of the other array are present in this array, and vice-versa.
    consecutive_addition(other: TickedCountsArray) -> TickedCountsArray
        Method which returns the consecutive sum of the CountsArray with another Array.
    simultaneous_addition(other: TickedCountsArray) -> TickedCountsArray
        Method which returns the simultaneous sum of the CountsArray with another Array.
    consecutive_subtraction(other: CountsArray) -> TickedCountsArray
        Method which returns the consecutive subtraction of another CountsArray from the Array.
    simultaneous_subtraction(other: CountsArray) -> TickedCountsArray:
        Method which returns the simultaneous subtraction of another CountsArray from the Array.
    subtract_backgrounds(self, backgrounds: CountsArray) -> TickedCountsArray:
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.
    simultaneous_sum() -> TickedCounts
        Simultaneously sum all members of the array.
    consecutive_sum() -> CountsArray
        Sum all ticks into a CountsArray.
    resample(factor: float) -> TickedCountsArray
        Method which returns a new array with each member resampled after scaling by the factor parameter.
    masked_array(names: List[str]) -> TickedCountsArray
        Method which returns a sub-array of this TickedCountsArray. The method returns a new TickedCountsArray
        containing only TickedCounts instances with the names given.
    get_single_tick(tick_num: int) -> CountsArray
        Method which returns a single tick of Counts from each TickedCounts instance in the array, returning a
        CountsArray.
    sum_ticks(start: datetime, end: datetime) -> CountsArray
        Method which sums the ticks in the TickedCountsArray into a CountsArray.
    simple_windowed_counts_arrays(tick_window_width: int = 1, mode: int = 0) -> Iterator[CountsArray]
        Generator for rolling fixed-length windows. Generator yields CountsArrays.
    plot()
        Method which plots each TickedCounts as a function of time, returning the figure and axes.
    """
    def __init__(self, t_counts: List[TickedCounts]):
        super(TickedCountsArray, self).__init__(t_counts)

    def __getitem__(self, item: str) -> TickedCounts:
        return super(TickedCountsArray, self).__getitem__(item)

    def get_single_tick(self, tick_num: int) -> CountsArray:
        """
        Method which returns a single tick of Counts from each TickedCounts instance in the array, returning a
        CountsArray.

        Parameters
        ----------
        tick_num : int
            Index of the tick to be returned.

        Returns
        -------
        CountsArray
        """
        return CountsArray([self[det].get_single_tick(tick_num) for det in self.names])

    def sum_ticks(self, start: Union[datetime, None] = None, end: Union[datetime, None] = None) -> CountsArray:
        """
        Method which sums the ticks in the TickedCountsArray into a CountsArray.

        Parameters
        ----------
        start : datetime
        end : datetime

        Returns
        -------
        CountsArray
        """
        return CountsArray([tc.sum_ticks(start, end) for tc in self])

    def simple_windowed_counts_arrays(self, tick_window_width: int = 1, mode: int = 0) -> Iterator[CountsArray]:
        """
        Generator for rolling fixed-length windows. Generator yields CountsArrays.

        Parameters
        ----------
        tick_window_width : int
            Length of the rolling window, in numbers of ticks.
        mode : int
            Mode (0, 1, or 2)  of the rolling windows.
                0 - windows are always full. For a TickedSpectrum with N ticks, there will be N - tick_window_width + 1
                    spectra yielded.
                    |====================================================| Ticks
                    |====|----------------------------------------->|====| Windows
                1 - windows are always at least half full. For a TickedSpectrum with N ticks, there will be N spectra
                    yielded.
                      |====================================================| Ticks
                    |====|--------------------------------------------->|====| Windows
                2 - windows are always at least one tick full. For a TickedSpectrum with N ticks, there will be
                    N + tick_window_width - 1 spectra yielded.
                         |====================================================| Ticks
                    |====|--------------------------------------------------->|====| Windows

        Yields
        ------
        CountsArray
        """
        generators = [self[d].simple_windowed_counts(tick_window_width, mode) for d in self.names]
        while 1:
            try:
                spectra = [next(gen) for gen in generators]
            except StopIteration:
                return
            yield CountsArray(spectra)

    def masked_array(self, names: List[str]) -> TickedCountsArray:
        """
        Method which returns a sub-array of this TickedCountsArray. The method returns a new TickedCountsArray
        containing only TickedCounts instances with the names given.

        Parameters
        ----------
        names : List[str]
            List of detector names.

        Returns
        -------
        TickedCountsArray
        """
        return self.__class__([self[name] for name in names])

    def plot(self, **kwargs) -> Tuple[plt.Figure, plt.Axes]:
        """
        Method which plots each TickedCounts as a function of time, returning the figure and axes.

        Parameters
        ----------
        xmin : Union[float, int, None]
            Lower bound of the X axis.
        xmax : Union[float, int, None]
            Upper bound of the X axis.
        ymin : Union[float, int, None]
            Lower bound of the Y axis.
        ymax : Union[float, int, None]
            Upper bound of the Y axis.
        axes : Union[plt.Axes, None]
            Optional axes on which to plot the data. If None, the method generates a new figure and axes.
        figsize : Tuple[float, float]
            Tuple containing the dimensions of the figure if the figure is generated in the method.
        xlabel : str
            Text label for the X axis.
        ylabel : str
            Text label for the Y axis.
        title : Union[str, None]
            Optional title for the axes.
        dpi : int
            Dots per inch value for the figure, if generated by the method.
        logy : bool
            False by default. Set to true to scale the Y-axis logarithmically.
        show : bool
            True by default. Set to False to not automatically show the figure.

        Returns
        -------
        Tuple[plt.Figure, plt.Axes]
        """
        return TickedCountsPlotter(ticked_counts=self.elements.values(), **kwargs).plot()

    def subtract_backgrounds(self, bg_array: CountsArray) -> TickedCountsArray:
        """
        Method which subtracts a background CountsArray.

        Parameters
        ----------
        bg_array : CountsArray

        Returns
        -------
        TickedCountsArray
        """
        return self.simultaneous_subtraction(bg_array)

    def simultaneous_addition(self, other: Union[CountsArray, TickedCountsArray]) -> TickedCountsArray:
        """
        Method which simultaneously adds a CountsArray or TickedCountsArray to this TickedCountsArray.
        Not sure why you'd want to though...

        Parameters
        ----------
        other : CountsArray

        Returns
        -------
        TickedCountsArray
        """
        assert self.names_match(other)
        return TickedCountsArray([self[det].simultaneous_addition(other[det]) for det in self.names])

    def simultaneous_subtraction(self, other: Union[CountsArray, TickedCountsArray]) -> TickedCountsArray:
        """
        Method which simultaneously subtracts a CountsArray from this TickedCountsArray. E.g. Background subtraction.

        Parameters
        ----------
        other : CountsArray

        Returns
        -------
        TickedCountsArray
        """
        assert self.names_match(other)
        return TickedCountsArray([self[det].simultaneous_subtraction(other[det]) for det in self.names])

    def consecutive_addition(self, other: TickedCountsArray) -> TickedCountsArray:
        """
        Method which consecutively adds a TickedCountsArray to this TickedCountsArray. Not sure why you'd want to
        though...

        Parameters
        ----------
        other : CountsArray

        Returns
        -------
        TickedCountsArray
        """
        return super(TickedCountsArray, self).consecutive_addition(other)

    def consecutive_sum(self) -> TickedCounts:
        """
        Consecutive sum of each member of the array.

        Returns
        -------
        TickedCounts
        """
        result: Union[TickedCounts, None] = None
        for ticked_counts in self:
            if result is None:
                result = ticked_counts
            else:
                result = result.consecutive_addition(ticked_counts)
        return result

    def simultaneous_sum(self) -> TickedCounts:
        """
        Simultaneous sum tick-wise of each member of the array.

        Returns
        -------
        TickedCounts
        """
        result: Union[TickedCounts, None] = None
        for ticked_counts in self:
            if result is None:
                result = ticked_counts
            else:
                result = result.simultaneous_addition(ticked_counts)
        return result

    def resample(self, factor: float) -> TickedCountsArray:
        """
        Method which returns a new array with each member resampled after scaling by the factor parameter.

        Parameters
        ----------
        factor : float
            Scale by which the measurements will be scaled before resampling.

        Returns
        -------
        TickedCountsArray
        """
        return super(TickedCountsArray, self).resample(factor)
