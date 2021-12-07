import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional, Callable, Type

from bs4 import BeautifulSoup
from pydantic import parse_obj_as
from websocket import create_connection, WebSocket

from webpilot import models
from webpilot.config import WebPilotConfig

is_windows = sys.platform.startswith('win')


def _send_message(id: int, ws: WebSocket, expected: Optional[models.Model], method: str, session_id: Optional[str],
                  payload: dict) -> models.Model:
    msg = {'id': id, 'method': method, 'params': payload}
    if session_id is not None:
        msg['sessionId'] = session_id
    ws.send(json.dumps(msg))
    while True:
        return_value: dict = json.loads(ws.recv())
        if return_value.get('id', None) is None:
            continue

        error_value = return_value.get('error', None)
        if error_value is not None:
            raise error_value

        result_value: Optional[dict] = return_value.get('result', None)
        if result_value is None:
            continue

        if expected is None:
            return None

        return parse_obj_as(expected, result_value)


class Tab:
    def __init__(self, send_msg: Callable, tab: Type[models.Target]):
        self._send_message = send_msg
        self._tab = tab

    def navigate(self, url: str, delay: int = 1):
        """navigate to a url an await delay seconds before return the page"""
        page = self._send_message(models.Page, "Page.navigate", self._tab.sessionId, {
            'url': url
        })
        page.target = self._tab
        time.sleep(delay)
        return Page(self._send_message, page)

    def close(self):
        self._send_message(models.Target, "Target.detachFromTarget", None, {
            'targetId': self._tab.targetId,
            'sessionId': self._tab.sessionId
        })
        self._send_message(models.Target, "Target.closeTarget", None, {
            'targetId': self._tab.targetId
        })

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class Page:
    def __init__(self, send_msg: Callable, page: Type[models.Page]):
        self._send_message = send_msg
        self._page = page

    def get_content(self):
        document = self._send_message(
            models.Document, 'DOM.getDocument', self._page.target.sessionId, {})
        content = self._send_message(models.OuterHTML, 'DOM.getOuterHTML', self._page.target.sessionId, {
            'nodeId': document.root.nodeId
        })
        return content.outerHTML

    def get_dom(self):
        return BeautifulSoup(self.get_content(), features="html.parser")


class Robot:
    def __init__(self, process: subprocess.Popen, endpoint: str, port: int):
        self._process = process
        self._counter = 0
        self._endpoint = endpoint
        self._port = port
        self._ws = create_connection(self._endpoint)

    def _send_message(self, expected: models.Model, method: str, session_id: Optional[str],
                      payload: dict) -> models.Model:
        self._counter = self._counter + 1
        return _send_message(self._counter, self._ws, expected,
                             method, session_id, payload)

    def new_tab(self):
        """Open a tab in the browser"""
        target = self._send_message(models.Target, "Target.createTarget", None, {
            'url': 'about:blank'
        })
        result = self._send_message(models.Target, "Target.attachToTarget", None, {
            'targetId': target.targetId,
            'flatten': True
        })
        result.targetId = target.targetId
        return Tab(self._send_message, result)

    def close(self):
        self._ws.close()
        self._process.kill()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


def open_chrome(config: WebPilotConfig = WebPilotConfig()):
    arguments = [config.chrome_executable]
    arguments.append(f'--remote-debugging-port={config.remote_port}')

    if config.headless:
        arguments.append('--headless')
        if is_windows:
            arguments.append('--disable-gpu')
    else:
        Path('.webrobot_data').mkdir(exist_ok=True)
        arguments.append(
            "--no-default-browser-check --user-data-dir=.webrobot_data")

    if not config.sandboxed:
        arguments.append('--no-sandbox')

    arguments.append(config.url)

    process = subprocess.Popen(arguments)

    time.sleep(1)

    with urllib.request.urlopen(f'http://localhost:{config.remote_port}/json/version') as response:
        metadata: dict = json.loads(response.read())
        endpoint = metadata.get('webSocketDebuggerUrl')

    return Robot(process=process, endpoint=endpoint, port=config.remote_port)
