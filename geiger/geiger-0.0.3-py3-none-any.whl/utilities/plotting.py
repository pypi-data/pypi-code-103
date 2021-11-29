# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 18:24:00 2018

@author: Ian Della-Rocca
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from dataclasses import dataclass, field
from typing import Union, NewType, Tuple, List, Any
from datetime import datetime, timedelta
from abc import ABC

Number = NewType('Number', Union[int, float, None])
Spectrum = NewType('Spectrum', Any)
TickedCounts = NewType('TickedCounts', Any)
HealthLibrary = NewType('HealthLibrary', Any)
HealthTracker = NewType('HealthTracker', Any)


@dataclass
class PlotterBase:
    xmin: Number = 0.
    xmax: Number = None
    ymin: Number = 0.
    ymax: Number = None
    xlabel: str = 'Energy [keV]'
    ylabel: str = 'Counts'
    title: str = None
    figsize: Tuple[float, float] = (9., 5.)
    dpi: int = 80
    logy: bool = False
    v_lines: List[float] = None
    h_lines: List[float] = None
    v_line_col: str = 'r'
    h_line_col: str = 'b'
    show: bool = True
    tight: bool = False
    save: str = None
    close: bool = False
    axis: Union[plt.Axes, None] = None
    legend: bool = True
    colors: List[str] = None

    figure: plt.Figure = field(init=False,  default=None)

    def __post_init__(self):
        if self.colors is None:
            self.colors = [f'C{i}' for i in range(10)]
        if self.axis is None:
            self.figure, self.axis = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        else:
            self.figure = self.axis.figure

        self.axis.set_xlabel(self.xlabel)
        self.axis.set_ylabel(self.ylabel)

        self.axis.set_title(self.title)

    def plot(self):
        self._do_plotting()
        self._finalize_plot()
        return self.figure, self.axis

    def _do_plotting(self):
        raise NotImplementedError

    def _finalize_plot(self):
        if self.legend:
            self.axis.legend()

        self.axis.set_xlim(left=self.xmin, right=self.xmax)
        self.axis.set_ylim(bottom=self.ymin, top=self.ymax)

        if self.logy:
            self.axis.set_yscale('logy')
            if self.xmin == 0.:
                self.axis.set_ylim(bottom=None)

        if self.v_lines is not None:
            for line in self.v_lines:
                self.axis.axvline(line, color=self.v_line_col)
        if self.h_lines is not None:
            for line in self.h_lines:
                self.axis.axhline(line, color=self.h_line_col)

        if self.tight:
            plt.tight_layout()

        if self.save is not None:
            self.figure.savefig(self.save)

        if self.show:
            plt.show()

        if self.close:
            plt.close(self.figure)


@dataclass
class SpectrumPlotter(PlotterBase):
    spectra: List[Spectrum] = field(default_factory=[])

    def _do_plotting(self):
        for i, spectrum in enumerate(self.spectra):
            self.axis.step(spectrum.energies, spectrum.counts, where='mid', color=self.colors[i], label=spectrum.name)


@dataclass
class TimeSeriesPlotter(PlotterBase, ABC):
    xmin: Union[datetime, None] = None
    xmax: Union[datetime, None] = None
    xlabel: str = 'Time'
    ylabel: str = 'Value'
    figsize: Tuple[float, float] = (14., 7.)
    x_tick_interval: Union[float, None] = None

    earliest: datetime = field(init=False)
    latest: datetime = field(init=False)

    def __post_init__(self):
        super(TimeSeriesPlotter, self).__post_init__()
        self.set_earliest_and_latest()
        if self.x_tick_interval is None:
            threshold1 = 20.
            threshold2 = 100.
            threshold3 = 300.
            threshold4 = 1800.
            threshold5 = 3600.
            threshold6 = 21600.
            threshold7 = 43200.
            threshold8 = 86400.
            total_interval = (self.latest - self.earliest).total_seconds()
            if total_interval <= threshold1:
                tick_interval = 1.0
            elif threshold1 < total_interval <= threshold2:
                tick_interval = 5.0
            elif threshold2 < total_interval <= threshold3:
                tick_interval = 10.0
            elif threshold3 < total_interval <= threshold4:
                tick_interval = 60.0
            elif threshold4 < total_interval <= threshold5:
                tick_interval = 300.0
            elif threshold5 < total_interval <= threshold6:
                tick_interval = 1800.0
            elif threshold6 < total_interval <= threshold7:
                tick_interval = 3600.0
            elif threshold7 < total_interval <= threshold8:
                tick_interval = 7200.0
            else:
                tick_interval = 21600.0
            self.x_tick_interval = tick_interval
        day_of_earliest = datetime(year=self.earliest.year, month=self.earliest.month,
                                   day=self.earliest.day, tzinfo=self.earliest.tzinfo)
        minor_ticks = [self.earliest - timedelta(seconds=((self.earliest - day_of_earliest).total_seconds() %
                                                 self.x_tick_interval - self.x_tick_interval))]
        while minor_ticks[-1] < self.latest:
            minor_ticks.append(minor_ticks[-1] + timedelta(seconds=self.x_tick_interval))
        minor_ticks.pop(-1)
        self.axis.set_xticks([self.earliest, self.latest])
        self.axis.set_xticks(minor_ticks, minor=True)
        # plt.xticks(rotation=90)
        # plt.setp(self.axis.xaxis.get_minorticklabels(), rotation=0)
        plt.setp(self.axis.xaxis.get_majorticklabels(), fontweight='bold')
        if self.x_tick_interval < 60.:
            self.axis.xaxis.set_minor_formatter(mpl_dates.DateFormatter('%H:%M:%S'))
            self.axis.xaxis.set_major_formatter(mpl_dates.DateFormatter('\n%H:%M:%S'))
        else:
            self.axis.xaxis.set_minor_formatter(mpl_dates.DateFormatter('%H:%M:%S'))
            self.axis.xaxis.set_major_formatter(mpl_dates.DateFormatter('\n%x\n%X'))

    def set_earliest_and_latest(self):
        raise NotImplementedError


@dataclass
class TickedCountsPlotter(TimeSeriesPlotter):
    ticked_counts: List[TickedCounts] = field(default_factory=[])
    ylabel: str = 'Counts'

    def set_earliest_and_latest(self):
        self.earliest = min([tc.tick_times[tc.tick_times != None][0] for tc in self.ticked_counts])
        self.latest = max([tc.tick_times[tc.tick_times != None][-1] for tc in self.ticked_counts])

    def _do_plotting(self):
        for i, item in enumerate(self.ticked_counts):
            self.axis.step(item.tick_times, item.ticks, where='post', color=self.colors[i], label=item.name)

