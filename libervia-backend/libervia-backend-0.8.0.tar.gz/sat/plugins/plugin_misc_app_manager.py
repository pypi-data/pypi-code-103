#!/usr/bin/env python3

# SàT plugin to manage external applications
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
from typing import Optional, List
from functools import partial, reduce
import tempfile
import secrets
import string
import shortuuid
from twisted.internet import defer
from twisted.python.procutils import which
from sat.core.i18n import _
from sat.core import exceptions
from sat.core.constants import Const as C
from sat.core.log import getLogger
from sat.tools.common import data_format
from sat.tools.common import async_process

log = getLogger(__name__)

try:
    import yaml
except ImportError:
    raise exceptions.MissingModule(
        'Missing module PyYAML, please download/install it. You can use '
        '"pip install pyyaml"'
    )

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    log.warning(
        "Can't use LibYAML binding (is libyaml installed?), pure Python version will be "
        "used, but it is slower"
    )
    from yaml import Loader, Dumper

from yaml.constructor import ConstructorError


PLUGIN_INFO = {
    C.PI_NAME: "Applications Manager",
    C.PI_IMPORT_NAME: "APP_MANAGER",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MODES: C.PLUG_MODE_BOTH,
    C.PI_MAIN: "AppManager",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(
        """Applications Manager

Manage external applications using packagers, OS virtualization/containers or other
software management tools.
"""),
}

APP_FILE_PREFIX = "sat_app_"


class AppManager:
    load = partial(yaml.load, Loader=Loader)
    dump = partial(yaml.dump, Dumper=Dumper)

    def __init__(self, host):
        log.info(_("plugin Applications Manager initialization"))
        self.host = host
        self._managers = {}
        self._apps = {}
        self._started = {}
        # instance id to app data map
        self._instances = {}
        host.bridge.addMethod(
            "applicationsList",
            ".plugin",
            in_sign="as",
            out_sign="as",
            method=self.list_applications,
        )
        host.bridge.addMethod(
            "applicationStart",
            ".plugin",
            in_sign="ss",
            out_sign="",
            method=self._start,
            async_=True,
        )
        host.bridge.addMethod(
            "applicationStop",
            ".plugin",
            in_sign="sss",
            out_sign="",
            method=self._stop,
            async_=True,
        )
        host.bridge.addMethod(
            "applicationExposedGet",
            ".plugin",
            in_sign="sss",
            out_sign="s",
            method=self._getExposed,
            async_=True,
        )
        yaml.add_constructor(
            "!sat_conf", self._sat_conf_constr, Loader=Loader)
        yaml.add_constructor(
            "!sat_generate_pwd", self._sat_generate_pwd_constr, Loader=Loader)
        yaml.add_constructor(
            "!sat_param", self._sat_param_constr, Loader=Loader)

    def unload(self):
        log.debug("unloading applications manager")
        for instances in self._started.values():
            for instance in instances:
                data = instance['data']
                if not data['single_instance']:
                    log.debug(
                        f"cleaning temporary directory at {data['_instance_dir_path']}")
                    data['_instance_dir_obj'].cleanup()

    def _sat_conf_constr(self, loader, node):
        """Get a value from SàT configuration

        A list is expected with either "name" of a config parameter, a one or more of
        those parameters:
            - section
            - name
            - default value
            - filter
        filter can be:
            - "first": get the first item of the value
        """
        config_data = loader.construct_sequence(node)
        if len(config_data) == 1:
            section, name, default, filter_ = "", config_data[0], None, None
        if len(config_data) == 2:
            (section, name), default, filter_ = config_data, None, None
        elif len(config_data) == 3:
            (section, name, default), filter_ = config_data, None
        elif len(config_data) == 4:
            section, name, default, filter_ = config_data
        else:
            raise ValueError(
                f"invalid !sat_conf value ({config_data!r}), a list of 1 to 4 items is "
                "expected"
            )

        value = self.host.memory.getConfig(section, name, default)
        # FIXME: "public_url" is used only here and doesn't take multi-sites into account
        if name == "public_url" and (not value or value.startswith('http')):
            if not value:
                log.warning(_(
                    'No value found for "public_url", using "example.org" for '
                    'now, please set the proper value in libervia.conf'))
            else:
                log.warning(_(
                    'invalid value for "public_url" ({value}), it musts not start with '
                    'schema ("http"), ignoring it and using "example.org" '
                    'instead')
                        .format(value=value))
            value = "example.org"

        if filter_ is None:
            pass
        elif filter_ == 'first':
            value = value[0]
        else:
            raise ValueError(f"unmanaged filter: {filter_}")

        return value

    def _sat_generate_pwd_constr(self, loader, node):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(30))

    def _sat_param_constr(self, loader, node):
        """Get a parameter specified when starting the application

        The value can be either the name of the parameter to get, or a list as
        [name, default_value]
        """
        try:
            name, default = loader.construct_sequence(node)
        except ConstructorError:
            name, default = loader.construct_scalar(node), None
        return self._params.get(name, default)

    def register(self, manager):
        name = manager.name
        if name in self._managers:
            raise exceptions.ConflictError(
                f"There is already a manager with the name {name}")
        self._managers[manager.name] = manager
        if hasattr(manager, "discover_path"):
            self.discover(manager.discover_path, manager)

    def getManager(self, app_data: dict) -> object:
        """Get manager instance needed for this app

        @raise exceptions.DataError: something is wrong with the type
        @raise exceptions.NotFound: manager is not registered
        """
        try:
            app_type = app_data["type"]
        except KeyError:
            raise exceptions.DataError(
                "app file doesn't have the mandatory \"type\" key"
            )
        if not isinstance(app_type, str):
            raise exceptions.DataError(
                f"invalid app data type: {app_type!r}"
            )
        app_type = app_type.strip()
        try:
            return self._managers[app_type]
        except KeyError:
            raise exceptions.NotFound(
                f"No manager found to manage app of type {app_type!r}")

    def getAppData(
        self,
        id_type: Optional[str],
        identifier: str
    ) -> dict:
        """Retrieve instance's app_data from identifier

        @param id_type: type of the identifier, can be:
            - "name": identifier is a canonical application name
                the first found instance of this application is returned
            - "instance": identifier is an instance id
        @param identifier: identifier according to id_type
        @return: instance application data
        @raise exceptions.NotFound: no instance with this id can be found
        @raise ValueError: id_type is invalid
        """
        if not id_type:
            id_type = 'name'
        if id_type == 'name':
            identifier = identifier.lower().strip()
            try:
                return next(iter(self._started[identifier]))
            except (KeyError, StopIteration):
                raise exceptions.NotFound(
                    f"No instance of {identifier!r} is currently running"
                )
        elif id_type == 'instance':
            instance_id = identifier
            try:
                return self._instances[instance_id]
            except KeyError:
                raise exceptions.NotFound(
                    f"There is no application instance running with id {instance_id!r}"
                )
        else:
            raise ValueError(f"invalid id_type: {id_type!r}")

    def discover(
            self,
            dir_path: Path,
            manager: Optional = None
    ) -> None:
        for file_path in dir_path.glob(f"{APP_FILE_PREFIX}*.yaml"):
            if manager is None:
                try:
                    app_data = self.parse(file_path)
                    manager = self.getManager(app_data)
                except (exceptions.DataError, exceptions.NotFound) as e:
                    log.warning(
                        f"Can't parse {file_path}, skipping: {e}")
            app_name = file_path.stem[len(APP_FILE_PREFIX):].strip().lower()
            if not app_name:
                log.warning(
                    f"invalid app file name at {file_path}")
                continue
            app_dict = self._apps.setdefault(app_name, {})
            manager_set = app_dict.setdefault(manager, set())
            manager_set.add(file_path)
            log.debug(
                f"{app_name!r} {manager.name} application found"
            )

    def parse(self, file_path: Path, params: Optional[dict] = None) -> dict:
        """Parse SàT application file

        @param params: parameters for running this instance
        @raise exceptions.DataError: something is wrong in the file
        """
        if params is None:
            params = {}
        with file_path.open() as f:
            # we set parameters to be used only with this instance
            # no async method must used between this assignation and `load`
            self._params = params
            app_data = self.load(f)
            self._params = None
        if "name" not in app_data:
            # note that we don't use lower() here as we want human readable name and
            # uppercase may be set on purpose
            app_data['name'] = file_path.stem[len(APP_FILE_PREFIX):].strip()
        single_instance = app_data.setdefault("single_instance", True)
        if not isinstance(single_instance, bool):
            raise ValueError(
                f'"single_instance" must be a boolean, but it is {type(single_instance)}'
            )
        return app_data

    def list_applications(self, filters: Optional[List[str]]) -> List[str]:
        """List available application

        @param filters: only show applications matching those filters.
            using None will list all known applications
            a filter can be:
                - available: applications available locally
                - running: only show launched applications
        """
        if not filters:
            return list(self.apps)
        found = set()
        for filter_ in filters:
            if filter_ == "available":
                found.update(self._apps)
            elif filter_ == "running":
                found.update(self._started)
            else:
                raise ValueError(f"Unknown filter: {filter_}")
        return list(found)

    def _start(self, app_name, extra):
        extra = data_format.deserialise(extra)
        return defer.ensureDeferred(self.start(str(app_name), extra))

    async def start(
        self,
        app_name: str,
        extra: Optional[dict] = None,
    ) -> None:
        # FIXME: for now we use the first app manager available for the requested app_name
        # TODO: implement running multiple instance of the same app if some metadata
        #   to be defined in app_data allows explicitly it.
        app_name = app_name.lower().strip()
        try:
            app_file_path = next(iter(next(iter(self._apps[app_name].values()))))
        except KeyError:
            raise exceptions.NotFound(
                f"No application found with the name {app_name!r}"
            )
        started_data = self._started.setdefault(app_name, [])
        app_data = self.parse(app_file_path, extra)
        app_data['_file_path'] = app_file_path
        app_data['_name_canonical'] = app_name
        single_instance = app_data['single_instance']
        if single_instance:
            if started_data:
                log.info(f"{app_name!r} is already started")
                return
            else:
                cache_path = self.host.memory.getCachePath(
                    PLUGIN_INFO[C.PI_IMPORT_NAME], app_name
                )
                cache_path.mkdir(0o700, parents=True, exist_ok=True)
                app_data['_instance_dir_path'] = cache_path
        else:
            dest_dir_obj = tempfile.TemporaryDirectory(prefix="sat_app_")
            app_data['_instance_dir_obj'] = dest_dir_obj
            app_data['_instance_dir_path'] = Path(dest_dir_obj.name)
        instance_id = app_data['_instance_id'] = shortuuid.uuid()
        manager = self.getManager(app_data)
        app_data['_manager'] = manager
        started_data.append(app_data)
        self._instances[instance_id] = app_data

        try:
            start = manager.start
        except AttributeError:
            raise exceptions.InternalError(
                f"{manager.name} doesn't have the mandatory \"start\" method"
            )
        else:
            await start(app_data)
        log.info(f"{app_name!r} started")

    def _stop(self, identifier, id_type, extra):
        extra = data_format.deserialise(extra)
        return defer.ensureDeferred(
            self.stop(str(identifier), str(id_type) or None, extra))

    async def stop(
        self,
        identifier: str,
        id_type: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> None:
        if extra is None:
            extra = {}

        app_data = self.getAppData(id_type, identifier)

        log.info(f"stopping {app_data['name']!r}")

        app_name = app_data['_name_canonical']
        instance_id = app_data['_instance_id']
        manager = app_data['_manager']

        try:
            stop = manager.stop
        except AttributeError:
            raise exceptions.InternalError(
                f"{manager.name} doesn't have the mandatory \"stop\" method"
            )
        else:
            try:
                await stop(app_data)
            except Exception as e:
                log.warning(
                    f"Instance {instance_id} of application {app_name} can't be stopped "
                    f"properly: {e}"
                )
                return

        try:
            del self._instances[instance_id]
        except KeyError:
            log.error(
                f"INTERNAL ERROR: {instance_id!r} is not present in self._instances")

        try:
            self._started[app_name].remove(app_data)
        except ValueError:
            log.error(
                "INTERNAL ERROR: there is no app data in self._started with id "
                f"{instance_id!r}"
            )

        log.info(f"{app_name!r} stopped")

    def _getExposed(self, identifier, id_type, extra):
        extra = data_format.deserialise(extra)
        d = defer.ensureDeferred(self.getExposed(identifier, id_type, extra))
        d.addCallback(lambda d: data_format.serialise(d))
        return d

    def getValueFromPath(self, app_data: dict, path: List[str]) -> any:
        """Retrieve a value set in the data from it path

        @param path: list of key to use in app_data to retrieve the value
        @return: found value
        @raise NotFound: the value can't be found
        """

    async def getExposed(
        self,
        identifier: str,
        id_type: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> dict:
        """Get data exposed by the application

        The manager's "computeExpose" method will be called if it exists. It can be used
        to handle manager specific conventions.
        """
        app_data = self.getAppData(id_type, identifier)
        if app_data.get('_exposed_computed', False):
            return app_data['expose']
        if extra is None:
            extra = {}
        expose = app_data.setdefault("expose", {})
        if "passwords" in expose:
            passwords = expose['passwords']
            for name, value in list(passwords.items()):
                if isinstance(value, list):
                    # if we have a list, is the sequence of keys leading to the value
                    # to expose. We use "reduce" to retrieve the desired value
                    try:
                        passwords[name] = reduce(lambda l, k: l[k], value, app_data)
                    except Exception as e:
                        log.warning(
                            f"Can't retrieve exposed value for password {name!r}: {e}")
                        del passwords[name]

        url_prefix = expose.get("url_prefix")
        if isinstance(url_prefix, list):
            try:
                expose["url_prefix"] = reduce(lambda l, k: l[k], url_prefix, app_data)
            except Exception as e:
                log.warning(
                    f"Can't retrieve exposed value for url_prefix: {e}")
                del expose["url_prefix"]

        try:
            computeExpose = app_data['_manager'].computeExpose
        except AttributeError:
            pass
        else:
            await computeExpose(app_data)

        app_data['_exposed_computed'] = True
        return expose

    async def _doPrepare(
        self,
        app_data: dict,
    ) -> None:
        name = app_data['name']
        dest_path = app_data['_instance_dir_path']
        if next(dest_path.iterdir(), None) != None:
            log.debug(f"There is already a prepared dir at {dest_path}, nothing to do")
            return
        try:
            prepare = app_data['prepare'].copy()
        except KeyError:
            prepare = {}

        if not prepare:
            log.debug("Nothing to prepare for {name!r}")
            return

        for action, value in list(prepare.items()):
            log.debug(f"[{name}] [prepare] running {action!r} action")
            if action == "git":
                try:
                    git_path = which('git')[0]
                except IndexError:
                    raise exceptions.NotFound(
                        "Can't find \"git\" executable, {name} can't be started without it"
                    )
                await async_process.run(git_path, "clone", value, str(dest_path))
                log.debug(f"{value!r} git repository cloned at {dest_path}")
            else:
                raise NotImplementedError(
                    f"{action!r} is not managed, can't start {name}"
                )
            del prepare[action]

        if prepare:
            raise exceptions.InternalError('"prepare" should be empty')

    async def _doCreateFiles(
        self,
        app_data: dict,
    ) -> None:
        dest_path = app_data['_instance_dir_path']
        files = app_data.get('files')
        if not files:
            return
        if not isinstance(files, dict):
            raise ValueError('"files" must be a dictionary')
        for filename, data in files.items():
            path = dest_path / filename
            if path.is_file():
                log.info(f"{path} already exists, skipping")
            with path.open("w") as f:
                f.write(data.get("content", ""))
            log.debug(f"{path} created")

    async def startCommon(self, app_data: dict) -> None:
        """Method running common action when starting a manager

        It should be called by managers in "start" method.
        """
        log.info(f"starting {app_data['name']!r}")
        await self._doPrepare(app_data)
        await self._doCreateFiles(app_data)
