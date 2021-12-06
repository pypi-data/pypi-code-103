#!/usr/bin/env python3
# Copyright 2004-present Facebook. All Rights Reserved.

# Built-in imports
import asyncio
import queue
from dataclasses import field
from typing import List, Tuple

# Import labgraph
import labgraph as lg
import numpy as np

# Import labgraph_viz & other graphics libs
from arvr.libraries.labgraph_viz.v1.plots import LinePlot, LinePlotConfig, Mode
from scipy import signal

# ==== Example README ====
# In this example we demo a simple bandpass filter by building the following graph
# 1. A Node that generates a sine wave signal
# 2. A Node that generates random values
# 3. A Node that adds up two signals
# 4. Using the 3 Nodes above we can generate a group that creates a "noisy" signal
#    composed of the base sine wave plus random noise at a higher frequency
# 5. We have one more node that is a bandpass filter, we use the output of group #4
#   as input to the bandpass filter
# 6. We output the original base, the noisy signal and the filtered signal into a
#   line plot that uses labgraph_viz to render this in a window

# ==  Signal configuration ===
# We will take 50 samples per second for all signals (Base, Noise, Filtered ... etc.)
SAMPLE_RATE = 50.0
# In this example our base signal will have a max amplitude of 10 in its "clean form"
BASE_AMPLITUDE = 10.0
# In this example we want our signal to have a period of 4 seconds (i.e. 0.25 Hz)
BASE_FREQUENCY = 0.25

# In this example our noise signal will have a max amplitude of 1
NOISE_AMPLITUDE = 1.0
# In this example we want our noise to have a period of 0.2 seconds (i.e. 5 Hz)
NOISE_FREQUENCY = 5.0

# The frequency at where we want to cut off, Ideally between noise and base
CUTOFF_FREQUENCY = 1.0

# Time window in which we sample in order to filter (Seconds)
SAMPLE_PERIOD = 8.0


class SignalMessage(lg.Message):
    """
    # A single-channel message that carries the time and the amplitude of a signal
    """

    timestamp: float
    data: float


# ================== SIGNAL GENERATOR ====================
class SineWaveGeneratorConfig(lg.Config):
    amplitude: float
    frequency: float
    sample_rate: float

    def __post_init__(self) -> None:
        assert self.sample_rate > 0.0


class SineWaveGenerator:
    """
    This is a simple SineWave Generator based on the config parameters.
    """

    def __init__(self, config: SineWaveGeneratorConfig) -> None:
        self.signal_config = config
        # This is time, which starts at zero
        self._time = 0.0

    def next_sample(self) -> SignalMessage:
        # Calculate output of the set of sine waves
        angle = self.signal_config.frequency * 2 * np.pi * self._time
        sample = self.signal_config.amplitude * np.sin(angle)
        sample_message = SignalMessage(timestamp=self._time, data=sample)
        # Update time
        self._time += 1 / self.signal_config.sample_rate
        return sample_message


class SignalGeneratorNode(lg.Node):

    OUTPUT = lg.Topic(SignalMessage)
    config: SineWaveGeneratorConfig

    def setup(self):
        self._shutdown = asyncio.Event()

    def cleanup(self):
        self._shutdown.set()

    @lg.publisher(OUTPUT)
    async def publish_samples(self) -> lg.AsyncPublisher:
        generator = SineWaveGenerator(self.config)
        while not self._shutdown.is_set():
            sample_message = generator.next_sample()
            yield self.OUTPUT, sample_message
            await asyncio.sleep(1 / self.config.sample_rate)


# ==== ADDING NODE =======
class SignalSumNode(lg.Node):

    INPUT_SIGNAL_LEFT = lg.Topic(SignalMessage)
    INPUT_SIGNAL_RIGHT = lg.Topic(SignalMessage)
    OUT_SIGNAL_SUM = lg.Topic(SignalMessage)
    # We just need sample rate so any config will do
    config: SineWaveGeneratorConfig

    def setup(self) -> None:
        self._left_in: queue.Queue = queue.Queue()
        self._right_in: queue.Queue = queue.Queue()
        self._shutdown = asyncio.Event()

    def cleanup(self) -> None:
        self._shutdown.set()

    @lg.subscriber(INPUT_SIGNAL_LEFT)
    def left_input(self, in_sample: SignalMessage) -> None:
        self._left_in.put(in_sample)

    @lg.subscriber(INPUT_SIGNAL_RIGHT)
    def right_input(self, in_sample: SignalMessage) -> None:
        self._right_in.put(in_sample)

    @lg.publisher(OUT_SIGNAL_SUM)
    async def sum_samples(self) -> lg.AsyncPublisher:
        while not self._shutdown.is_set():
            while self._left_in.empty() or self._right_in.empty():
                # We sample a bit faster in the mixer (sleep 0.9T instead of 1T)
                await asyncio.sleep(0.9 / self.config.sample_rate)
            left = self._left_in.get()
            right = self._right_in.get()
            sum_output = left.data + right.data
            # In this example we expect timestamps to be about the same since
            # all signals share sample rate, so we use left.
            out_sample = SignalMessage(timestamp=left.timestamp, data=sum_output)
            yield self.OUT_SIGNAL_SUM, out_sample


# ==== FILTER ====
# The state of the RollingAverager node: holds windowed messages
class RollingState(lg.State):
    time: float = 0.0
    messages: List[SignalMessage] = field(default_factory=list)


class FilterConfig(lg.Config):
    # Cutoff frequency : desired cutoff frequency of the filter (Hz)
    cutoff_frequency: float
    # Order of the filter
    order: int
    sample_rate: float
    sample_period: float  # Window, in seconds, to filter over

    def __post_init__(self) -> None:
        assert self.sample_rate > 0.0


class LowPassFilterNode(lg.Node):
    """
    This node serves as a low passs filter for the input signal.
    Uses a rough butterworth implementation
    """

    INPUT = lg.Topic(SignalMessage)
    OUTPUT = lg.Topic(SignalMessage)
    state: RollingState
    config: FilterConfig

    def setup(self) -> None:
        # Nyquist Frequency = 0.5*sample_rate
        # Normal Cuttof = cutoff/nyq
        self._normal_cutoff = self.config.cutoff_frequency * 2 / self.config.sample_rate

        # Get the params for butter filter
        b, a = signal.butter(
            self.config.order, self._normal_cutoff, "low", analog=False
        )
        self._filter_param_a = a
        self._filter_param_b = b

    # A transformer method that transforms data from one topic into another
    @lg.subscriber(INPUT)
    @lg.publisher(OUTPUT)
    async def filter(self, message: SignalMessage) -> lg.AsyncPublisher:

        self.state.messages.append(message)
        self.state.messages = [
            message
            for message in self.state.messages
            if message.timestamp >= self.state.time - self.config.sample_period
        ]
        if len(self.state.messages) < 10:
            return

        all_data = np.array([message.data for message in self.state.messages])

        # calculate the filtered signal at the end of the window
        y = signal.filtfilt(self._filter_param_b, self._filter_param_a, all_data)

        # Output takes the first message which is the earliest computable
        # and outputs as message
        out_msg = SignalMessage(timestamp=message.timestamp, data=y[0])

        # Update time
        self.state.time += 1 / self.config.sample_rate

        yield self.OUTPUT, out_msg


# =============================== PLOT WINDOW ===============================
class Window(lg.Node):
    """
    This is an example of a cusom Window Node.
    It creates a new window, sets some properties of the Window,
    adds some plots and starts the QT application.
    """

    BASE_PLOT: LinePlot
    NOISE_PLOT: LinePlot
    FILTERED_PLOT: LinePlot

    @lg.main
    def run_plot(self) -> None:
        import pyqtgraph as pg  # type: ignore
        from pyqtgraph.Qt import QtGui  # type: ignore

        win = pg.GraphicsWindow()
        win.setWindowTitle("Bandpass Example")

        win.addItem(self.BASE_PLOT.build())
        win.nextRow()
        win.addItem(self.NOISE_PLOT.build())
        win.nextRow()
        win.addItem(self.FILTERED_PLOT.build())
        QtGui.QApplication.instance().exec_()

    def cleanup(self) -> None:
        from pyqtgraph.Qt import QtGui  # type: ignore

        QtGui.QApplication.instance().quit()


class VizGroup(lg.Group):
    """
    This is a simple example of how we can display the LinePlot
    in a custom Window Node.

    Note that we map the message fields to x_field and y_field
    in self.PLOT.configure to tell the LinePlot which data is associated
    with which axis.
    """

    BASE_PLOT: LinePlot
    NOISE_PLOT: LinePlot
    FILTERED_PLOT: LinePlot
    WINDOW: Window

    def setup(self) -> None:
        self.BASE_PLOT.configure(self.plot_config())
        self.NOISE_PLOT.configure(self.plot_config())
        self.FILTERED_PLOT.configure(self.plot_config())
        self.WINDOW.BASE_PLOT = self.BASE_PLOT
        self.WINDOW.NOISE_PLOT = self.NOISE_PLOT
        self.WINDOW.FILTERED_PLOT = self.FILTERED_PLOT

    def plot_config(self) -> LinePlotConfig:
        return LinePlotConfig(
            x_field="timestamp", y_field="data", mode=Mode.APPEND, window_size=200
        )

    def process_modules(self) -> Tuple[lg.Module, ...]:
        return (self.BASE_PLOT, self.NOISE_PLOT, self.FILTERED_PLOT, self.WINDOW)


# =============================== DEMO =================================
class Demo(lg.Graph):
    """
    A simple graph showing how we can add our group
    """

    BASE_SIGNAL: SignalGeneratorNode
    NOISE_SIGNAL: SignalGeneratorNode
    NOISY_SIGNAL_ADDER: SignalSumNode
    LOWPASS_FILTER: LowPassFilterNode
    VIZ: VizGroup

    def setup(self) -> None:

        base_signal_config = SineWaveGeneratorConfig(
            amplitude=BASE_AMPLITUDE,
            frequency=BASE_FREQUENCY,
            sample_rate=SAMPLE_RATE,
        )

        noise_signal_config = SineWaveGeneratorConfig(
            amplitude=NOISE_AMPLITUDE,
            frequency=NOISE_FREQUENCY,
            sample_rate=SAMPLE_RATE,
        )

        filter_config = FilterConfig(
            cutoff_frequency=CUTOFF_FREQUENCY,
            order=2,
            sample_rate=SAMPLE_RATE,
            sample_period=SAMPLE_PERIOD,
        )

        self.BASE_SIGNAL.configure(base_signal_config)
        self.NOISE_SIGNAL.configure(noise_signal_config)
        self.NOISY_SIGNAL_ADDER.configure(noise_signal_config)
        self.LOWPASS_FILTER.configure(filter_config)

    def connections(self) -> lg.Connections:
        return (
            # Base signal goes both to the adder and the plot
            (self.BASE_SIGNAL.OUTPUT, self.VIZ.BASE_PLOT.INPUT),
            (self.BASE_SIGNAL.OUTPUT, self.NOISY_SIGNAL_ADDER.INPUT_SIGNAL_LEFT),
            (self.NOISE_SIGNAL.OUTPUT, self.NOISY_SIGNAL_ADDER.INPUT_SIGNAL_RIGHT),
            (self.NOISY_SIGNAL_ADDER.OUT_SIGNAL_SUM, self.VIZ.NOISE_PLOT.INPUT),
            (self.NOISY_SIGNAL_ADDER.OUT_SIGNAL_SUM, self.LOWPASS_FILTER.INPUT),
            (self.LOWPASS_FILTER.OUTPUT, self.VIZ.FILTERED_PLOT.INPUT),
        )

    def process_modules(self) -> Tuple[lg.Module, ...]:
        return (
            self.BASE_SIGNAL,
            self.NOISE_SIGNAL,
            self.NOISY_SIGNAL_ADDER,
            self.LOWPASS_FILTER,
            self.VIZ,
        )


if __name__ == "__main__":
    graph = Demo()
    runner = lg.LocalRunner(module=graph)
    runner.run()
