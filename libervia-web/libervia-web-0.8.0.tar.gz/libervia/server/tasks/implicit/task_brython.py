#!/ur/bin/env python3

import shutil
import json
from pathlib import Path
from ast import literal_eval
from sat.core.i18n import _
from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools.common import utils
from libervia.server.constants import Const as C
from libervia.server.classes import Script
from libervia.server.tasks import task


log = getLogger(__name__)


class Task(task.Task):

    def prepare(self):
        if "brython" not in self.resource.browser_modules:
            raise exceptions.CancelError("No brython module found")

        brython_js = self.build_path / "brython.js"
        if not brython_js.is_file():
            installed_ver = None
        else:
            with brython_js.open() as f:
                for line in f:
                    if line.startswith('// implementation ['):
                        installed_ver = literal_eval(line[18:])[:3]
                        log.debug(
                            f"brython v{'.'.join(str(v) for v in installed_ver)} already "
                            f"installed")
                        break
                else:
                    log.warning(
                        f"brython file at {brython_js} doesn't has implementation "
                        f"version"
                    )
                    installed_ver = None

        try:
            import brython
        except ModuleNotFoundError as e:
            log.error('"brython" module is missing, can\'t use browser code for Brython')
            raise e
        ver = [int(v) for v in brython.implementation.split('.')[:3]]
        if ver != installed_ver:
            log.info(_("Installing Brython v{version}").format(
                version='.'.join(str(v) for v in ver)))
            data_path = Path(brython.__file__).parent / 'data'
            # shutil has blocking method, but the task is run before we start
            # the web server, so it's not a big deal
            shutil.copyfile(data_path / "brython.js", brython_js)
            shutil.copy(data_path / "brython_stdlib.js", self.build_path)
        else:
            log.debug("Brython is already installed")

        self.WATCH_DIRS = []
        self.setCommonScripts()

    def setCommonScripts(self):
        for dyn_data in self.resource.browser_modules["brython"]:
            url_hash = dyn_data['url_hash']
            import_url = f"/{C.BUILD_DIR}/{C.BUILD_DIR_DYN}/{url_hash}"
            dyn_data.setdefault('scripts', utils.OrderedSet()).update([
                Script(src=f"/{C.BUILD_DIR}/brython.js"),
                Script(src=f"/{C.BUILD_DIR}/brython_stdlib.js"),
            ])
            dyn_data.setdefault('template', {})['body_onload'] = self.getBodyOnload(
                extra_path=[import_url])
            self.WATCH_DIRS.append(dyn_data['path'].resolve())

    def getBodyOnload(self, debug=True, cache=True, extra_path=None):
            on_load_opts = {"pythonpath": [f"/{C.BUILD_DIR}"]}
            if debug:
                on_load_opts[debug] = 1
            if cache:
                on_load_opts["cache"] = True
            if extra_path is not None:
                on_load_opts["pythonpath"].extend(extra_path)

            return f"brython({json.dumps(on_load_opts)})"

    def copyFiles(self, files_paths, dest):
        for p in files_paths:
            log.debug(f"copying {p}")
            if p.is_dir():
                if p.name == '__pycache__':
                    continue
                shutil.copytree(p, dest / p.name)
            else:
                shutil.copy(p, dest)

    async def onDirEvent(self, host, filepath, flags):
        self.setCommonScripts()
        await self.manager.runTaskInstance(self)

    def start(self):
        dyn_path = self.build_path / C.BUILD_DIR_DYN
        for dyn_data in self.resource.browser_modules["brython"]:
            url_hash = dyn_data['url_hash']
            if url_hash is None:
                # root modules
                url_prefix = dyn_data.get('url_prefix')
                if url_prefix is None:
                    dest = self.build_path
                    init_dest_url = f"/{C.BUILD_DIR}/__init__.py"
                else:
                    dest = self.build_path / url_prefix
                    dest.mkdir(exist_ok = True)
                    init_dest_url = f"/{C.BUILD_DIR}/{url_prefix}/__init__.py"

                self.copyFiles(dyn_data['path'].glob('*py'), dest)

                init_file = dyn_data['path'] / '__init__.py'
                if init_file.is_file():
                    self.resource.dyn_data_common['scripts'].update([
                        Script(src=f"/{C.BUILD_DIR}/brython.js"),
                        Script(type='text/python', src=init_dest_url)
                    ])
                    self.resource.dyn_data_common.setdefault(
                        "template", {})['body_onload'] = self.getBodyOnload()
            else:
                page_dyn_path = dyn_path / url_hash
                log.debug(f"using dynamic path at {page_dyn_path}")
                if page_dyn_path.exists():
                    log.debug("cleaning existing path")
                    shutil.rmtree(page_dyn_path)

                page_dyn_path.mkdir(parents=True, exist_ok=True)
                log.debug("copying browser python files")
                self.copyFiles(dyn_data['path'].iterdir(), page_dyn_path)

                script = Script(
                    type='text/python',
                    src=f"/{C.BUILD_DIR}/{C.BUILD_DIR_DYN}/{url_hash}/__init__.py"
                )
                dyn_data.setdefault('scripts', utils.OrderedSet()).add(script)
