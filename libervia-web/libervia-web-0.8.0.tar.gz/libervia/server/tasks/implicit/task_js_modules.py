#!/ur/bin/env python3

import json
from pathlib import Path
from sat.core.i18n import _
from sat.core.log import getLogger
from sat.core import exceptions
from libervia.server.constants import Const as C
from libervia.server.tasks import task


log = getLogger(__name__)


class Task(task.Task):

    async def prepare(self):
        if "js" not in self.resource.browser_modules:
            raise exceptions.CancelError("No JS module needed")

    async def start(self):
        js_data = self.resource.browser_modules['js']
        package = js_data.get('package', {})
        package_path = self.build_path / 'package.json'
        with package_path.open('w') as f:
            json.dump(package, f)

        cmd = self.findCommand('yarnpkg', 'yarn')
        await self.runCommand(cmd, 'install', path=str(self.build_path))

        try:
            brython_map = js_data['brython_map']
        except KeyError:
            pass
        else:
            log.info(_("creating JS modules mapping for Brython"))
            js_modules_path = self.build_path / 'js_modules'
            js_modules_path.mkdir(exist_ok=True)
            init_path = js_modules_path / '__init__.py'
            init_path.touch()

            for module_name, module_data in brython_map.items():
                log.debug(f"generating mapping for {module_name}")
                if ' ' in module_name:
                    raise ValueError(
                        f"module {module_name!r} has space(s), it must not!")
                module_path = js_modules_path / f"{module_name}.py"
                if isinstance(module_data, str):
                    module_data = {'path': module_data}
                try:
                    js_path = module_data.pop('path')
                except KeyError:
                    raise ValueError(
                        f'module data for {module_name} must have a "path" key')
                module_data['path'] = Path('node_modules') / js_path.strip(' /')
                export = module_data.get('export') or [module_name]
                export_objects = '\n'.join(f'{e} = window.{e}' for e in export)
                extra_kwargs = {"build_dir": C.BUILD_DIR}

                with module_path.open('w') as f:
                    f.write(f"""\
#!/usr/bin/env python3
from browser import window, load
{module_data.get('extra_import', '')}

load("{Path('/').joinpath(C.BUILD_DIR, module_data['path'])}")
{export_objects}
{module_data.get('extra_init', '').format(**extra_kwargs)}
""")
