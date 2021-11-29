from asyncio.events import get_event_loop
from asyncio import sleep
from devdeck_core.controls.deck_control import DeckControl

from obswebsocket import obsws, requests, events
from obswebsocket.exceptions import ConnectionFailure


class OBSControl(DeckControl):
    def __init__(self, key_no, **kwargs):
        self.loop = get_event_loop()
        super().__init__(key_no, **kwargs)
        self.scene_name = self.settings["scene_name"]
        self.active = False
        self.obs = obsws()

    async def _connection_watcher(self):
        while True:
            while not self.obs.ws.connected:
                try:
                    self.obs.reconnect()
                    self._update_active()
                    self.obs.unregister(self._scene_switched)
                    self.obs.register(self._scene_switched, events.SwitchScenes)
                except ConnectionFailure:
                    await sleep(0.5)
            await sleep(10)

    def initialize(self):
        try:
            self.obs.connect()
        except ConnectionFailure:
            self.loop.create_task(self._update_display(True))
        self.obs.register(self._scene_switched, events.SwitchScenes)
        self.loop.create_task(self._connection_watcher())
        self._update_active()
        self.loop.create_task(self._update_display())

    def pressed(self):
        self.obs.call(requests.SetCurrentScene(self.scene_name))
        self.active = True
        self.loop.create_task(self._update_display(True))

    def _scene_switched(self, event):
        self.active = event.datain["scene-name"] == self.scene_name

    def _update_active(self):
        try:
            self.active = (
                self.obs.call(requests.GetCurrentScene()).getName() == self.scene_name
            )
        except:
            self.active = False

    async def _update_display(self, once=False):
        while True:
            color = "green" if self.active else "red"
            if not self.obs.ws.connected:
                color = "grey"
            with self.deck_context() as context:
                with context.renderer() as r:
                    r.emoji(self.settings["emoji"]).end()
                    r.colorize(color)
            if once:
                return
            await sleep(0.1)

    def settings_schema(self):
        return {"scene_name": {"type": "string"}, "emoji": {"type": "string"}}
