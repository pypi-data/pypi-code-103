#!/usr/bin/env python3

# SàT plugin to manage Docker
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

from pathlib import Path
from twisted.python.procutils import which
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core import exceptions
from sat.core.log import getLogger
from sat.tools.common import async_process

log = getLogger(__name__)


PLUGIN_INFO = {
    C.PI_NAME: "Docker Applications Manager",
    C.PI_IMPORT_NAME: "APP_MANAGER_DOCKER",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_DEPENDENCIES: ["APP_MANAGER"],
    C.PI_MAIN: "AppManagerDocker",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Applications Manager for Docker"""),
}


class AppManagerDocker:
    name = "docker-compose"
    discover_path = Path(__file__).parent

    def __init__(self, host):
        log.info(_("Docker App Manager initialization"))
        try:
            self.docker_compose_path = which('docker-compose')[0]
        except IndexError:
            raise exceptions.NotFound(
                '"docker-compose" executable not found, Docker can\'t be used with '
                'application manager')
        self.host = host
        self._am = host.plugins['APP_MANAGER']
        self._am.register(self)

    async def start(self, app_data: dict) -> None:
        await self._am.startCommon(app_data)
        working_dir = app_data['_instance_dir_path']
        try:
            override = app_data['override']
        except KeyError:
            pass
        else:
            log.debug("writting override file")
            override_path = working_dir / "docker-compose.override.yml"
            with override_path.open("w") as f:
                self._am.dump(override, f)
        await async_process.run(
            self.docker_compose_path,
            "up",
            "--detach",
            path=str(working_dir),
        )

    async def stop(self, app_data: dict) -> None:
        working_dir = app_data['_instance_dir_path']
        await async_process.run(
            self.docker_compose_path,
            "down",
            path=str(working_dir),
        )

    async def computeExpose(self, app_data: dict) -> dict:
        working_dir = app_data['_instance_dir_path']
        expose = app_data['expose']
        ports = expose.get('ports', {})
        for name, port_data in list(ports.items()):
            try:
                service = port_data['service']
                private = port_data['private']
                int(private)
            except (KeyError, ValueError):
                log.warning(
                    f"invalid value found for {name!r} port in {app_data['_file_path']}")
                continue
            exposed_port = await async_process.run(
                self.docker_compose_path,
                "port",
                service,
                str(private),
                path=str(working_dir),
            )
            exposed_port = exposed_port.decode().strip()
            try:
                addr, port = exposed_port.split(':')
                int(port)
            except ValueError:
                log.warning(
                    f"invalid exposed port for {name}, ignoring: {exposed_port!r}")
                del ports[name]
            else:
                ports[name] = exposed_port
