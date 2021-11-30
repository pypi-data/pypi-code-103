#!/usr/bin/env python3


# SAT: a jabber client
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

"""tools to launch process in a async way (using Twisted)"""

import os.path
from twisted.internet import defer, reactor, protocol
from twisted.python.failure import Failure
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.log import getLogger
log = getLogger(__name__)


class CommandProtocol(protocol.ProcessProtocol):
    """handle an external command"""
    # name of the command (unicode)
    name = None
    # full path to the command (bytes)
    command = None
    # True to activate logging of command outputs (bool)
    log = False

    def __init__(self, deferred, stdin=None):
        """
        @param deferred(defer.Deferred): will be called when command is completed
        @param stdin(str, None): if not None, will be push to standard input
        """
        self._stdin = stdin
        self._deferred = deferred
        self.data = []
        self.err_data = []

    @property
    def command_name(self):
        """returns command name or empty string if it can't be guessed"""
        if self.name is not None:
            return self.name
        elif self.command is not None:
            return os.path.splitext(os.path.basename(self.command))[0].decode('utf-8',
                                                                              'ignore')
        else:
            return ''

    def connectionMade(self):
        if self._stdin is not None:
            self.transport.write(self._stdin)
            self.transport.closeStdin()

    def outReceived(self, data):
        if self.log:
            log.info(data.decode('utf-8', 'replace'))
        self.data.append(data)

    def errReceived(self, data):
        if self.log:
            log.warning(data.decode('utf-8', 'replace'))
        self.err_data.append(data)

    def processEnded(self, reason):
        data = b''.join(self.data)
        if (reason.value.exitCode == 0):
            log.debug(f'{self.command_name!r} command succeed')
            # we don't use "replace" on purpose, we want an exception if decoding
            # is not working properly
            self._deferred.callback(data)
        else:
            err_data = b''.join(self.err_data)

            msg = (_("Can't complete {name} command (error code: {code}):\n"
                     "stderr:\n{stderr}\n{stdout}\n")
                   .format(name = self.command_name,
                           code = reason.value.exitCode,
                           stderr= err_data.decode(errors='replace'),
                           stdout = "stdout: " + data.decode(errors='replace')
                                    if data else '',
                           ))
            self._deferred.errback(Failure(exceptions.CommandException(
                msg, data, err_data)))

    @classmethod
    def run(cls, *args, **kwargs):
        """Create a new CommandProtocol and execute the given command.

        @param *args(unicode): command arguments
            if cls.command is specified, it will be the path to the command to execute
            otherwise, first argument must be the path
        @param **kwargs: can be:
            - stdin(unicode, None): data to push to standard input
            - verbose(bool): if True stdout and stderr will be logged
            other keyword arguments will be used in reactor.spawnProcess
        @return ((D)bytes): stdout in case of success
        @raise RuntimeError: command returned a non zero status
            stdin and stdout will be given as arguments

        """
        stdin = kwargs.pop('stdin', None)
        if stdin is not None:
            stdin = stdin.encode('utf-8')
        verbose = kwargs.pop('verbose', False)
        args = list(args)
        d = defer.Deferred()
        prot = cls(d, stdin=stdin)
        if verbose:
            prot.log = True
        if cls.command is None:
            if not args:
                raise ValueError(
                    "You must either specify cls.command or use a full path to command "
                    "to execute as first argument")
            command = args.pop(0)
            if prot.name is None:
                name = os.path.splitext(os.path.basename(command))[0]
                prot.name = name
        else:
            command = cls.command
        cmd_args = [command] + args
        if "env" not in kwargs:
            # we pass parent environment by default
            kwargs["env"] = None
        reactor.spawnProcess(prot,
                             command,
                             cmd_args,
                             **kwargs)
        return d


run = CommandProtocol.run
