import os
from typing import Union, Any, Dict
from collections import OrderedDict
from pathlib import Path
from easydict import EasyDict as edict
from ruamel.yaml import YAML, yaml_object
from jais.__init__ import ROOT_DIR

__all__ = [
    # JSON
    'load_json', 'save_json',

    # YAML
    'load_yaml', 'save_yaml',
]


# ----------------------------------------> JSON :
def load_json(path: Union[str, Path]) -> edict:
    """Load .json file from given path"""
    import json
    with open(path) as f:
        return edict(json.load(f))


def save_json(object: Any, path: Union[str, Path]) -> None:
    """Save .json file to given path"""
    import json
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(path), 'w') as f:
        json.dump(object, f)


# ----------------------------------------> YAML :
# * When using the decorator, which takes the YAML() instance as a parameter,
# * the yaml = YAML() line needs to be moved up in the file -- *yaml docs*
yaml = YAML(typ='safe', pure=True)
yaml.default_flow_style = False
yaml.indent(mapping=2, sequence=4, offset=2)


@yaml_object(yaml)
class JoinPath:
    """Custom tag `!join` loader class to join strings for yaml file."""

    yaml_tag = u'!joinpath'

    def __init__(self, joined_string):
        self.joined_string = joined_string

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.joined_string}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        seq = constructor.construct_sequence(node)
        fullpath = Path(os.path.join(*[str(i) for i in seq])).resolve()
        return str(fullpath)


@yaml_object(yaml)
class RootDirSetter:
    """Custom tag `!rootdir` loader class for yaml file."""

    yaml_tag = u'!rootdir'

    def __init__(self, path):
        self.path = path

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.path}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        return str(ROOT_DIR)


@yaml_object(yaml)
class CWDSetter:
    """Custom tag `!cwd` loader class for yaml file."""

    yaml_tag = u'!cwd'  # Current Working Directory

    def __init__(self, path):
        self.path = path

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.path}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        return load_json(ROOT_DIR/'configs/jais_settings.json').JAIS_CWD


@yaml_object(yaml)
class HomeDirSetter:
    """Custom tag `!homedir` loader class for yaml file."""

    yaml_tag = u'!homedir'

    def __init__(self, path):
        self.path = path

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            u'{.path}'.format(node))

    @classmethod
    def from_yaml(cls, constructor, node):
        return str(Path.home())


def load_yaml(path: Union[str, Path], pure: bool = False) -> dict:
    """config.yaml file loader.

    This function converts the config.yaml file to `dict` object.

    Args:
        path: .yaml configuration filepath
        pure: If True, just load the .yaml without converting to EasyDict
            and exclude extra info.

    Returns:
        `dict` object containing configuration parameters.

    Example:
        .. code-block:: python

            config = load_yaml("../config.yaml")
            print(config["project_name"])
    """

    path = str(Path(path).absolute().resolve())
    # * Load config file
    with open(path) as file:
        config = yaml.load(file)

    if pure == False:  # Add extra features
        # Convert dict to easydict
        config = edict(config)
    return config


def save_yaml(config_dict: Dict, path: Union[str, Path] = None,
                saveas_ordered: bool = True, force_overwrite: bool = False,
                file_extension: str = 'yaml') -> None:
    """save `dict` config parameters to `.yaml` file

    Args:
        config_dict: parameters to save.
        path: path/to/save/auto_config.yaml.
        saveas_ordered: save as collections.OrderedDict on Python 3 and 
            `!!omap` is generated for these types.
        file_extension: default `.yaml`

    Returns: 
        nothing

    Example:
        .. code-block:: python

            config = {"Example": 10}
            save_config(config, "../auto_config.yaml")
    """

    if path is None:  # set default path if not given
        path = config_dict.paths.output_dir
        path = f"{path}/modified_config.{file_extension}"
    else:
        path = str(Path(path).absolute().resolve())
        # Check if the path given is the original config's path
        if (config_dict.original_config_filepath == path) and \
           (not force_overwrite):
            msg = f"""
            Error while saving config file @ {path}.
            Cannot overwrite the original config file
            Choose different save location.
            """
            raise ValueError(msg)

    # converting easydict format to default dict because
    # YAML does not processes EasyDict format well.
    cleaned_dict = {
        k: edict_to_dict_converter(v)
        for k, v in config_dict.items()
    }
    # print("cleaned_dict =", cleaned_dict)

    # Fix order
    if saveas_ordered:
        cleaned_dict = OrderedDict(cleaned_dict)

    # Save the file to given location
    with open(path, 'w') as file:
        yaml.dump(cleaned_dict, file)

    print(f"config saved @ {path}")


def edict_to_dict_converter(x: Union[Dict, Any]) -> Union[Dict, Any]:
    """Recursive function to convert given dictionary's datatype
    from edict to dict.

    Args:
        x (dict or other): nested dictionary

    Returns: x (same x but default dict type)
    """
    if not isinstance(x, dict):
        return x

    # Recursion for nested dicts
    ndict = {}
    for k, v in x.items():
        v1 = edict_to_dict_converter(v)
        ndict[k] = v1
    return ndict
