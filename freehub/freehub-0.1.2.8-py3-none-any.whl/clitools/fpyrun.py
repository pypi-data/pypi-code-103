from freehub import apis
import os

os.environ['ANSI_COLORS_DISABLED'] = "1"
import shutil
import fire
from freehub.clitools.cli import Cli


def fpyrun(address: str, *args, **kwargs):
    return Cli.pyrun(address, *args, **kwargs)


def main():
    fire.Fire(fpyrun)


if __name__ == '__main__':
    main()
