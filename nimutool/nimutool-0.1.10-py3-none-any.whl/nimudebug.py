import argparse
import nimutool.parser
import nimutool.canbus
import can


class NimuDebugDefaultArguments:

    file_format: str = 'n/a'
    input_file: str = 'n/a'
    can_adapter: str = 'pcan'
    can_channel: str = 'PCAN_USBBUS1'


class DebugWriter:

    def __init__(self):
        self.line = {}

    def write(self, processed_block: nimutool.canbus.ProcessedCanDataBlock):
        for msg in processed_block.get_messages():
            if msg.nodeid not in self.line:
                self.line[msg.nodeid] = ''
            self.line[msg.nodeid] += msg.data[0]
            lines = self.line[msg.nodeid].split('\n')
            if len(lines) > 1:
                print(f'{msg.nodeid}: {lines[0]}')
                self.line[msg.nodeid] = '\n'.join(lines[1:])


class NimuDebug:

    def __init__(self, arguments: NimuDebugDefaultArguments = None):
        args = arguments if arguments else self.parse_arguments()
        if args.file_format:
            self.bus = nimutool.canbus.READERS[args.file_format](args.input_file)
        else:
            self.bus = nimutool.canbus.CanBusReader(can.interface.Bus(bustype=args.can_adapter, channel=args.can_channel, bitrate=1000000))
        self.run()

    def run(self):
        processor = nimutool.parser.PARSERS['nimudebug']()
        writer = DebugWriter()
        block_processor = nimutool.canbus.BusBlockReader(input=self.bus, processor=processor, outputs=[writer], traffic_study_period=1, show_progress=False)
        block_processor.process()

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Tool for reading nimu data from CAN bus')
        parser.add_argument('--file-format', choices=nimutool.canbus.READERS.keys(), type=str, help='Parse raw can message CSV file')
        parser.add_argument('--input-file', type=str, help='Parse can messages from input file, determine parser with --file-parser argument')
        parser.add_argument('--can-adapter', default='pcan', help='Can adapter to use, see options from python-can documentation')
        parser.add_argument('--can-channel', default='PCAN_USBBUS1', help='Can adapter channel to use, see options from python-can documentation')
        return parser.parse_args()


if __name__ == '__main__':
    NimuDebug()
