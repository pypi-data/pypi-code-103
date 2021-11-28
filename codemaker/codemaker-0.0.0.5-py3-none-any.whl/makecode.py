import os.path
import shutil
import yaml
from pathlib import Path

from jinja2 import Template, Environment


def render_string(s, config):
    tem = Environment().from_string(s)
    return tem.render(**config)


def is_template_str(s):
    return "{{" in s


def convert_item_path(path, config):
    new_path = render_string(path, config)
    shutil.move(path, new_path)
    return new_path


def convert_file_content(path, config):
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
    s_out = render_string(s, config)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(s_out)


def read_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
def write_yaml(data,path):
    with open(path, 'w', encoding='utf-8') as f:
        return yaml.dump(data,f)

class CodeGenerator:
    def __init__(self, extensions=None):
        if extensions is None:
            extensions = ['.py','.txt']
        self.extensions = extensions

    def should_file_be_converted(self, path: str):
        if os.path.isfile(path):
            for ext in self.extensions:
                if path.endswith(ext):
                    return True
        return False
    def generate(self, template_path, target_path, config_dict: dict, overwrite=False):
        if os.path.exists(target_path) and overwrite:
            print('Removing %s' % (target_path))
            shutil.rmtree(target_path) if os.path.isdir(target_path) else os.remove(target_path)


        if os.path.isfile(template_path):
            shutil.copy(template_path, target_path)
        else:
            assert os.path.isdir(template_path)
            shutil.copytree(template_path, target_path)
        self.convert_(target_path, config_dict)

    def convert_(self, path, config: dict):
        print('Converting %s ' % (path))
        if is_template_str(path):
            path = convert_item_path(path, config)
        if os.path.isfile(path):
            if self.should_file_be_converted(path):
                convert_file_content(path, config)
            return
        else:
            items = os.listdir(path)
            for item in items:
                self.convert_(os.path.join(path, item), config)




def gencode(src,dst,tmpl,overwrite=False):
    cfg=read_yaml(tmpl)
    cg=CodeGenerator(
        extensions=cfg['exts'],
    )
    cg.generate(src,dst,cfg['params'],overwrite=overwrite)
