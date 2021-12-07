import os
import json
from copy import deepcopy
import yaml

class PipielineMigrations:

    POPKeys = ['http_proxy', 'https_proxy', 'pxml', 'notify', 'clean']
    SECRETKeys = ['password', 'phrase']

    def __init__(self, pipelines_location, git_location, type):
        self.path = pipelines_location
        self.passwords = {}
        self.dest_path = os.path.join(git_location, 'config', 'pypers', type)
        os.makedirs(self.dest_path, exist_ok=True)


    def start(self):
        files = self._get_files()
        parsed_files = {}
        for f in files:
            name, yaml_data = self._parse_pipeline(f)
            parsed_files[name] = yaml_data
        for name in parsed_files.keys():
            d_path = os.path.join(self.dest_path, "%s.yml" % name)
            with open(d_path, 'w') as f:
                f.write(parsed_files[name])
        with open('secrets.txt', 'w') as f:
            for key in self.passwords:
                f.write('%s %s\n' % (key, self.passwords[key]))


    def _parse_pipeline(self, path):
        name, _ = os.path.splitext(os.path.basename(path))
        name = name.replace('_fetch', '')
        with open(path, 'r') as f:
            raw_data = json.loads(f.read())
            self._parse_data(raw_data, name)
            return name, yaml.safe_dump(raw_data)

    def _get_password_filed(self, key, collection):
        return "${%s_%s}" % (collection.upper(), key.upper())

    def  _parse_data(self, d, collection, root=[]):
        if isinstance(d, dict):
            to_remove = []
            for key in d.keys():
                tmp = deepcopy(root)
                if key in self.POPKeys:
                    to_remove.append(key)
                    continue
                for secret_el in self.SECRETKeys:
                    if secret_el in key.lower():
                        password_filed = self._get_password_filed(key, collection)
                        self.passwords[password_filed] = d[key]
                        d[key] = password_filed
                tmp.append(key)
                self._parse_data(d[key], collection, tmp)
            for k in to_remove:
                d.pop(k)
        elif isinstance(d, list):
            for e in d:
                self._parse_data(e, collection, root)





    def _get_files(self):
        pipeline_files = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if f.endswith(".json"):
                    pipeline_files.append(os.path.join(root, f))
        return pipeline_files
