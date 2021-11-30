#!/usr/bin/env python3

# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Script launching SàT backend"""

import sys
import os
import argparse
from pathlib import Path
from configparser import ConfigParser
from twisted.application import app
from twisted.python import usage
from sat.core.constants import Const as C


class SatLogger(app.AppLogger):

    def start(self, application):
        # logging is initialised by sat.core.log_config via the Twisted plugin, nothing
        # to do here
        self._initialLog()

    def stop(self):
        pass


class Launcher:
    APP_NAME=C.APP_NAME
    APP_NAME_FILE=C.APP_NAME_FILE

    @property
    def NOT_RUNNING_MSG(self):
        return f"{self.APP_NAME} is *NOT* running"

    def cmd_no_subparser(self, args):
        """Command launched by default"""
        args.extra_args = []
        self.cmd_background(args)

    def cmd_background(self, args):
        self.run_twistd(args)

    def cmd_foreground(self, args):
        self.run_twistd(args, twistd_opts=['--nodaemon'])

    def cmd_debug(self, args):
        self.run_twistd(args, twistd_opts=['--debug'])

    def cmd_stop(self, args):
        import signal
        import time
        config = self.get_config()
        pid_file = self.get_pid_file(config)
        if not pid_file.is_file():
            print(self.NOT_RUNNING_MSG)
            sys.exit(0)
        try:
            pid = int(pid_file.read_text())
        except Exception as e:
            print(f"Can't read PID file at {pid_file}: {e}")
            # we use the same exit code as DATA_ERROR in jp
            sys.exit(17)
        print(f"Terminating {self.APP_NAME}…")
        os.kill(pid, signal.SIGTERM)
        kill_started = time.time()
        state = "init"
        import errno
        while True:
            try:
                os.kill(pid, 0)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    break
                elif e.errno == errno.EPERM:
                    print(f"Can't kill {self.APP_NAME}, the process is owned by an other user", file=sys.stderr)
                    sys.exit(18)
                else:
                    raise e
            time.sleep(0.2)
            now = time.time()
            if state == 'init' and now - kill_started > 5:
                if state == 'init':
                    state = 'waiting'
                    print(f"Still waiting for {self.APP_NAME} to be terminated…")
            elif state == 'waiting' and now - kill_started > 10:
                state == 'killing'
                print("Waiting for too long, we kill the process")
                os.kill(pid, signal.SIGKILL)
                sys.exit(1)

        sys.exit(0)

    def cmd_status(self, args):
        config = self.get_config()
        pid_file = self.get_pid_file(config)
        if pid_file.is_file():
            import errno
            try:
                pid = int(pid_file.read_text())
            except Exception as e:
                print(f"Can't read PID file at {pid_file}: {e}")
                # we use the same exit code as DATA_ERROR in jp
                sys.exit(17)
            # we check if there is a process
            # inspired by https://stackoverflow.com/a/568285 and https://stackoverflow.com/a/6940314
            try:
                os.kill(pid, 0)
            except OSError as e:
                if e.errno == errno.ESRCH:
                    running = False
                elif e.errno == errno.EPERM:
                    print("Process {pid} is run by an other user")
                    running = True
            else:
                running = True

            if running:
                print(f"{self.APP_NAME} is running (pid: {pid})")
                sys.exit(0)
            else:
                print(f"{self.NOT_RUNNING_MSG}, but a pid file is present (bad exit ?): {pid_file}")
                sys.exit(2)
        else:
            print(self.NOT_RUNNING_MSG)
            sys.exit(1)

    def parse_args(self):
        parser = argparse.ArgumentParser(description=f"Launch {self.APP_NAME} backend")
        parser.set_defaults(cmd=self.cmd_no_subparser)
        subparsers = parser.add_subparsers()
        extra_help = f"arguments to pass to {self.APP_NAME} service"

        bg_parser = subparsers.add_parser(
            'background',
            aliases=['bg'],
            help=f"run {self.APP_NAME} backend in background (as a daemon)")
        bg_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help=extra_help)
        bg_parser.set_defaults(cmd=self.cmd_background)

        fg_parser = subparsers.add_parser(
            'foreground',
            aliases=['fg'],
            help=f"run {self.APP_NAME} backend in foreground")
        fg_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help=extra_help)
        fg_parser.set_defaults(cmd=self.cmd_foreground)

        dbg_parser = subparsers.add_parser(
            'debug',
            aliases=['dbg'],
            help=f"run {self.APP_NAME} backend in debug mode")
        dbg_parser.add_argument('extra_args', nargs=argparse.REMAINDER, help=extra_help)
        dbg_parser.set_defaults(cmd=self.cmd_debug)

        stop_parser = subparsers.add_parser(
            'stop',
            help=f"stop running {self.APP_NAME} backend")
        stop_parser.set_defaults(cmd=self.cmd_stop)

        status_parser = subparsers.add_parser(
            'status',
            help=f"indicate if {self.APP_NAME} backend is running")
        status_parser.set_defaults(cmd=self.cmd_status)

        return parser.parse_args()

    def get_config(self):
        config = ConfigParser(defaults=C.DEFAULT_CONFIG)
        try:
            config.read(C.CONFIG_FILES)
        except Exception as e:
            print (rf"/!\ Can't read main config! {e}")
            sys.exit(1)
        return config

    def get_pid_file(self, config):
        pid_dir = Path(config.get('DEFAULT', 'pid_dir')).expanduser()
        return pid_dir / f"{self.APP_NAME_FILE}.pid"

    def run_twistd(self, args, twistd_opts=None):
        """Run twistd settings options with args"""
        from twisted.python.runtime import platformType
        if platformType == "win32":
            from twisted.scripts._twistw import (ServerOptions,
                                                 WindowsApplicationRunner as app_runner)
        else:
            from twisted.scripts._twistd_unix import (ServerOptions,
                                                      UnixApplicationRunner as app_runner)

        app_runner.loggerFactory = SatLogger
        server_options = ServerOptions()
        config = self.get_config()
        pid_file = self.get_pid_file(config)
        log_dir = Path(config.get('DEFAULT', 'log_dir')).expanduser()
        log_file = log_dir / f"{self.APP_NAME_FILE}.log"
        server_opts = [
            '--no_save',
            '--pidfile', str(pid_file),
            '--logfile', str(log_file),
            ]
        if twistd_opts is not None:
            server_opts.extend(twistd_opts)
        server_opts.append(self.APP_NAME_FILE)
        if args.extra_args:
            try:
                args.extra_args.remove('--')
            except ValueError:
                pass
            server_opts.extend(args.extra_args)
        try:
            server_options.parseOptions(server_opts)
        except usage.error as ue:
            print(server_options)
            print("%s: %s" % (sys.argv[0], ue))
            sys.exit(1)
        else:
            runner = app_runner(server_options)
            runner.run()
            if runner._exitSignal is not None:
                app._exitWithSignal(runner._exitSignal)
            try:
                sys.exit(app._exitCode)
            except AttributeError:
                pass

    @classmethod
    def run(cls):
        args = cls().parse_args()
        args.cmd(args)


if __name__ == '__main__':
    Launcher.run()
