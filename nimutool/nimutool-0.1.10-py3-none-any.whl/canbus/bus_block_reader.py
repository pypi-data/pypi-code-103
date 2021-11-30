from nimutool.canbus.bus_synchronizer import BusSynchronizer
from nimutool.parser import PARSERS
from nimutool.data.writer import CsvWriter
from tqdm import tqdm
import threading
from pathlib import Path


class BusBlockReader:

    def __init__(self, input, processor, outputs, traffic_study_period=0.5, show_progress=True):
        self.input = input
        self.synchronizer = BusSynchronizer(traffic_study_period, processor, True)
        self.outputs = outputs
        self.show_progress = show_progress

    def _process_message(self, msg):
        processed_block = self.synchronizer.synchronize(msg)
        if processed_block:
            if processed_block.reception_window_us < 0:
                print(processed_block)
            for output in self.outputs:
                output.write(processed_block)

    def process(self):
        if self.show_progress:
            for msg in tqdm(self.input, desc='Receiving messages', unit='msg'):
                self._process_message(msg)
        else:
            for msg in self.input:
                self._process_message(msg)


class ThreadedNimuAndPI48ReaderWriter(threading.Thread):

    def __init__(self, bus, path: Path, file_prefix: str, extras=True, nimu_protocol=2, traffic_study_period=0.5,):
        super().__init__()
        self.running = True
        self.nifile = Path(path) / Path(f'{file_prefix}_ni_data.csv')
        self.pifile = Path(path) / Path(f'{file_prefix}_pi_data.csv')
        self.bus = bus
        niprocessor = PARSERS['nimu']()
        piprocessor = PARSERS['pi48']()
        self.nisynchronizer = BusSynchronizer(traffic_study_period, niprocessor, True)
        self.pisynchronizer = BusSynchronizer(traffic_study_period, piprocessor, True)
        self.next_trace = 0
        self.extras = extras

    def run(self):
        niwriter = CsvWriter(self.nifile)
        piwriter = CsvWriter(self.pifile)
        for msg in self.bus:
            if not self.running:
                break
            block = self.nisynchronizer.synchronize(msg)
            if block:
                niwriter.write(block)
            block = self.pisynchronizer.synchronize(msg)
            if block:
                piwriter.write(block)

            if self.next_trace < msg.timestamp:
                print(f'NI: {self.nisynchronizer} PI: {self.pisynchronizer}')
                self.next_trace = msg.timestamp + 5
                # if self.extras and block:
                #    ConsoleWriter().write(block)
        if self.nisynchronizer.collection_monitor.count != 0:
            print(f'Written {self.nisynchronizer.collection_monitor.count} rows to {self.nifile}')
        if self.pisynchronizer.collection_monitor.count != 0:
            print(f'Written {self.pisynchronizer.collection_monitor.count} rows to {self.pifile}')

    def stop(self):
        self.running = False
        self.join()
        if self.bus:
            self.bus.stop()
