from nimutool.canbus.can_message import ProcessedCanDataBlock
from nimutool.data.conversion import calculate_rpy_if_possible

SEP = ';'


def formatter_csv(elems):
    return SEP.join(arg.strip() for arg in elems)


def formatter_console(elems):
    return ' '.join(elems)


class CsvWriter:

    def __init__(self, filename, write_every_nth=1):
        self.f = open(filename, "w")
        self.write_every_nth = write_every_nth
        self.cnt = 0
        self.header_written = False

    def __del__(self):
        self.f.close()

    def _add_header_if_needed(self, processed_block: ProcessedCanDataBlock):
        if self.header_written:
            return
        hdr = ['timestamp', 'window_us']
        for msg in processed_block.get_messages():
            hdr += [(signal + str(msg.nodeid) if msg.nodeid else signal) for signal in msg.signals]
        self.f.write(formatter_csv(hdr) + '\n')
        self.header_written = True

    def write(self, processed_block: ProcessedCanDataBlock):
        self.cnt += 1
        if self.cnt % self.write_every_nth != 0:
            return
        # calculate_rpy_if_possible(processed_block)
        self._add_header_if_needed(processed_block)
        formatted_data_items = [f'{processed_block.timestamp:.6f}', str(processed_block.reception_window_us)]
        for msg in processed_block.get_messages():
            formatted_data_items += [data for data in msg.formatted_data]
        self.f.write(formatter_csv(formatted_data_items) + '\n')


class ConsoleWriter:

    def __init__(self, column_names=None):
        self.columns_filter = column_names

    def is_filtered(self, msg):
        return any([signal in self.columns_filter for signal in msg.signals])

    def write(self, processed_block: ProcessedCanDataBlock):
        calculate_rpy_if_possible(processed_block)
        formatted_timing = [str(processed_block.timestamp), str(processed_block.reception_window_us)]
        formatted_data_items = []
        for msg in processed_block.get_messages():
            if self.is_filtered(msg):
                formatted_data_items += [data for data in msg.formatted_data]
        if len(formatted_data_items):
            print(formatter_console(formatted_timing + formatted_data_items))
