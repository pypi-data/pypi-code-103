import json
import os
import shutil
import yaml
from manifest_to_helm import utils

class Chart:
    def __init__(self, description: str = '', name: str = '', version='1.0.0', app_version='1.0.0'):
        self.data = {}
        self.patterns = None
        self.description = description
        self.name = name
        self.version = version
        self.app_version = app_version
        self.values = {}
        self.output = {}
        self.helmignore = '''
# Patterns to ignore when building packages.
# This supports shell glob matching, relative path matching, and
# negation (prefixed with !). Only one pattern per line.
.DS_Store
# Common VCS dirs
.git/
.gitignore
.bzr/
.bzrignore
.hg/
.hgignore
.svn/
# Common backup files
*.swp
*.bak
*.tmp
*.orig
*~
# Various IDEs
.project
.idea/
*.tmproj
.vscode/
'''


    def loads_manifest(self, contents: str, name: str) -> None:
        self.data[name] = list(yaml.safe_load_all(contents))


    def load_manifest(self, path: str) -> None:
        files = [f for f in os.listdir(path)]
        for fi in files:
            with open(f'{path}/{fi}') as f:
                contents = f.read()
            name = '.'.join(fi.split('.')[:-1])
            self.loads_manifest(contents, name)


    def load_patterns(self, path: str) -> None:
        with open(path) as f:
            contents = f.read()
        self.patterns = json.loads(contents)

    
    def build_chart(self) -> None:
        to_replace = {}
        for name in self.data:
            for path in self.patterns['all']:
                for i in range(0, len(self.data[name])):
                    value = utils.get_from_key_list(self.data[name][i], path.split('.'))
                    if value:
                        self.values = utils.set_from_key_list(self.values, [name.replace('-', '_'), str(i), self.patterns['all'][path]['key']], value)
                        to_replace[f'{name}.{str(i)}.{self.patterns["all"][path]["key"]}'] = self.patterns['all'][path]['pattern'].replace('<<NAME>>', name.replace('-', '_')).replace('<<INDEX>>', str(i)).replace('<<KEY>>', self.patterns['all'][path]['key'])
                        self.data[name][i] = utils.set_from_key_list(self.data[name][i], path.split('.'), f'<<{name}.{str(i)}.{self.patterns["all"][path]["key"]}>>')
            if name in self.patterns.keys():
                for path in self.patterns[name]:
                    for i in range(0, len(self.data[name])):
                        value = utils.get_from_key_list(self.data[name][i], path.split('.'))
                        if value:
                            self.values = utils.set_from_key_list(self.values, [name.replace('-', '_'), str(i), self.patterns[name][path]['key']], utils.get_from_key_list(self.data[name][i], path.split('.')))
                            to_replace[f'{name}.{str(i)}.{self.patterns[name][path]["key"]}'] = self.patterns[name][path]['pattern'].replace('<<NAME>>', name.replace('-', '_')).replace('<<INDEX>>', str(i)).replace('<<KEY>>', self.patterns[name][path]['key'])
                            self.data[name][i] = utils.set_from_key_list(self.data[name][i], path.split('.'), f'<<{name}.{str(i)}.{self.patterns[name][path]["key"]}>>')
        for name in self.data:
            contents = yaml.dump_all(self.data[name])
            for k in to_replace:
                contents = contents.replace(f'<<{k}>>', to_replace[k])
            self.output[name] = contents

    def dump_chart(self, path: str, delete_existing: bool = False) -> None:
        if delete_existing and os.path.exists(path):
            shutil.rmtree(path)
        if not os.path.exists(path):
            os.mkdir(path)
        os.mkdir(f'{path}/charts')
        os.mkdir(f'{path}/templates')
        with open(f'{path}/.helmignore', 'w') as f:
            f.write(self.helmignore)
        with open(f'{path}/Chart.yaml', 'w') as f:
            yaml.dump(
                {
                    'apiVersion': 'v2',
                    'name': self.name,
                    'description': self.description,
                    'type': 'application',
                    'version': self.version,
                    'appVersion': self.app_version
                }, f
            )
        with open(f'{path}/values.yaml', 'w') as f:
            yaml.dump(self.values, f)
        for name in self.output:
            with open(f'{path}/templates/{name}.yaml', 'w') as f:
                f.write(self.output[name])