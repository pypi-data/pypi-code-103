import collections
import datetime
import enum
import logging
import multiprocessing.connection
import os
import signal
import sys
import threading
import time

import numpy
import psutil
from PySide2 import QtCore

from hyperborea.namedprocess import NamedProcess
from hyperborea.proxy import DeviceLoggerAdapter, RemoteToLocalLogHandler
from hyperborea.ringbuffer import RingBuffer

logger = logging.getLogger(__name__)


@enum.unique
class CalcData(enum.Enum):
    CHANNEL_UPDATE = 0
    PLOT_UPDATE = 1
    FFT_UPDATE = 2
    LOST_PACKET_UPDATE = 3
    UNKNOWN_ID = 4


@enum.unique
class CalcControl(enum.Enum):
    STOP = 0  # stop the packet processing, but still pull them from the pipe
    CLOSE = 1
    SET_SHOWN = 2
    PLOT_CHANGE = 3
    RESET_LOST_PACKETS = 4


class CalcRunner:
    def __init__(self, packet_pipe, data_pipe, ctrl_pipe, serial_number,
                 is_shown, device_decoder, channel_infos, channel_indexes,
                 channel_interval, plot_interval, fft_interval):
        self.packet_pipe = packet_pipe
        self.data_pipe = data_pipe
        self.ctrl_pipe = ctrl_pipe
        self.serial_number = serial_number
        self.is_shown = is_shown
        self.device_decoder = device_decoder
        self.channel_infos = channel_infos
        self.channel_indexes = channel_indexes
        self.channel_interval = channel_interval
        self.plot_interval = plot_interval
        self.fft_interval = fft_interval

        self.current_channel_index = None
        self.current_subchannel_index = None

        self.data_lock = threading.Lock()

        self.lost_packet_lock = threading.Lock()
        self.lost_packet_count = 0
        self.lost_packet_last_time = None
        self.recent_lost_packet_count = 0
        self.lost_packet_deque = collections.deque()
        self.last_lost_packet_update = None

        self.logger = DeviceLoggerAdapter(logger, self.serial_number)

        self.stopped = threading.Event()

        self.update_thread = threading.Thread(target=self.update_thread_run)

        self.setup_decoder()

    def setup_decoder(self):
        self.device_decoder.set_unknown_id_callback(self.unknown_id_cb)

        channel_count = len(self.channel_infos)
        self.mean_ringbuffers = [None] * channel_count
        self.plot_ringbuffers = [None] * channel_count
        self.fft_ringbuffers = [None] * channel_count

        channel_decoders = {}
        for i, stream_decoder in enumerate(self.device_decoder.decoders):
            stream_id = self.device_decoder.stream_ids[i]
            lost_packet_cb = self.create_lost_packet_callback(stream_id)
            stream_decoder.set_lost_packet_callback(lost_packet_cb)
            for j, channel_decoder in enumerate(stream_decoder.decoders):
                channel_id = stream_decoder.stream_info.channel_index_list[j]
                channel_decoders[channel_id] = channel_decoder

        # operate on the channel decoders sorted by channel index
        for channel_id in sorted(channel_decoders.keys()):
            channel_decoder = channel_decoders[channel_id]
            channel_index = self.channel_indexes[channel_id]
            if channel_index is not None:
                self.setup_channel(channel_index, channel_decoder)

    def setup_channel(self, channel_index, channel_decoder):
        channel_info = self.channel_infos[channel_index]

        mean_rb = RingBuffer(
            channel_info.mean_len, channel_decoder.subchannels)
        self.mean_ringbuffers[channel_index] = mean_rb
        plot_rb = RingBuffer(
            channel_info.plot_len, channel_decoder.subchannels)
        self.plot_ringbuffers[channel_index] = plot_rb
        fft_rb = RingBuffer(
            channel_info.fft_sample_len, channel_decoder.subchannels)
        self.fft_ringbuffers[channel_index] = fft_rb

        downsample = channel_info.downsample_factor != 1

        def callback(_counter, data, samples, subchannels):
            d = numpy.array(data).reshape(samples, subchannels)
            if downsample:
                plot_rb.append(d[-1, :])
            else:
                plot_rb.extend(d)
            fft_rb.extend(d)
            mean_rb.extend(d)

        channel_decoder.set_callback(callback)

        channel_decoder.set_conversion_factor(
            channel_info.unit_formatter.conversion_scale,
            channel_info.unit_formatter.conversion_offset)

    def create_lost_packet_callback(self, stream_id):
        def lost_packet_callback(current, last):
            lost = (current - last - 1) & 0xFFFFFFFFFFFFFFFF

            now = datetime.datetime.utcnow()

            with self.lost_packet_lock:
                self.lost_packet_count += lost
                self.recent_lost_packet_count += lost
                self.lost_packet_last_time = now

            self.lost_packet_deque.append((now, lost))

            for channel_index, channel_info in enumerate(self.channel_infos):
                if channel_info.stream_id == stream_id:
                    fft_ringbuffer = self.fft_ringbuffers[channel_index]
                    if fft_ringbuffer is not None:
                        fft_ringbuffer.clear()

        return lost_packet_callback

    def update_lost_packets(self):
        lost_count_too_old = 0
        now = datetime.datetime.utcnow()
        twenty_secs_ago = now - datetime.timedelta(seconds=20)
        while len(self.lost_packet_deque):
            lost_dt, lost = self.lost_packet_deque[0]
            if lost_dt < twenty_secs_ago:
                lost_count_too_old += lost
                self.lost_packet_deque.popleft()
            else:
                break

        with self.lost_packet_lock:
            self.recent_lost_packet_count -= lost_count_too_old
            if self.recent_lost_packet_count < 0:
                self.recent_lost_packet_count = 0

            # grab local copies
            total = self.lost_packet_count
            recent = self.recent_lost_packet_count
            last_datetime = self.lost_packet_last_time

        update = (CalcData.LOST_PACKET_UPDATE, total, last_datetime, recent)
        if self.last_lost_packet_update != update:
            self.last_lost_packet_update = update
            with self.data_lock:
                self.data_pipe.send(update)

    def get_stream_rate(self, rate_info):
        if rate_info.available:
            rate_channel_index = self.channel_indexes[rate_info.channel_index]
            rate_channel_info = self.channel_infos[rate_channel_index]
            ringbuffer = self.fft_ringbuffers[rate_channel_index]
            if len(ringbuffer) != 0:
                rate_data = ringbuffer.get_contents()
                raw_rate = numpy.average(rate_data)

                # compute channel rate
                stream_rate = raw_rate * rate_info.scale + rate_info.offset
                if rate_info.invert:
                    if stream_rate != 0.0:
                        stream_rate = 1 / stream_rate
                    else:
                        stream_rate = 0.0  # no divide by zero please

                # undo the formatter
                uf = rate_channel_info.unit_formatter
                stream_rate = (stream_rate - uf.conversion_offset) * \
                    uf.conversion_scale

                return stream_rate
            else:
                # no data available to compute rate yet
                return None
        else:
            return None

    def update_channels(self):
        for channel_index, ringbuffer in enumerate(self.mean_ringbuffers):
            if ringbuffer is not None and len(ringbuffer) > 0:
                d = ringbuffer.get_contents()
                mean = numpy.mean(d, axis=0)
                std = numpy.std(d, axis=0)
                self.data_pipe.send((
                    CalcData.CHANNEL_UPDATE, channel_index, mean, std))

    def update_plots(self):
        if not self.is_shown:
            return

        channel_index = self.current_channel_index
        if channel_index is None:
            return

        channel_info = self.channel_infos[channel_index]

        stream_rate = self.get_stream_rate(channel_info.rate_info)
        if not stream_rate:
            channel_rate = channel_info.rate
        else:
            channel_rate = stream_rate * channel_info.samples
        plot_rate = channel_rate / channel_info.downsample_factor

        plot_array = self.plot_ringbuffers[channel_index].get_contents()
        if len(plot_array) > 0:
            length = len(plot_array)
            start = -(length - 1) / plot_rate
            time_axis = numpy.linspace(start, 0, length)
            with self.data_lock:
                self.data_pipe.send((CalcData.PLOT_UPDATE, channel_index,
                                     time_axis, plot_array))

    def update_ffts(self):
        if not self.is_shown:
            return

        channel_index = self.current_channel_index
        if channel_index is None:
            return

        subchannel_index = self.current_subchannel_index
        if subchannel_index is None:
            return

        channel_info = self.channel_infos[channel_index]

        stream_rate = self.get_stream_rate(channel_info.rate_info)
        if not stream_rate:
            fft_freq_axis = channel_info.fft_freq_axis
        else:
            channel_rate = stream_rate * channel_info.samples
            fft_freq_axis = numpy.fft.rfftfreq(channel_info.fft_size,
                                               1 / channel_rate)

        ringbuffer = self.fft_ringbuffers[channel_index]
        fft_array = ringbuffer.get_contents()
        if ringbuffer.maxlen != len(fft_array):
            buffering_progress = len(fft_array) / ringbuffer.maxlen
            with self.data_lock:
                self.data_pipe.send((
                    CalcData.FFT_UPDATE, channel_index, subchannel_index,
                    fft_freq_axis, buffering_progress))
        else:
            fft_array = fft_array[:, subchannel_index].flatten()
            fft_array -= numpy.mean(fft_array)
            fft_size = channel_info.fft_size
            fft_array = fft_array[0:fft_size]
            fft_data = numpy.abs(numpy.fft.rfft(fft_array)) * 2 / fft_size
            with self.data_lock:
                self.data_pipe.send((
                    CalcData.FFT_UPDATE, channel_index, subchannel_index,
                    fft_freq_axis, fft_data))

    def set_is_shown(self, is_shown):
        self.is_shown = is_shown
        if is_shown:
            # update the plots now
            self.update_plots()
            self.update_ffts()

    def plot_change(self, channel_index, subchannel_index):
        if channel_index == -1:
            channel_index = None
        if subchannel_index == -1:
            subchannel_index = None

        self.current_channel_index = channel_index
        self.current_subchannel_index = subchannel_index

    def reset_lost_packets(self):
        self.lost_packet_deque.clear()
        with self.lost_packet_lock:
            self.recent_lost_packet_count = 0

    def unknown_id_cb(self, unknown_id):
        with self.data_lock:
            self.data_pipe.send((CalcData.UNKNOWN_ID, unknown_id))

    def update_thread_run(self):
        update_funcs = [
            (self.update_channels, self.channel_interval),
            (self.update_plots, self.plot_interval),
            (self.update_ffts, self.fft_interval),
            (self.update_lost_packets, self.channel_interval),
        ]
        next_run = [time.monotonic()] * len(update_funcs)

        try:
            while True:
                now = time.monotonic()
                for i, (func, interval) in enumerate(update_funcs):
                    if next_run[i] <= now:
                        func()
                        next_run[i] += interval
                        if next_run[i] <= now:
                            # fell behind, just wait for the interval to pass
                            next_run[i] = now + interval

                wait_time = min(next_run) - time.monotonic()
                if wait_time < 0.0:
                    wait_time = 0.0
                if self.stopped.wait(wait_time):
                    # all done
                    self.logger.debug("Calc process update thread stopped")
                    return
        except Exception:
            self.logger.exception("Unhandled exception in update_thread_run")

    def run(self):
        try:
            self.logger.debug("Calc process started")

            self.update_thread.start()

            me = psutil.Process(os.getpid())
            object_list = [self.packet_pipe, self.ctrl_pipe]
            while me.parent() is not None:
                ready_pipes = multiprocessing.connection.wait(
                    object_list, timeout=0.1)
                for pipe in ready_pipes:
                    if pipe == self.packet_pipe:
                        packet_list = pipe.recv()
                        if not self.stopped.is_set():
                            for packet in packet_list:
                                self.device_decoder.decode(packet)
                    else:
                        ctrl = pipe.recv()
                        if ctrl[0] == CalcControl.STOP:
                            self.stopped.set()
                        elif ctrl[0] == CalcControl.CLOSE:
                            # all done!
                            return
                        elif ctrl[0] == CalcControl.SET_SHOWN:
                            self.set_is_shown(ctrl[1])
                        elif ctrl[0] == CalcControl.PLOT_CHANGE:
                            self.plot_change(*ctrl[1:])
                        elif ctrl[0] == CalcControl.RESET_LOST_PACKETS:
                            self.reset_lost_packets()
        except Exception:
            self.logger.exception("Unhandled exception in calc process run")
        finally:
            self.stopped.set()
            self.update_thread.join()
            self.logger.debug("Calc process exiting")


def run_calc_runner(log_queue, *args, **kwargs):
    # fix a bug with stderr and stdout being None
    sys.stdout = open(os.devnull)
    sys.stderr = open(os.devnull)

    handler = logging.handlers.QueueHandler(log_queue)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    # ctrl+c handling: want to let the main process send the exit command
    if sys.platform == "win32":
        # the best way on windows? since we can't create a new process group
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    else:
        # move to a new process group (won't be signalled with ctrl+c)
        os.setpgrp()

    try:
        calc_runner = CalcRunner(*args, **kwargs)
        calc_runner.run()
    except Exception:
        logger.exception("unhandled exception in run_calc_runner")
    finally:
        log_queue.close()
        log_queue.join_thread()


class CalcProcess(QtCore.QObject):
    # error_str
    status_received = QtCore.Signal(object)

    # channel_index, mean, std
    channel_update = QtCore.Signal(object, object, object)

    # channel_index, time_array, data_array
    plot_update = QtCore.Signal(object, object, object)

    # channel_index, subchannel_id, fft_freqs, fft_data
    # NOTE: data may be a scalar from 0 to 1 showing buffering status
    fft_update = QtCore.Signal(object, object, object, object)

    # total, last_datetime, recent
    lost_packet_update = QtCore.Signal(object, object, object)

    # stream_id
    unknown_id = QtCore.Signal(object)

    def __init__(self, serial, is_shown, device_decoder, channel_infos,
                 channel_indexes, channel_interval, plot_interval,
                 fft_interval):
        super().__init__()

        self.log_queue = multiprocessing.Queue()
        local_handler = RemoteToLocalLogHandler(__name__ + ".remote")
        self.log_listener = logging.handlers.QueueListener(
            self.log_queue, local_handler)
        self.log_listener.start()

        self.logger = DeviceLoggerAdapter(logger, serial)

        self.stopped = threading.Event()
        self.finished = threading.Event()

        # for the StreamManager communication
        self.status_rx_pipe, self.status_tx_pipe = multiprocessing.Pipe(False)
        self.packet_rx_pipe, self.packet_tx_pipe = multiprocessing.Pipe(False)

        # for the CalcRunner communication
        self.data_rx_pipe, self.data_tx_pipe = multiprocessing.Pipe(False)
        self.ctrl_rx_pipe, self.ctrl_tx_pipe = multiprocessing.Pipe(False)

        self.status_thread = threading.Thread(target=self.status_thread_run)
        self.status_thread.start()

        self.data_thread = threading.Thread(target=self.data_thread_run)
        self.data_thread.start()

        self.remote_process = NamedProcess(
            name="acheron-calc", description=serial, target=run_calc_runner,
            args=(self.log_queue, self.packet_rx_pipe, self.data_tx_pipe,
                  self.ctrl_rx_pipe, serial, is_shown, device_decoder,
                  channel_infos, channel_indexes, channel_interval,
                  plot_interval, fft_interval))
        self.remote_process.daemon = True
        self.remote_process.start()

    def stop(self):
        self.stopped.set()
        self.ctrl_tx_pipe.send((CalcControl.STOP,))

        self.logger.debug("Calc process stopping")

    def join(self):
        if not self.stopped.is_set():
            self.stop()

        self.ctrl_tx_pipe.send((CalcControl.CLOSE,))
        self.finished.set()

        self.remote_process.join()
        self.status_thread.join()
        self.data_thread.join()

        self.log_listener.stop()

        self.status_rx_pipe.close()
        self.status_tx_pipe.close()
        self.packet_rx_pipe.close()
        self.packet_tx_pipe.close()
        self.data_rx_pipe.close()
        self.data_tx_pipe.close()
        self.ctrl_rx_pipe.close()
        self.ctrl_tx_pipe.close()

        self.logger.debug("Calc process closed")

    def get_pipes(self):
        return self.packet_tx_pipe, self.status_tx_pipe

    def status_thread_run(self):
        pipe = self.status_rx_pipe
        while True:
            if self.finished.is_set():
                break

            if pipe.poll(0.1):  # 100 ms
                try:
                    status = pipe.recv()
                except EOFError:
                    break

                self.status_received.emit(status)

    def data_thread_run(self):
        pipe = self.data_rx_pipe
        while True:
            if self.finished.is_set():
                break

            if pipe.poll(0.1):  # 100 ms
                try:
                    data = pipe.recv()
                except EOFError:
                    break

                self.handle_data(data)

    def handle_data(self, data):
        if self.stopped.is_set():
            return

        if data[0] == CalcData.CHANNEL_UPDATE:
            self.channel_update.emit(*data[1:])
        elif data[0] == CalcData.PLOT_UPDATE:
            self.plot_update.emit(*data[1:])
        elif data[0] == CalcData.FFT_UPDATE:
            self.fft_update.emit(*data[1:])
        elif data[0] == CalcData.LOST_PACKET_UPDATE:
            self.lost_packet_update.emit(*data[1:])
        elif data[0] == CalcData.UNKNOWN_ID:
            self.unknown_id.emit(*data[1:])

    def set_is_shown(self, is_shown):
        self.ctrl_tx_pipe.send((CalcControl.SET_SHOWN, is_shown))

    def plot_change(self, channel_index, subchannel_index):
        self.ctrl_tx_pipe.send(
            (CalcControl.PLOT_CHANGE, channel_index, subchannel_index))

    def reset_lost_packets(self):
        self.ctrl_tx_pipe.send((CalcControl.RESET_LOST_PACKETS,))
