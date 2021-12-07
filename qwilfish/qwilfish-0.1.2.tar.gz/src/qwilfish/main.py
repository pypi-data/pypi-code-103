# Standard library imports
import argparse

# Local imports
from qwilfish.qwilfuzzer import QwilFuzzer
from qwilfish.constants import SIMPLE_GRAMMAR_EXAMPLE
from qwilfish.ethernet_frame import ETHERNET_FRAME_GRAMMAR
from qwilfish.linux_socket_runner import LinuxSocketRunner

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-l", "--log",
                        dest="log",
                        help="Turn on logging",
                        action="store_true")

    parser.add_argument("-i", "--interface",
                        dest="interface",
                        help="Network interface to transmit fuzzed packets on",
                        default="lo")

    parser.add_argument("-c", "--count",
                        dest="count",
                        help="Number of fuzzed packets to transmit",
                        type=int,
                        default=1)


    args = parser.parse_args()

    grammar = ETHERNET_FRAME_GRAMMAR
    runner = LinuxSocketRunner(interface=args.interface)
    qf = QwilFuzzer(grammar, log=args.log)
    for i in range(0, args.count):
        qf.run(runner=runner)
