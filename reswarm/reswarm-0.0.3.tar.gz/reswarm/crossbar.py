import asyncio
import os
import threading
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth
from autobahn.asyncio.wamp import ApplicationRunner

DATAPODS_WS_URI = "ws://35.187.185.237:8088/ws"
STUDIO_WS_URI = "ws://cb.reswarm.io:8080/ws"

socketURIMap = {
    "https://studio.datapods.io": DATAPODS_WS_URI,
    "https://studio.record-evolution.com": STUDIO_WS_URI,
}

def getWebSocketURI():
    reswarm_url = os.environ.get("RESWARM_URL")
    if not reswarm_url:
        reswarm_url = DATAPODS_WS_URI
    return reswarm_url

class _Component(ApplicationSession):
    def __init__(self, config=None, serial_number=None, setSession=None):
        super().__init__(config=config)

        self.serial_number = serial_number
        self.setSession = setSession

    def onConnect(self):
        self.join(u'userapps', [u"wampcra"], self.serial_number)

    def onChallenge(self, challenge):
        if challenge.method == u"wampcra":
            signature = auth.compute_wcs(
                self.serial_number, challenge.extra['challenge'])
            return signature

        raise Exception("Invalid authmethod {}".format(challenge.method))

    def onJoin(self, details):
        self.setSession(self)
        print("Connected to the user realm as:", self.serial_number)

    def onLeave(self, details):
        self.disconnect()

    def onDisconnect(self):
        loop = asyncio.get_running_loop()

        loop.stop()
        loop.close()


class CrossbarConnection():
    def __init__(self, serial_number: str) -> None:
        self.session = None
        self.loop = None
        self.serial_number = serial_number

    def start(self):
        t = threading.Thread(target=self._initSessionLoop)
        t.start()

    def _setSession(self, session):
        self.session = session

    def getEventLoop(self):
        while self.loop == None:
            continue

        return self.loop

    def getSession(self) -> ApplicationSession:
        while self.session == None:
            continue

        return self.session

    def _componentAdapter(self, serial_number, setSession):
        def x(config):
            return _Component(config, serial_number, setSession)

        return x

    def _initSessionLoop(self):
        self.runner = ApplicationRunner(
            url=getWebSocketURI(),
            realm="userapps"
        )

        loop = asyncio.new_event_loop()
        self.loop = loop

        asyncio.set_event_loop(loop)
        component = self._componentAdapter(self.serial_number, self._setSession)
        coro = self.runner.run(component, False)
        loop.run_until_complete(coro)
        loop.run_forever()
