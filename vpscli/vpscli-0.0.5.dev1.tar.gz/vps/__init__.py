#!/usr/local/env python3
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass

import codefast as cf

SUPVISOR_CONF_TEMPLATE = '''
[program:PLACEHOLDER]
directory=/tmp/
command=COMMAND
user=root
autostart=true
autorestart=true
redirect_stderr=true
stopasgroup=true
killasgroup=true'''


class Symbols:
    smiley = '😀'
    sad = '😞'
    question = '❓'
    info = 'ℹ️'
    warning = '⚠️'
    error = '🚫'
    success = '✅'
    fail = '❌'
    ok = '✅'
    turtule = '🐢'
    mokey = '🐵'


@dataclass
class Cmd:
    pre_msg: str = ''
    command: str = ''
    post_msg: str = ''


class BashRunner:
    @staticmethod
    def get_output(command: str) -> str:
        return subprocess.check_output(command,
                                       shell=True).decode('utf-8').strip()

    @staticmethod
    def call(command: str) -> int:
        '''return 0 if no error occurs'''
        return subprocess.call(command, shell=True)

    @staticmethod
    def call_with_msg(cmd_obj: Cmd) -> None:
        cf.info(cmd_obj.pre_msg)
        resp = BashRunner.call(cmd_obj.command)
        if resp == 0:
            cf.info(cmd_obj.post_msg + ' ' + Symbols.success)
        else:
            raise Exception(f'{cmd_obj.post_msg} failed')

    @staticmethod
    def get_app_path(app_name: str) -> str:
        resp = BashRunner.get_output('which {}'.format(app_name))
        if resp and resp.endswith(app_name):
            return resp
        return '/usr/local/bin/{}'.format(app_name)

    @staticmethod
    def check_if_app_installed(app_name: str) -> bool:
        resp = BashRunner.get_output('apt-cache policy {}'.format(app_name))
        return 'Installed: (none)' not in resp


class Installer:
    '''App installer'''
    core_apps = [
        'tree', 'p7zip-full', 'python3-pip', 'emacs', 'ufw', 'curl', 'wget',
        'unzip', 'aria2', 'shadowsocks-libev', 'ncdu', 'git', 'supervisor',
        'graphviz'
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


class StatAppInstaller(Installer):
    def run(self):
        for app in self.stat_apps:
            if not BashRunner.check_if_app_installed(app):
                cmd = Cmd(pre_msg=f'Installing {app}',
                          command=f'apt -y install {app}',
                          post_msg=f'【{app}】 installed\n' + '-' * 80)
                BashRunner.call_with_msg(cmd)


class SupervisorConfig(ABC):
    def run(self):
        cf.info('update {} supervisor config file'.format(self.app_name))
        cf.io.write(self.conf, self.conf_path)
        cf.info('restart supervisor')
        BashRunner.call(f'supervisorctl update')


class EndlessConfig(SupervisorConfig):
    def __init__(self):
        self.app_name = 'endlessh'
        self.command = BashRunner.get_app_path('endlessh') + ' -p 22'
        self.conf = SUPVISOR_CONF_TEMPLATE.replace('PLACEHOLDER',
                                                   self.app_name)
        self.conf = self.conf.replace('COMMAND', self.command)
        self.conf_path = '/etc/supervisor/conf.d/endlessh.conf'


class SystemConfig:
    cmds = ['timedatectl set-timezone Asia/Shanghai']

    def run(self):
        for cmd in self.cmds:
            str_cmd = Cmd(f'Running {cmd}', cmd, f'{cmd} finished')
            BashRunner.call_with_msg(str_cmd)


class Executor:
    @classmethod
    def run(cls):
        CoreAppInstaller().run()
        StatAppInstaller().run()
        SystemConfig().run()
        EndlessConfig().run()


def main():
    Executor.run()


if __name__ == '__main__':
    main()
