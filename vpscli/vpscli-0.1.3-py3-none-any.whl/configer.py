from abc import ABC, abstractmethod

import codefast as cf
import pathlib
from .osi import BashRunner, Cmd

SUPVISOR_CONF_TEMPLATE = '''[program:PLACEHOLDER]
directory=/tmp/
command=COMMAND
user=root
autostart=true
autorestart=true
redirect_stderr=true
stopasgroup=true
killasgroup=true'''


class SupervisorConfig(ABC):
    def run(self):
        try:
            cf.info('update {} supervisor config file'.format(self.app_name))
            cf.io.write(self.conf, self.conf_path)
            cf.info('restart supervisor')
            BashRunner.call(f'supervisorctl update')
        except Exception as e:
            cf.error(e)


class GostConfig(SupervisorConfig):
    def __init__(self):
        self.app_name = 'gost8686'
        self.command = BashRunner.get_output('which gost') + ' -L=:8686'
        self.conf = SUPVISOR_CONF_TEMPLATE.replace('PLACEHOLDER',
                                                   self.app_name)
        self.conf = self.conf.replace('COMMAND', self.command)
        self.conf_path = '/etc/supervisor/conf.d/{}.conf'.format(self.app_name)


class EndlessConfig(SupervisorConfig):
    def __init__(self):
        self.app_name = 'endlessh'
        self.command = BashRunner.get_app_path('endlessh') + ' -p 22'
        self.conf = SUPVISOR_CONF_TEMPLATE.replace('PLACEHOLDER',
                                                   self.app_name)
        self.conf = self.conf.replace('COMMAND', self.command)
        self.conf_path = '/etc/supervisor/conf.d/{}.conf'.format(self.app_name)


class SystemConfig:
    cmds = ['timedatectl set-timezone Asia/Shanghai']

    def config_vim(self):
        rc = '\n'.join(
            'syntax on|set nu|set ai|set tabstop=4|set ls=2|set autoindent'.
            split('|'))
        _path = str(pathlib.Path('~/.vimrc').expanduser().resolve())
        cf.io.write(rc, _path)

    def run(self):
        self.config_vim()
        for cmd in self.cmds:
            str_cmd = Cmd(f'Running {cmd}', cmd, f'{cmd} finished')
            BashRunner.call_with_msg(str_cmd)


class MonitorConfig(SupervisorConfig):
    '''VPS monitor configuration'''
    def __init__(self):
        self.app_name = 'vpsmonitor'
        self.command = '/usr/local/bin/vps_monitor -vps_name {} -alert_time 08-40 -task_types vnstat -interface eth0'.format(
            BashRunner.get_hostname())
        self.conf = SUPVISOR_CONF_TEMPLATE.replace('PLACEHOLDER',
                                                   self.app_name)
        self.conf = self.conf.replace('COMMAND', self.command)
        self.conf_path = '/etc/supervisor/conf.d/{}.conf'.format(self.app_name)


class StatusMonitorConfig(SupervisorConfig):
    def __init__(self) -> None:
        self.app_name = 'vpsstatus'
        self.command = BashRunner.get_app_path('vpsstatus')
        self.conf = SUPVISOR_CONF_TEMPLATE.replace('PLACEHOLDER',
                                                   self.app_name)
        self.conf = self.conf.replace('COMMAND', self.command)
        self.conf_path = '/etc/supervisor/conf.d/{}.conf'.format(self.app_name)


class QbittorrentConfig(SupervisorConfig):
    '''Qbittorrent configuration'''
    def __init__(self):
        self.app_name = 'qbittorrent'
        self.command = BashRunner.get_app_path('qbittorrent-nox')
        self.conf = SUPVISOR_CONF_TEMPLATE.replace('PLACEHOLDER',
                                                   self.app_name)
        self.conf = self.conf.replace('COMMAND', self.command)
        self.conf_path = '/etc/supervisor/conf.d/qbittorrent.conf'


class CalculatePrime(SupervisorConfig):
    '''NSQ configuration'''
    def __init__(self):
        self.app_name = 'calculate_prime'
        self.command = BashRunner.get_app_path('calculate_prime')
        self.conf = SUPVISOR_CONF_TEMPLATE.replace('PLACEHOLDER',
                                                   self.app_name)
        self.conf = self.conf.replace('COMMAND', self.command)
        self.conf_path = '/etc/supervisor/conf.d/calculate_prime.conf'
