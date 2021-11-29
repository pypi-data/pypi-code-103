# -*- coding: utf-8 -*-
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import timeit
from typing import Iterable, List, Optional, Tuple, cast, Union

import pandas as pd

from gordo_dataset.file_system.base import FileSystem
from gordo_dataset.sensor_tag import SensorTag, Tag
from gordo_dataset.utils import capture_args
from gordo_dataset.assets_config import AssetsConfig

from .base import GordoBaseDataProvider
from .ncs_contants import NCS_READER_NAME
from .ncs_file_type import load_ncs_file_types, DEFAULT_TYPE_NAMES
from .ncs_lookup import NcsLookup, TagLocations
from .constants import DEFAULT_MAX_FILE_SIZE
from .partition import PartitionBy, split_by_partitions, Partition

from ..exceptions import ConfigException

logger = logging.getLogger(__name__)


class NcsReader(GordoBaseDataProvider):
    @capture_args
    def __init__(
        self,
        storage: FileSystem,
        assets_config: AssetsConfig,
        threads: Optional[int] = 1,
        remove_status_codes: Optional[list] = [0, 64, 60, 8, 24, 3, 32768],
        dl_base_path: Optional[str] = None,
        lookup_for: Optional[List[str]] = None,
        storage_name: Optional[str] = None,
        ncs_lookup: Optional[NcsLookup] = None,
        max_file_size: Optional[int] = DEFAULT_MAX_FILE_SIZE,
        partition_by: Union[str, PartitionBy] = PartitionBy.MONTH,
        **kwargs,  # Do not remove this
    ):
        """
        Creates a reader for tags from the Norwegian Continental Shelf. Currently
        only supports a small subset of assets.

        Parameters
        ----------
        storage: FileSystem
            Storage file system
        assets_config: AssetsConfig
            Assets config
        threads : Optional[int]
            Number of threads to use. If None then use 1 thread
        remove_status_codes: Optional[list]
            Removes data with Status code(s) in the list. By default it removes data
            with Status code 0.
        dl_base_path: Optional[str]
            Base bath used to override the asset to path dictionary. Useful for demos
            and other non-production settings.
        lookup_for:  Optional[List[str]]
            List of file finders by the file type name. Value by default: ``['parquet', 'yearly_parquet', 'csv']``
        storage_name: Optional[str]
            Used by ``AssetsConfig``
        ncs_lookup: Optional[NcsLookup]
            Creates with current ``storage``, ``storage_name`` and ``lookup_for`` if None
        max_file_size: Optional[int]
            Maximal file size
        partition_by: Union[str, PartitionBy]
            Partition by year or month. Default: "month"

        Notes
        -----
        `lookup_for` provide list sorted by priority. It means that for value ``['csv', 'parquet']``
        the reader will prefer to find CSV files over Parquet

        """
        self.storage = storage
        self.assets_config = assets_config

        self.threads = threads
        self.remove_status_codes = remove_status_codes
        self.dl_base_path = dl_base_path

        if lookup_for is None:
            lookup_for = DEFAULT_TYPE_NAMES
        self.lookup_for = lookup_for
        if storage_name is None:
            storage_name = storage.name
        self.storage_name: str = storage_name
        if ncs_lookup is None:
            ncs_lookup = self.create_ncs_lookup(assets_config, max_file_size)
        elif not isinstance(ncs_lookup, NcsLookup):
            raise ConfigException("ncs_lookup should be instance of NcsLookup")
        self.ncs_lookup = ncs_lookup
        self.partition_by = self.prepare_partition_by(partition_by)
        logger.info(f"Starting NCS reader with {self.threads} threads")

    @staticmethod
    def prepare_partition_by(partition_by: Union[str, PartitionBy]) -> PartitionBy:
        result: Optional[PartitionBy]
        if isinstance(partition_by, str):
            result = PartitionBy.find_by_name(partition_by)
            if result is None:
                raise ConfigException("Wrong partition_by argument '%s'" % partition_by)
        else:
            result = partition_by
        return cast(PartitionBy, result)

    def create_ncs_lookup(
        self, assets_config: AssetsConfig, max_file_size: Optional[int]
    ) -> NcsLookup:
        ncs_file_types = load_ncs_file_types(self.lookup_for)
        return NcsLookup(
            self.storage,
            assets_config,
            ncs_file_types,
            self.storage_name,
            max_file_size=max_file_size,
        )

    @property
    def reader_name(self) -> str:
        """
        Property used for validating result of `AssetsConfig.get_path()`
        """
        return NCS_READER_NAME

    def can_handle_tag(self, tag: Union[str, SensorTag]):
        """
        Implements GordoBaseDataProvider, see base class for documentation
        """
        # TODO do something better here
        return True

    @staticmethod
    def filter_series(
        series: pd.Series,
        train_start_date: datetime,
        train_end_date: datetime,
    ) -> Iterable[pd.Series]:
        return series[
            (series.index >= train_start_date) & (series.index < train_end_date)
        ]

    def load_series(
        self,
        train_start_date: datetime,
        train_end_date: datetime,
        tag_list: List[Union[str, SensorTag]],
        dry_run: Optional[bool] = False,
        **kwargs,
    ) -> Iterable[Tuple[pd.Series, Tag]]:
        """
        See GordoBaseDataProvider for documentation
        """
        if train_end_date < train_start_date:
            raise ValueError(
                f"NCS reader called with train_end_date: {train_end_date} before train_start_date: {train_start_date}"
            )

        partitions = list(
            split_by_partitions(self.partition_by, train_start_date, train_end_date)
        )

        tag_lookups = self.ncs_lookup.assets_config_tags_lookup(
            tag_list, self.dl_base_path
        )

        if self.threads:
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                fetched_tags = executor.map(
                    lambda arg: self._load_series_mapper(
                        arg[0], arg[1], partitions, dry_run
                    ),
                    tag_lookups,
                )
                for series, tag in fetched_tags:
                    yield self.filter_series(
                        series, train_start_date, train_end_date
                    ), tag
        else:
            for tag_name, path_with_tag in tag_lookups:
                series, tag = self._load_series_mapper(
                    tag_name, path_with_tag, partitions, dry_run
                )
                yield self.filter_series(series, train_start_date, train_end_date), tag

    def _load_series_mapper(
        self,
        tag_name: str,
        path_with_tag: Optional[Tuple[str, SensorTag]],
        partitions: List[Partition],
        dry_run: Optional[bool] = False,
    ) -> Tuple[pd.Series, Tag]:
        if path_with_tag is None:
            logger.info(
                "Unable to find tag '%s' (asset '%s') directory in storage '%s'",
                tag_name,
                self.storage_name,
            )
            return pd.Series(), tag_name
        tag_dir, tag = path_with_tag
        tag_locations = self.ncs_lookup.files_lookup(tag_dir, tag, partitions)
        return self.read_tag_locations(tag_locations, dry_run), tag

    def read_tag_locations(
        self, tag_locations: TagLocations, dry_run: Optional[bool] = False
    ) -> pd.Series:
        """
        Reads all data from files in ``tag_locations``

        Parameters
        ----------
        tag_locations: TagLocations
        dry_run: bool

        Returns
        -------
        pd.Series

        """
        tag = tag_locations.tag
        partitions = tag_locations.partitions()

        all_partitions = []
        logger.info(f"Downloading tag: {tag} for partitions: {partitions}")
        for tag, partition, location in tag_locations:
            file_path = location.path
            file_type = location.file_type
            logger.info(f"Parsing file {file_path} from partition {partition}")

            try:
                info = self.storage.info(file_path)
                file_size = info.size / (1024 ** 2)
                logger.debug(f"File size for file {file_path}: {file_size:.2f}MB")

                if dry_run:
                    logger.info("Dry run only, returning empty frame early")
                    return pd.Series()
                before_downloading = timeit.default_timer()
                with self.storage.open(file_path, "rb") as f:
                    df = file_type.read_df(f)
                    df = df.rename(columns={"Value": tag.name})
                    df = df[~df["Status"].isin(self.remove_status_codes)]
                    df.sort_index(inplace=True)
                    all_partitions.append(df)
                    logger.info(
                        f"Done in {(timeit.default_timer()-before_downloading):.2f} sec {file_path}"
                    )

            except FileNotFoundError as e:
                logger.debug(f"{file_path} not found, skipping it: {e}")

        try:
            combined = pd.concat(all_partitions)
        except Exception as e:
            logger.debug(f"Not able to concatinate all partitions: {e}.")
            return pd.Series(name=tag.name, data=[])

            # There often comes duplicated timestamps, keep the last
        if combined.index.duplicated().any():
            combined = combined[~combined.index.duplicated(keep="last")]

        return combined[tag.name]

    @staticmethod
    def _verify_tag_path_exist(fs: FileSystem, path: str):
        """
        Verify that the tag path exists, if not the `fs.info` will raise a FileNotFound error.

        Parameters
        ----------
        fs: FileSystem
            File system
        path : str
            Path of tag to be checked if exists.
        """
        fs.info(path)
