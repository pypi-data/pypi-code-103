#!/usr/bin/env python3

# jp: a SAT command line tool
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

import sys
import asyncio
import logging as log
from sat.core.i18n import _
from sat_frontends.jp.constants import Const as C

log.basicConfig(level=log.WARNING,
                format='[%(name)s] %(message)s')

USER_INTER_MSG = _("User interruption: good bye")


class QuitException(BaseException):
    """Quitting is requested

    This is used to stop execution when host.quit() is called
    """


def getJPLoop(bridge_name):
    if 'dbus' in bridge_name:
        import signal
        import threading
        from gi.repository import GLib

        class JPLoop:

            def run(self, jp, args, namespace):
                signal.signal(signal.SIGINT, self._on_sigint)
                self._glib_loop = GLib.MainLoop()
                threading.Thread(target=self._glib_loop.run).start()
                loop = asyncio.get_event_loop()
                loop.run_until_complete(jp.main(args=args, namespace=namespace))
                loop.run_forever()

            def quit(self, exit_code):
                loop = asyncio.get_event_loop()
                loop.stop()
                self._glib_loop.quit()
                sys.exit(exit_code)

            def call_later(self, delay, callback, *args):
                """call a callback repeatedly

                @param delay(int): delay between calls in s
                @param callback(callable): method to call
                    if the callback return True, the call will continue
                    else the calls will stop
                @param *args: args of the callbac
                """
                loop = asyncio.get_event_loop()
                loop.call_later(delay, callback, *args)

            def _on_sigint(self, sig_number, stack_frame):
                """Called on keyboard interruption

                Print user interruption message, set exit code and stop reactor
                """
                print("\r" + USER_INTER_MSG)
                self.quit(C.EXIT_USER_CANCELLED)
    else:
        import signal
        from twisted.internet import asyncioreactor
        asyncioreactor.install()
        from twisted.internet import reactor, defer

        class JPLoop:

            def __init__(self):
                # exit code must be set when using quit, so if it's not set
                # something got wrong and we must report it
                self._exit_code = C.EXIT_INTERNAL_ERROR

            def run(self, jp, *args):
                self.jp = jp
                signal.signal(signal.SIGINT, self._on_sigint)
                defer.ensureDeferred(self._start(jp, *args))
                try:
                    reactor.run(installSignalHandlers=False)
                except SystemExit as e:
                    self._exit_code = e.code
                sys.exit(self._exit_code)

            async def _start(self, jp, *args):
                fut = asyncio.ensure_future(jp.main(*args))
                try:
                    await defer.Deferred.fromFuture(fut)
                except BaseException:
                    import traceback
                    traceback.print_exc()
                    jp.quit(1)

            def quit(self, exit_code):
                self._exit_code = exit_code
                reactor.stop()

            def _timeout_cb(self, args, callback, delay):
                try:
                    ret = callback(*args)
                # FIXME: temporary hack to avoid traceback when using XMLUI
                #        to be removed once create_task is not used anymore in
                #        xmlui_manager (i.e. once sat_frontends.tools.xmlui fully supports
                #        async syntax)
                except QuitException:
                    return
                if ret:
                    reactor.callLater(delay, self._timeout_cb, args, callback, delay)

            def call_later(self, delay, callback, *args):
                reactor.callLater(delay, self._timeout_cb, args, callback, delay)

            def _on_sigint(self, sig_number, stack_frame):
                """Called on keyboard interruption

                Print user interruption message, set exit code and stop reactor
                """
                print("\r" + USER_INTER_MSG)
                self._exit_code = C.EXIT_USER_CANCELLED
                reactor.callFromThread(reactor.stop)


    if bridge_name == "embedded":
        raise NotImplementedError
        # from sat.core import sat_main
        # sat = sat_main.SAT()

    return JPLoop
