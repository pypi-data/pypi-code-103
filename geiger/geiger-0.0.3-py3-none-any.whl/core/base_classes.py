from __future__ import annotations
from abc import ABC
from datetime import datetime, timedelta
from typing import Union, List, Any
import logging
from copy import deepcopy
import numpy as np
from collections import OrderedDict


class MeasurementBase(ABC):
    """
    Base class for all measurement types (Counts and Spectrum so far).

    Attributes
    ----------
    live_time : float
        The live time of the measurement
    real_time : float
        The real time of the measurement
    name : str
        Optional name to attach to the measurement.
    comment : str
        Optional comment to attach to the measurement.
    start_time : datetime
        Optional time at which the measurement began.
    log : logging.Logger
        Logger for logging loggable log logs.

    Methods
    -------
    end_time() -> datetime or None
        Property returning the end time of the measurement. "The end times are nigh."
    copy_me() -> Measurement
        Method which returns a deep copy of the measurement.
    resample(factor: float = 1.0) -> Measurement
        Must be implemented by subclasses.
    subtract_background(background: Measurement) -> Measurement
        Method which subtracts a background signal from the measurement.
    consecutive_addition(other: MeasurementBase) -> Measurement
        Must be implemented by subclasses.
    simultaneous_addition(other: MeasurementBase) -> Measurement
        Must be implemented by subclasses.
    consecutive_subtraction(other: MeasurementBase) -> Measurement
        Must be implemented by subclasses.
    simultaneous_subtraction(other: MeasurementBase) -> Measurement
        Must be implemented by subclasses.
    """
    def __init__(self,
                 live_time: float = 1.0,
                 real_time: float = 1.0,
                 name: str = '',
                 comment: str = '',
                 start_time: Union[datetime, None] = None):
        """
        Parameters
        ----------
        live_time : float
            The live time of the measurement
        real_time : float
            The real time of the measurement
        name : str
            Optional name to attach to the measurement.
        comment : str
            Optional comment to attach to the measurement.
        start_time : datetime
            Optional time at which the measurement began.
        """
        self.live_time = live_time
        self.real_time = real_time
        self.name = name
        self.comment = comment
        self.start_time = start_time
        self.log = logging.getLogger(f"{self.__class__.__name__}:{self.name}")
        self.log.debug(f"Created {self.__class__.__name__}({self.name})")

    @property
    def end_time(self) -> Union[datetime, None]:
        """
        Property which returns the time at which the measurement ended, if the start time is known, otherwise it
        returns None.

        Returns
        -------
        datetime
        """
        return None if self.start_time is None else self.start_time + timedelta(seconds=self.real_time)

    def copy_me(self):
        """
        Method which returns a deep copy of the measurement.

        Returns
        -------
        CopiedMeasurement
        """
        return deepcopy(self)

    def resample(self, factor: float = 1.0) -> MeasurementBase:
        raise NotImplementedError

    def subtract_background(self, background: MeasurementBase):
        """
        Method which subtracts a background signal from the measurement.

        Parameters
        ----------
        background : MeasurementBase

        Returns
        -------
        BackgroundSubtractedMeasurement
        """
        return self.simultaneous_subtraction(background)

    def consecutive_addition(self, other: MeasurementBase):
        raise NotImplementedError

    def simultaneous_addition(self, other: MeasurementBase):
        raise NotImplementedError

    def consecutive_subtraction(self, other: MeasurementBase):
        raise NotImplementedError

    def simultaneous_subtraction(self, other: MeasurementBase):
        raise NotImplementedError


class TickedMeasurement(MeasurementBase, ABC):
    """
    Base class for all ticked measurement types (TickedCounts and TickedSpectrum so far).

    Attributes
    ----------
    tick_times : Array[datetime]
        Numpy array of datetime objects, labelling the times at which the ticks occurred.
    live_times : Array[float]
        Numpy array of floats, determining the live times of each tick.
    real_times : Array[float]
        Numpy array of floats, determining the real times of each tick.
    live_time : float
        The total live time of the measurement
    real_time : float
        The total real time of the measurement
    name : str
        Optional name to attach to the measurement.
    comment : str
        Optional comment to attach to the measurement.
    start_time : datetime
        Optional time at which the measurement began.
    log : logging.Logger
        Logger for logging loggable log logs.

    Methods
    -------
    n_ticks() -> int
        Property which returns the number of ticks in the measurement.
    end_time() -> datetime or None
        Property returning the end time of the measurement. "The end times are nigh."
    copy_me() -> Measurement
        Method which returns a deep copy of the measurement.
    resample(factor: float = 1.0) -> Measurement
        Must be implemented by subclasses.
    subtract_background(background: Measurement) -> Measurement
        Method which subtracts a background signal from the measurement.
    consecutive_addition(other: MeasurementBase) -> Measurement
        Must be implemented by subclasses.
    simultaneous_addition(other: MeasurementBase) -> Measurement
        Must be implemented by subclasses.
    consecutive_subtraction(other: MeasurementBase) -> Measurement
        This method cannot be used for ticked types. Raises TypeError always.
    simultaneous_subtraction(other: MeasurementBase) -> Measurement
        Must be implemented by subclasses.
    get_single_tick(tick_number: int) -> Measurement
        Must be implemented by subclasses.
    sum_ticks(start: datetime = None, end: datetime = None) -> Measurement
        Must be implemented by subclasses.
    """
    def __init__(self,
                 tick_times: np.ndarray,
                 live_times: np.ndarray,
                 real_times: np.ndarray,
                 name: str = '',
                 comment: str = '',
                 start_time: Union[datetime, None] = None):
        """
        Parameters
        ----------
        tick_times : Array[datetime]
            Numpy array of datetime objects, labelling the times at which the ticks occurred.
        live_times : Array[float]
            Numpy array of floats, determining the live times of each tick.
        real_times : Array[float]
            Numpy array of floats, determining the real times of each tick.
        name : str
            Optional name to attach to the measurement.
        comment : str
            Optional comment to attach to the measurement.
        start_time : datetime
            Optional time at which the measurement began.
        """
        if start_time is None:
            start_time = tick_times[0]
        super().__init__(live_time=live_times.sum(),
                         real_time=real_times.sum(),
                         name=name,
                         comment=comment,
                         start_time=start_time)
        self.tick_times = tick_times
        self.live_times = live_times
        self.real_times = real_times

    @property
    def n_ticks(self) -> int:
        """
        Property which returns the number of ticks in the measurement.

        Returns
        -------
        int
        """
        return self.tick_times.size

    def get_single_tick(self, tick_number: int):
        raise NotImplementedError

    def sum_ticks(self, start: Union[datetime, None] = None, end: Union[datetime, None] = None):
        raise NotImplementedError

    def consecutive_subtraction(self, other: MeasurementBase):
        raise TypeError('Consecutive subtraction makes no sense for ticked types.')


class ArrayBase:
    """
    Base class for all Array types (CountsArray, SpectrumArray, TickedCountsArray and TickedSpectrumArray so far).

    Attributes
    ----------
    elements : OrderedDict[str, Measurement]
        OrderedDict, mapping measurements by their names.

    Methods
    -------
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
    consecutive_addition(other: ArrayBase) -> ArrayBase
        Method which returns the consecutive sum of the CountsArray with another Array.
    simultaneous_addition(other: ArrayBase) -> ArrayBase
        Method which returns the simultaneous sum of the CountsArray with another Array.
    consecutive_subtraction(other: ArrayBase) -> ArrayBase
        Method which returns the consecutive subtraction of another CountsArray from the Array.
    simultaneous_subtraction(other: ArrayBase) -> ArrayBase:
        Method which returns the simultaneous subtraction of another CountsArray from the Array.
    subtract_backgrounds(self, backgrounds: ArrayBase) -> ArrayBase:
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.
    simultaneous_sum() -> MeasurementBase
        Must be implemented by subclasses.
    consecutive_sum() -> MeasurementBase
        Must be implemented by subclasses.
    resample(factor: float) -> ArrayBase
        Method which returns a new array with each member resampled after scaling by the factor parameter.
    masked_array(names: List[str]) -> ArrayBase
        Method which returns a new array consisting only of members with the names in the given list of names.
    """
    def __init__(self, items):
        self.elements = OrderedDict([(i.name, i) for i in items])

    def __getitem__(self, item: str):
        return self.elements[item]

    def get(self, key: str, default_val: Any = None):
        return self.elements.get(key, default_val)

    def __setitem__(self, key: str, value):
        self.elements[key] = value

    def __contains__(self, item: str) -> bool:
        return item in self.elements

    def __iter__(self):
        for k in self.elements:
            yield self.elements[k]

    @property
    def names(self) -> List[str]:
        """
        Property which returns a list of the 'names' attributes for each member of the array.

        Returns
        -------
        List[str]
        """
        return list(self.elements.keys())

    @property
    def number_of_members(self) -> int:
        """
        Property which returns the number of members of the array.

        Returns
        -------
        int
        """
        return len(self.elements)

    @property
    def start_times(self) -> List[datetime]:
        """
        Property which returns a list of the 'start_time' attributes for each member of the array. The values are
        datetime objects or None.

        Returns
        -------
        List[Union[str, None]]
        """
        return [e.start_time for e in self]

    def contains_all(self, names: List[str]) -> bool:
        """
        Method which returns True if all the strings in the argument match the names of elements in the array.

        Parameters
        ----------
        names : List[str]
            List of names to match.

        Returns
        -------
        bool
        """
        return all([name in self for name in names])

    def names_match(self, other: ArrayBase):
        """
        Method which returns True if all the names of the other array are present in this array, and vice-versa.

        Parameters
        ----------
        other : Array

        Returns
        -------
        bool
        """
        return self.contains_all(other.names) and other.contains_all(self.names)

    def consecutive_addition(self, other: ArrayBase):
        """
        Method which returns the consecutive sum of the CountsArray with another Array.

        Parameters
        ----------
        other : Array
            The Array instance to add to this one.

        Returns
        -------
        Array
        """
        assert self.names_match(other)
        return self.__class__([d.consecutive_addition(other[d.name]) for d in self])

    def simultaneous_addition(self, other: ArrayBase):
        """
        Method which returns the simultaneous sum of the CountsArray with another Array.

        Parameters
        ----------
        other : Array
            The Array instance to add to this one.

        Returns
        -------
        Array
        """
        assert self.names_match(other)
        return self.__class__([d.simultaneous_addition(other[d.name]) for d in self])

    def consecutive_subtraction(self, other: ArrayBase):
        """
        Method which returns the consecutive subtraction of another CountsArray from the Array.

        Parameters
        ----------
        other : Array
            The Array instance to subtract from this one.

        Returns
        -------
        Array
        """
        assert self.names_match(other)
        return self.__class__([d.consecutive_subtraction(other[d.name]) for d in self])

    def simultaneous_subtraction(self, other: ArrayBase):
        """
        Method which returns the simultaneous subtraction of another CountsArray from the Array.

        Parameters
        ----------
        other : Array
            The Array instance to subtract from this one.

        Returns
        -------
        Array
        """
        assert self.names_match(other)
        return self.__class__([d.simultaneous_subtraction(other[d.name]) for d in self])

    def subtract_backgrounds(self, backgrounds: ArrayBase):
        """
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.

        Parameters
        ----------
        backgrounds : ArrayBase

        Returns
        -------
        Array
        """
        return self.simultaneous_subtraction(backgrounds)

    def simultaneous_sum(self):
        raise NotImplementedError

    def consecutive_sum(self):
        raise NotImplementedError

    def resample(self, factor: float):
        """
        Method which returns a new array with each member resampled after scaling by the factor parameter.

        Parameters
        ----------
        factor : float
            Scale by which the measurements will be scaled before resampling.

        Returns
        -------
        Array
        """
        return self.__class__([e.resample(factor) for e in self])

    def masked_array(self, names: List[str]):
        """
        Method which returns a new array consisting only of members with the names in the given list of names.

        Parameters
        ----------
        names : List[str]

        Returns
        -------
        Array
        """
        assert self.contains_all(names)
        return self.__class__([self[name] for name in names])


class TickedArrayBase(ArrayBase, ABC):
    """
    Base class for all TickedArray types (TickedCountsArray and TickedSpectrumArray so far).

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
    consecutive_addition(other: ArrayBase) -> ArrayBase
        Method which returns the consecutive sum of the CountsArray with another Array.
    simultaneous_addition(other: ArrayBase) -> ArrayBase
        Method which returns the simultaneous sum of the CountsArray with another Array.
    consecutive_subtraction(other: ArrayBase) -> ArrayBase
        This method makes no sense...
    simultaneous_subtraction(other: ArrayBase) -> ArrayBase:
        Method which returns the simultaneous subtraction of another CountsArray from the Array.
    subtract_backgrounds(self, backgrounds: ArrayBase) -> ArrayBase:
        Method which subtracts the background from each member of the array, using the array of background counts
        supplied as the argument.
    simultaneous_sum() -> MeasurementBase
        Must be implemented by subclasses.
    consecutive_sum() -> MeasurementBase
        Must be implemented by subclasses.
    resample(factor: float) -> ArrayBase
        Method which returns a new array with each member resampled after scaling by the factor parameter.
    masked_array(names: List[str]) -> ArrayBase
        Method which returns a new array consisting only of members with the names in the given list of names.
    get_single_tick(tick_num: int) -> ArrayBase
        Must be implemented by subclasses.
    sum_ticks(start: datetime, end: datetime) -> ArrayBase
        Must be implemented by subclasses.
    """
    def __init__(self, items: List[TickedMeasurement]):
        super(TickedArrayBase, self).__init__(items)

    @property
    def tick_times(self) -> np.ndarray:
        """
        Property which returns a list of datetime instances labelling the time at which each tick occurred (for the
        first member of the array).

        Returns
        -------
        Array[datetime]
        """
        return self[self.names[0]].tick_times

    @property
    def n_ticks(self) -> int:
        """
        Property which returns the number of ticks in the first member of the array.

        Returns
        -------
        int
        """
        return self.tick_times.size

    @property
    def n_ticks_all(self) -> List[int]:
        """
        Property which, like n_ticks, returns the number of ticks, but returns a list of values for each member, in
        case you suspect they may not all contain equal numbers.

        Returns
        -------
        List[int]
        """
        return [self[name].n_ticks for name in self.names]

    def get_single_tick(self, tick_num: int):
        raise NotImplementedError

    def sum_ticks(self, start: Union[datetime, None] = None, end: Union[datetime, None] = None):
        raise NotImplementedError
