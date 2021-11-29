import yaml
import re

from typing import Optional, Dict, IO, List, Pattern, Tuple, Set, Any, Union
from dataclasses import dataclass

from .exceptions import ConfigException
from .file_system.base import FileSystem

from pydantic import BaseModel, ValidationError
from collections import defaultdict


class AssetsModel(BaseModel):
    aliases: Dict[str, str]


class PathAsset(BaseModel):
    path: str
    asset: str


class StorageAsset(BaseModel):
    name: str
    tag_pattern: Optional[str]
    path: str
    additional_directory_patterns: Optional[List[str]]


class StorageItems(BaseModel):
    base_dir: str
    assets: List[StorageAsset]


class ConfigModel(BaseModel):
    assets: Optional[AssetsModel] = None
    storages: Dict[str, List[StorageItems]]


@dataclass(frozen=True)
class PathSpec:
    asset: str
    base_dir: str
    path: str
    tag_pattern: Optional[Pattern] = None
    additional_directory_patterns: Optional[List[Pattern]] = None

    def full_path(self, fs: FileSystem) -> str:
        return fs.join(self.base_dir, self.path)


def pydantic_loc_to_json_path(loc: Tuple[Union[int, str], ...]) -> str:
    if len(loc):
        json_paths = []
        for v in loc:
            format_str = "[%d]" if type(v) is int else ".%s"
            json_paths.append(format_str % v)
        json_path = "".join(json_paths)
        return json_path if json_path[0] == "." else "." + json_path
    return ""


def exception_message(message: str, file_path: Optional[str] = None) -> str:
    if file_path:
        return message + ". Config path: %s" % file_path
    else:
        return message


def validation_error_exception_message(errors: List[Dict[str, Any]]) -> str:
    error_messages = []
    for error in errors:
        error_messages.append(
            "%s in '%s'" % (error["msg"], pydantic_loc_to_json_path(error["loc"]))
        )
    message = "Validation error%s: %s" % (
        "" if len(errors) <= 1 else "s",
        "; ".join(error_messages),
    )
    return message


WithPattern = Dict[str, List[Tuple[Pattern, PathSpec]]]
WithoutPattern = Dict[str, List[PathSpec]]
ByAssets = Dict[str, Dict[str, List[PathSpec]]]


class AssetsConfig:
    @classmethod
    def load_from_yaml(
        cls, f: IO[str], file_path: Optional[str] = None
    ) -> "AssetsConfig":
        """
        Loading AssetsConfig from YAML file

        Parameters
        ----------
        f: IO[str]
            File object
        file_path
            Source file path. Using only for exception messages

        Returns
        -------

        """
        raw_config = yaml.safe_load(f)
        return cls.load(raw_config, file_path=file_path)

    @classmethod
    def load(cls, raw_config: dict, file_path: Optional[str] = None) -> "AssetsConfig":
        """
        Loading AssetsConfig from a dictionary. See ``load_from_yaml`` method for loading from YAML file

        Examples
        --------
        >>> raw_config = {'storages': {'adlstore': [{'assets': [{'name': 'asset1',
        ...                             'tag_pattern': '^tag1',
        ...                             'path': 'path/to/asset1'},
        ...                            {'name': 'asset2',
        ...                             'path': 'path/to/asset2'}],
        ...                  'base_dir': '/ncs_data'
        ...                  }]}}
        >>> config = AssetsConfig.load(raw_config)
        >>> config.get_paths("adlstore", "tag11")
        [PathSpec(asset='asset1', base_dir='/ncs_data', path='path/to/asset1', tag_pattern=re.compile('^tag1', re.IGNORECASE), additional_directory_patterns=None)]
        >>> config.get_paths("adlstore", "tag22", "asset2")
        [PathSpec(asset='asset2', base_dir='/ncs_data', path='path/to/asset2', tag_pattern=None, additional_directory_patterns=None)]

        Parameters
        ----------
        raw_config: dict
            Config source
        file_path
            Source file path. Using only for exception messages


        Returns
        -------
        AssetsConfig

        """
        try:
            config = ConfigModel(**raw_config)
        except ValidationError as e:
            message = validation_error_exception_message(e.errors())
            raise ConfigException(exception_message(message, file_path))
        storages = {}
        for storage, storage_items in config.storages.items():
            path_specs: List[PathSpec] = []
            for storage_item in storage_items:
                paths_set: Set[Tuple[str, str]] = set()
                base_dir = storage_item.base_dir
                for storage_asset in storage_item.assets:
                    path = storage_asset.path
                    key = (base_dir, path)
                    if key in paths_set:
                        message = (
                            f"Found duplicate path in storage '{storage}' with base "
                            f"dir '{base_dir}', and path '{path}'"
                        )
                        raise ConfigException(message)
                    name = storage_asset.name
                    tag_pattern = None
                    if storage_asset.tag_pattern:
                        try:
                            tag_pattern = re.compile(
                                storage_asset.tag_pattern, re.IGNORECASE
                            )
                        except re.error as e:
                            error = str(e)
                            message = (
                                f"Unable to compile tag_pattern in storage '{storage}' with base "
                                f"dir '{base_dir}', and path '{path}', because: {error}"
                            )
                            raise ConfigException(message)
                    additional_directory_patterns: Optional[List[Pattern]] = None
                    if storage_asset.additional_directory_patterns is not None:
                        additional_directory_patterns = []
                        for pattern in storage_asset.additional_directory_patterns:
                            try:
                                additional_directory_patterns.append(
                                    re.compile(pattern, re.IGNORECASE)
                                )
                            except re.error as e:
                                message = (
                                    f"Unable to compile addition_directory_pattern '{pattern}' "
                                    f"in storage '{storage}' with base "
                                    f"dir '{base_dir}', and path '{path}', because: {str(e)}"
                                )
                                raise ConfigException(message)
                    path_spec = PathSpec(
                        name,
                        base_dir,
                        storage_asset.path,
                        tag_pattern,
                        additional_directory_patterns,
                    )
                    path_specs.append(path_spec)
                    paths_set.add(key)
            storages[storage] = path_specs
        assets_aliases: Optional[Dict[str, str]] = None
        if config.assets is not None:
            assets_aliases = config.assets.aliases
        return cls(storages, assets_aliases)

    def __init__(
        self,
        storages: Dict[str, List[PathSpec]],
        assets_aliases: Optional[Dict[str, str]] = None,
    ):
        self.storage_names = set(storages.keys())
        self.with_pattern, self.without_pattern, self.by_assets = self.prepare(storages)
        self.assets_aliases = assets_aliases

    @staticmethod
    def prepare(
        storages: Dict[str, List[PathSpec]]
    ) -> Tuple[WithPattern, WithoutPattern, ByAssets]:
        with_pattern: WithPattern = defaultdict(list)
        without_pattern: WithoutPattern = defaultdict(list)
        by_assets: ByAssets = defaultdict(dict)
        for storage, path_specs in storages.items():
            storage_by_asset = by_assets[storage]
            for path_spec in path_specs:
                asset = path_spec.asset
                if asset not in storage_by_asset:
                    storage_by_asset[asset] = []
                storage_by_asset[asset].append(path_spec)
                if path_spec.tag_pattern:
                    with_pattern[storage].append((path_spec.tag_pattern, path_spec))
                else:
                    without_pattern[storage].append(path_spec)
        return with_pattern, without_pattern, by_assets

    def prepare_asset_name(self, asset: str) -> str:
        if self.assets_aliases is not None:
            return self.assets_aliases.get(asset, asset)
        return asset

    def get_paths(
        self,
        storage: str,
        tag: str,
        asset: Optional[str] = None,
    ) -> List[PathSpec]:
        """
        Tries to find tag corresponded path in the config

        Parameters
        ----------
        storage
            Storage name. For Azure Data Lake Gen2 <container name>@<storage account>
        tag
            Tag name
        asset
            Asset name if known. If None will be determined through tag_patterns in the config

        Returns
        -------
        List[PathSpec]

        """
        path_specs: List[PathSpec] = []
        if storage in self.storage_names:
            if asset is not None:
                asset = self.prepare_asset_name(asset)
                if storage in self.by_assets:
                    path_specs = self.by_assets[storage].get(asset, [])
            else:
                if storage in self.with_pattern:
                    for tag_pattern, path_spec in self.with_pattern[storage]:
                        if tag_pattern.match(tag):
                            path_specs.append(path_spec)
                if not path_specs:
                    path_specs = self.without_pattern.get(storage, [])
        return path_specs
