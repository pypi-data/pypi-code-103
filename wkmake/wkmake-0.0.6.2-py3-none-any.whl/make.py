import os,glob
from jinja2 import Template,Environment
import json
import shutil
# WKMAKE_FILENAME='wkmake.json'
WKMAKE_FILENAME='wkmake.yaml'
DEFAULT_CONFIG=dict(
)

def load_json(f):
    with open(f,'r',encoding='utf-8') as fp:
        return json.load(fp)
def load_yaml(f):
    import yaml
    with open(f,'r',encoding='utf-8') as fp:
        return yaml.safe_load(fp)
def check_config(local_config,config):
    assert isinstance(local_config,dict)
    assert isinstance(config,dict)
    required_vars=local_config.get('required_vars',None)
    defaults=local_config.get('defaults',{})
    if required_vars:
        for item in required_vars:
            if not item in config.keys():
                raise Exception('Variable %s is required  but not given.'%(item,))
    tmp={}
    tmp.update(defaults)
    for k,v in config.items():
        if v is None and (defaults.get(k,None) is not None):
            continue
        tmp[k]=v
    return tmp
def read_dir_info(dir):
    cfg={}
    if os.path.exists(os.path.join(dir, WKMAKE_FILENAME)):
        cfg = load_yaml(os.path.join(dir, WKMAKE_FILENAME))
    return cfg
def make_file(src_path,dst_path,config={},overwrite=False):
    if os.path.exists(dst_path):
        if not  overwrite:
            raise FileExistsError('File already existed at %s, while overwrite is not True' % (dst_path))
        else:
            os.remove(dst_path)
    print('reading %s' % (src_path))
    with open(src_path, 'r',encoding='utf-8') as f:
        s=f.read()
        template = Environment().from_string(s)
        s = template.render(**config)
    shutil.copy(src_path,dst_path)
    with open(dst_path, 'w') as f:
        f.write(s)


def make_simple(template_dir,out_dir,config,overwrite=False):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    fs=os.listdir(template_dir)
    for i,fn in enumerate(fs):
        template_path=os.path.join(template_dir,fn)
        dst_path=os.path.join(out_dir,fn)
        make_file(template_path,dst_path,config,overwrite=overwrite)

def make_recursively(src_path, dst_path, config=None, overwrite=False):
    if config is None:
        config = {}
    if not isinstance(config,dict):
        assert isinstance(config,ConfigBase)
        config=config.to_dict()
    default=DEFAULT_CONFIG.copy()
    default.update(config)
    config=default
    if os.path.isfile(src_path):
        make_file(src_path,dst_path,config,overwrite=overwrite)
        print('Render template from %s to %s.' % (src_path,dst_path))
    elif os.path.isdir(src_path):
        if os.path.basename(src_path)=='__pycache__':
            return
        if os.path.exists(os.path.join(src_path,WKMAKE_FILENAME)):
            cfg=load_yaml(os.path.join(src_path,WKMAKE_FILENAME))
            config=check_config(cfg,config)
        if not os.path.exists(dst_path):
            os.makedirs(dst_path)
        for child in os.listdir(src_path):
            if child.lower()==WKMAKE_FILENAME:
                continue
            child_src=os.path.join(src_path,child)
            child_dst=os.path.join(dst_path,child)
            make_recursively(child_src,child_dst,config=config,overwrite=overwrite)


def make_from_files(src,dst,config_files,overwrite=False):
    class Config(ConfigBase):
        pass
    for cfg in config_files:
        cfg=load_yaml(cfg)
        Config.update(**cfg)
    make_recursively(src,dst,Config(),overwrite=overwrite)



class ConfigBase:
    pkg_name=None
    python_name=None
    pip_name=None
    author=None
    author_email=None
    author_url=None
    url=None
    remote_url=None
    install_requires=None
    pkg_desc=None
    __required__=['pkg_name']
    def __init__(self):
        self.check_required()

    @classmethod
    def check_required(cls):
        for key in cls.__required__:
            if getattr(cls,key,None) is None:
                print(cls,key)
                raise Exception('Argument %s is required but not given.'%(key))
    @classmethod
    def update(cls,**kwargs):
        for k,v in kwargs.items():
            setattr(cls,k,v)
    @classmethod
    def to_dict(cls,recursive=True):
        if recursive and issubclass(cls.__base__,ConfigBase):
            dic=cls.__base__.to_dict(recursive=recursive)
        else:
            dic={}
        for k,v in cls.__dict__.items():
            if not (k.startswith('__') and k.endswith('__')):
                dic[k]=v
        return dic




