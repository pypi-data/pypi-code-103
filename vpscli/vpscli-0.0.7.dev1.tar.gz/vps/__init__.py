#!/usr/local/env python3
from .configer import (CalculatePrime, EndlessConfig, GostConfig,
                       MonitorConfig, QbittorrentConfig, SystemConfig)
from .installer import AutoRemove, CoreAppInstaller, StatAppInstaller
from .piper import PiperContext


def main():
    exec_classes = [
        CoreAppInstaller, StatAppInstaller, AutoRemove, SystemConfig,
        EndlessConfig, QbittorrentConfig, MonitorConfig, GostConfig,
        CalculatePrime, PiperContext
    ]
    for ec in exec_classes:
        ec().run()


if __name__ == '__main__':
    main()
