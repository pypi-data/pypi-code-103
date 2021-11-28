import logging
import sys
from text_analyzer.launcher import Launcher

if __name__ == "__main__":
    logging.basicConfig(filename="./textanalyzer.log", filemode="a", format="%(asctime)s|%(message)s|%(levelname)s",
                        datefmt="%d-%b-%y %H:%M:%S", level=logging.NOTSET)
    launcher = Launcher(sys.argv)
    launcher.launch()
