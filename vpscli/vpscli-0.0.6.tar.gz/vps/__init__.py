#!/usr/local/env python3
from .configer import EndlessConfig, SystemConfig
from .installer import CoreAppInstaller, StatAppInstaller
from .piper import PiperContext


def main():
    exec_classes = [
        CoreAppInstaller, StatAppInstaller, SystemConfig, EndlessConfig,
        PiperContext
    ]
    for ec in exec_classes:
        ec().run()


if __name__ == '__main__':
    main()
