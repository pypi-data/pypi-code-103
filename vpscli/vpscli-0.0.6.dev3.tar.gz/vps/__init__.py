#!/usr/local/env python3
from .configer import EndlessConfig, MonitorConfig, SystemConfig,QbittorrentConfig
from .installer import AutoRemove, CoreAppInstaller, StatAppInstaller
from .piper import PiperContext


def main():
    exec_classes = [
        CoreAppInstaller, StatAppInstaller, AutoRemove, SystemConfig,
        EndlessConfig, QbittorrentConfig, MonitorConfig, PiperContext
    ]
    for ec in exec_classes:
        ec().run()


if __name__ == '__main__':
    main()
