import os
import yaml
import json
from dataclasses import dataclass, field, fields
from typing import List, Dict, Union
import logging
from dotenv import load_dotenv

log = logging.getLogger(__name__)


@dataclass
class ContainerRegistryItem:
    name: str
    image_repo: str
    tag: str = "latest"
    info_link: str = None
    desc: str = None
    image_reg_password: str = None
    image_reg_username: str = None
    is_service_container: bool = False
    env_vars: Dict = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    exlude_in_env: List[str] = field(default_factory=list)
    volumes: Dict = field(default_factory=dict)
    command: Dict = field(default_factory=list)
    sidecars: List["ContainerRegistryItem"] = field(default_factory=list)

    # alpha feature properties. not documented yet. still under review:

    exlude_in_env: List = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "ContainerRegistryItem":
        if (
            not "name" in d
            or not "image_repo" in d
            or d["name"] is None
            or d["image_repo"] is None
        ):
            raise ValueError(
                "Incomplete container description. Expected at least 'name' and 'image_repo'. Got:\n\t{}".format(
                    d
                )
            )
        regitem = cls(d["name"], d["image_repo"])
        for data_field in fields(cls):
            if data_field.name in d:
                if data_field.name == "sidecars":
                    sidecars = []
                    for sidecar_dict in d[data_field.name]:
                        print(sidecar_dict)
                        sidecars.append(cls(**sidecar_dict))
                    setattr(regitem, data_field.name, sidecars)
                else:
                    setattr(regitem, data_field.name, d[data_field.name])

        return regitem

    def get_env_vars(self, extra_envs: Dict):
        all_envs = {}
        for key, val in {**extra_envs, **self.env_vars}.items():
            # add all keys redudant for with a CONFIGS_ prefix to make env vars compatible with https://git.connect.dzd-ev.de/dzdtools/pythonmodules/-/tree/master/Configs
            all_envs[key] = val
            all_envs["CONFIGS_{}".format(key)] = val
        return all_envs


class ContainerRegistry:
    DATALOADER_BLOCK_LIST: List = None
    DATALOADER_ALLOW_LIST: List = None
    global_env_vars: dict = None

    name = None

    def __init__(self, data: str, env_file_path: str):
        """[summary]

        Args:
            data (str): File path to yaml or json file OR yaml or json string OR dict
            env_vars (str): File path to a .env file
        """
        self.global_env_vars = {}
        self.parse_dot_env(env_file_path)
        self.data = self.parse_data(data)

    def add_global_env(self, key, value):
        log.debug("Add global env '{}' with value '{}'".format(key, value))
        self.global_env_vars[key] = value
        # redudant entry with "CONFIGS_" prefix to support https://git.connect.dzd-ev.de/dzdtools/pythonmodules/-/tree/master/Configs
        if not key.startswith("CONFIGS_"):
            self.global_env_vars["CONFIGS_".format(key)] = value

    def parse_dot_env(self, env_path):
        if not os.path.isfile(env_path):
            log.warning(
                "Can not find a .env file at '{}'. Will skip .env file parsing.".format(
                    os.path.abspath(env_path)
                )
            )
            return
        # load into system envs to have affect while pipeline description parsing
        load_dotenv(dotenv_path=env_path)
        # add these env vars to global env list to be able to pass them into the pipeline children
        with open(env_path) as f:
            for line in f:
                # skip comments, empty lines, broken lines
                if line.startswith("#") or not line.strip() or "=" not in line:
                    continue
                key, value = line.strip().split("=", 1)
                self.add_global_env(key, value)

    def parse_data(self, data) -> List[ContainerRegistryItem]:
        payload = None
        if os.path.isfile(data):
            # we have a json or yaml file
            with open(data, "r") as file:
                payload = "".join(file.readlines())
        elif isinstance(data, str):
            # we have a json or yaml str
            payload = data
        elif isinstance(payload, list):
            d = data
        if payload is not None:
            # Try to parse as yaml. if this failes try to parse a json
            try:
                d = yaml.load(payload, Loader=yaml.FullLoader)
            except Exception as ye:
                try:
                    d = json.load(payload)[list(d.keys())[0]]
                except Exception as je:
                    raise RegistrySourceInvalidEx(
                        "Registry source is not a valid dict, json or yaml file or string.\nYaml parsing error:{}\nJson parsing error:{}".format(
                            ye, je
                        )
                    )
            self.name = list(d.keys())[0]
            d = d[self.name]
            d = self._expand_reg_data_env_vars(d)
            log.debug("Expanded Pipeline:\n{}".format(json.dumps(d, indent=4)))
        registry_item_list = []
        for regitem_dict in d:
            registry_item_list.append(ContainerRegistryItem.from_dict(regitem_dict))
        return registry_item_list

    def _expand_reg_data_env_vars(self, data: Union[Dict, List]) -> Union[Dict, List]:
        # replace all env vars strings (e.g. $MYENVVAR, ${MY_OTHER_ENV_VAR}) by their actual value
        expanded_data = None
        if isinstance(data, list):
            expanded_data = []
            for item in data:
                if isinstance(item, (dict, list)):
                    expanded_data.append(self._expand_reg_data_env_vars(item))
                elif isinstance(item, str):
                    expanded_data.append(os.path.expandvars(item))
                else:
                    expanded_data.append(item)
        elif isinstance(data, dict):
            expanded_data = {}
            for key, val in data.items():

                expanded_key = os.path.expandvars(key)
                if expanded_key != key:
                    log.debug("EXPAND KEY:'{}' -> '{}'".format(key, expanded_key))
                expanded_data[expanded_key] = val
                if isinstance(val, (dict, list)):
                    expanded_data[expanded_key] = self._expand_reg_data_env_vars(val)
                elif isinstance(val, str):
                    new_val = os.path.expandvars(val)
                    if new_val != val:
                        log.debug("EXPAND VALUE:'{}' -> '{}'".format(val, new_val))
                    expanded_data[expanded_key] = new_val
                else:
                    expanded_data[expanded_key] = val
        else:
            raise ValueError("Expected dict or list got {}".format(type(data)))
        return expanded_data

    def get_ordered_containers(self, service_containers_only=False):
        """Returns the container registry sorted by dependencies and filters out reg_items not relevant for the current environment"""
        sorted_reg_items = []
        current_env = os.getenv("ENV", None)
        reg_items_unsorted = self.data

        if self.DATALOADER_BLOCK_LIST and self.DATALOADER_ALLOW_LIST:
            raise ValueError(
                "'DATALOADER_BLOCK_LIST' and 'DATALOADER_ALLOW_LIST' can not be used concurrent. Set one to 'None' or '[]'"
            )
        elif self.DATALOADER_BLOCK_LIST:
            # filter out non listed reg_items
            reg_items_unsorted = [
                reg_item
                for reg_item in reg_items_unsorted
                if reg_item.name not in self.DATALOADER_BLOCK_LIST
            ]
        elif self.DATALOADER_ALLOW_LIST:
            reg_items_unsorted = [
                reg_item
                for reg_item in reg_items_unsorted
                if reg_item.name in self.DATALOADER_ALLOW_LIST
            ]

        def add_data_source(reg_item):
            for index, dep in enumerate(reg_item.dependencies):
                try:
                    add_data_source(
                        next(
                            r_item
                            for r_item in reg_items_unsorted
                            if r_item.name == dep
                        )
                    )
                except StopIteration:
                    log.warning(
                        "Unknown dependency '{}' declared for '{}'. Please check your pipeline defintion. The dependency will be ignored...".format(
                            dep, reg_item.name
                        )
                    )
            if (
                next(
                    (
                        r_item
                        for r_item in sorted_reg_items
                        if r_item.name == reg_item.name
                    ),
                    None,
                )
                is None
                and current_env not in reg_item.exlude_in_env
            ):
                if not service_containers_only or (
                    service_containers_only and reg_item.is_service_container
                ):
                    sorted_reg_items.append(reg_item)

        for r_item in reg_items_unsorted:
            add_data_source(r_item)
        return sorted_reg_items


class RegistrySourceInvalidEx(Exception):
    pass
