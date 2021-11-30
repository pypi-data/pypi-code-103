#!/ur/bin/env python3

import json
from sat.core.log import getLogger
from sat.core import exceptions
from libervia.server.tasks import task


log = getLogger(__name__)

SASS_SUFFIXES = ('.sass', '.scss')


class Task(task.Task):
    """Compile .sass and .scss files found in themes browser paths"""
    AFTER = ['js_modules']

    async def prepare(self):
        # we look for any Sass file, and cancel this task if none is found
        sass_dirs = set()
        for browser_path in self.resource.browser_modules.get('themes_browser_paths', []):
            for p in browser_path.iterdir():
                if p.suffix in SASS_SUFFIXES:
                    sass_dirs.add(browser_path)
                    break

        if not sass_dirs:
            raise exceptions.CancelError("No Sass file found")

        # we have some Sass files, we need to install the compiler
        d_path = self.resource.dev_build_path
        package_path = d_path / "package.json"
        try:
            with package_path.open() as f:
                package = json.load(f)
        except FileNotFoundError:
            package = {}
        except Exception as e:
            log.error(f"Unexepected exception while parsing package.json: {e}")

        if 'node-sass' not in package.setdefault('dependencies', {}):
            package['dependencies']['node-sass'] = 'latest'
            with package_path.open('w') as f:
                json.dump(package, f, indent=4)

        cmd = self.findCommand('yarnpkg', 'yarn')
        await self.runCommand(cmd, 'install', path=str(d_path))

        self.WATCH_DIRS = list(sass_dirs)

    async def onDirEvent(self, host, filepath, flags):
        if filepath.suffix in SASS_SUFFIXES:
            await self.manager.runTaskInstance(self)

    async def start(self):
        d_path = self.resource.dev_build_path
        node_sass = d_path / 'node_modules' / 'node-sass' / 'bin' / 'node-sass'
        for browser_path in self.resource.browser_modules['themes_browser_paths']:
            for p in browser_path.iterdir():
                if p.suffix not in SASS_SUFFIXES:
                    continue
                await self.runCommand(
                    str(node_sass),
                    "--omit-source-map-url",
                    "--output-style", "compressed",
                    "--output", str(self.build_path),
                    str(p),
                    path=str(self.build_path)
                )
