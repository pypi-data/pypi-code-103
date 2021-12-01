from qwilfish.qwilfuzzer import QwilFuzzer
from qwilfish.constants import SIMPLE_GRAMMAR_EXAMPLE
from qwilfish.ethernet_frame import ETHERNET_FRAME_GRAMMAR
from qwilfish.linux_socket_runner import LinuxSocketRunner

def main():
    grammar = ETHERNET_FRAME_GRAMMAR
    qf = QwilFuzzer(grammar, log=True)
    qf.run(runner=LinuxSocketRunner())
