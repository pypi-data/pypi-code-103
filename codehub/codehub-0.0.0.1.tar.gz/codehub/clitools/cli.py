import os
os.environ['ANSI_COLORS_DISABLED']="1"
import shutil
import fire

class CLI:
    def hi(cls):
        print('Hi, welcome to use codehub !'.center(50, '*'))


def main():
    fire.Fire(CLI())

if __name__ == '__main__':
    main()