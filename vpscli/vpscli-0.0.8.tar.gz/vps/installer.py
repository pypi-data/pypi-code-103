#!/usr/local/env python3
from abc import ABC, abstractmethod

import codefast as cf

from .osi import BashRunner, Cmd


class Installer(ABC):
    '''App installer'''
    core_apps = [
        'tree', 'p7zip-full', 'python3-pip', 'emacs', 'ufw', 'curl', 'wget',
        'unzip', 'aria2', 'shadowsocks-libev', 'ncdu', 'git', 'supervisor',
        'graphviz', 'qbittorrent-nox'
    ]
    stat_apps = [
        'vnstat', 'iftop', 'bmon', 'tcptrack', 'slurm', 'sysstat', 'bc', 'pv',
        'neofetch', 'jq', 'htop', 'vnstat', 'ffmpeg', 'nload', 'ncdu'
    ]

    @abstractmethod
    def run(self):
        pass


class CoreAppInstaller(Installer):
    def run(self):
        for app in self.core_apps:
            if not BashRunner.check_if_app_installed(app):
                cmd = Cmd(pre_msg=f'Installing {app}',
                          command=f'apt -y install {app}',
                          post_msg=f'【{app}】 installed\n' + '-' * 80)
                BashRunner.call_with_msg(cmd)
            else:
                cf.info(f'{app} already installed')


class StatAppInstaller(Installer):
    def run(self):
        for app in self.stat_apps:
            if not BashRunner.check_if_app_installed(app):
                cmd = Cmd(pre_msg=f'Installing {app}',
                          command=f'apt -y install {app}',
                          post_msg=f'【{app}】 installed\n' + '-' * 80)
                BashRunner.call_with_msg(cmd)
            else:
                cf.info(f'{app} already installed')


class AutoRemove:
    def run(self):
        BashRunner.call('apt -y autoremove')
        cf.info('Auto removed')
