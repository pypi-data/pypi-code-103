# -*- coding: utf-8 -*-
import logging
import inject

from typing import Tuple, List, Dict, Optional, Iterable, Callable, Sequence, Set, cast
from datetime import datetime
from dateutil.parser import isoparse
from functools import wraps
from typing import Union

import pandas as pd
import numpy as np

from .data_provider.providers import RandomDataProvider, DataLakeProvider
from .exceptions import InsufficientDataError
from .base import GordoBaseDataset, ConfigurationError
from .data_provider.base import GordoBaseDataProvider
from .filter_rows import pandas_filter_rows, parse_pandas_filter_vars
from .filter_periods import FilterPeriods
from .sensor_tag import (
    SensorTag,
    Tag,
    extract_tag_name,
    normalize_sensor_tag,
    unique_tag_names,
)
from .utils import capture_args_ext, capture_args, join_timeseries
from .dataset_metadata import (
    tags_to_json_representation,
    sensor_tags_from_build_metadata,
)
from .assets_config import AssetsConfig
from .resource_assets_config import load_assets_config
from .validators import (
    ValidTagList,
    ValidDatetime,
    ValidDatasetKwargs,
    ValidDataProvider,
)

logger = logging.getLogger(__name__)


def compat(init):
    """
    __init__ decorator for compatibility where the Gordo config file's ``dataset`` keys have
    drifted from what kwargs are actually expected in the given dataset. For example,
    using `train_start_date` is common in the configs, but :class:`~TimeSeriesDataset`
    takes this parameter as ``train_start_date``, as well as :class:`~RandomDataset`

    Renames old/other acceptable kwargs to the ones that the dataset type expects
    """

    @wraps(init)
    def wrapper(*args, **kwargs):
        renamings = {
            "from_ts": "train_start_date",
            "to_ts": "train_end_date",
            "tags": "tag_list",
        }
        for old, new in renamings.items():
            if old in kwargs:
                kwargs[new] = kwargs.pop(old)
        return init(*args, **kwargs)

    return wrapper


TagList = List[Union[Dict, str, SensorTag]]


class TimeSeriesDataset(GordoBaseDataset):

    train_start_date = ValidDatetime()
    train_end_date = ValidDatetime()
    tag_list = ValidTagList()
    target_tag_list = ValidTagList()
    data_provider = ValidDataProvider()
    kwargs = ValidDatasetKwargs()

    @staticmethod
    def create_default_data_provider() -> GordoBaseDataProvider:
        return DataLakeProvider()

    @staticmethod
    def tag_normalizer(
        assets_config: AssetsConfig,
        sensors: TagList,
        asset: str = None,
    ) -> List[Union[str, SensorTag]]:
        """
        Prepare and validate sensors list.
        This function might be useful for overwriting in the extended class
        """
        tag_list = [
            normalize_sensor_tag(assets_config, sensor, asset) for sensor in sensors
        ]
        unique_tag_names(tag_list)
        return tag_list

    @compat
    @capture_args_ext(ignore=["assets_config"])
    @inject.params(assets_config=AssetsConfig)
    def __init__(
        self,
        train_start_date: Union[datetime, str],
        train_end_date: Union[datetime, str],
        tag_list: Sequence[Union[str, Dict, SensorTag]],
        target_tag_list: Optional[Sequence[Union[str, Dict, SensorTag]]] = None,
        data_provider: Optional[Union[GordoBaseDataProvider, dict]] = None,
        assets_config: Optional[AssetsConfig] = None,
        resolution: Optional[str] = "10T",
        row_filter: Union[str, list] = "",
        known_filter_periods: Optional[list] = None,
        aggregation_methods: Union[str, List[str], Callable] = "mean",
        row_filter_buffer_size: int = 0,
        asset: Optional[str] = None,
        n_samples_threshold: int = 0,
        low_threshold: Optional[int] = -1000,
        high_threshold: Optional[int] = 50000,
        interpolation_method: str = "linear_interpolation",
        interpolation_limit: str = "8H",
        filter_periods: Optional[Union[dict, FilterPeriods]] = None,
        **kwargs,
    ):
        """
        Creates a TimeSeriesDataset backed by a provided dataprovider.

        A TimeSeriesDataset is a dataset backed by timeseries, but resampled,
        aligned, and (optionally) filtered.

        Parameters
        ----------
        train_start_date: Union[datetime, str]
            Earliest possible point in the dataset (inclusive)
        train_end_date: Union[datetime, str]
            Earliest possible point in the dataset (exclusive)
        tag_list: Sequence[Union[str, Dict, sensor_tag.SensorTag]]
            List of tags to include in the dataset. The elements can be strings,
            dictionaries or SensorTag namedtuples.
        target_tag_list: Sequence[List[Union[str, Dict, sensor_tag.SensorTag]]]
            List of tags to set as the dataset y. These will be treated the same as
            tag_list when fetching and pre-processing (resampling) but will be split
            into the y return from ``.get_data()``
        data_provider: Union[GordoBaseDataProvider, dict]
            A dataprovider which can provide dataframes for tags from train_start_date to train_end_date
            of which can also be a config definition from a data provider's ``.to_dict()`` method.
        assets_config: Optional[AssetsConfig]
            Assets config for determining tags assets
        resolution: Optional[str]
            The bucket size for grouping all incoming time data (e.g. "10T").
            Available strings come from https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects
            **Note**: If this parameter is ``None`` or ``False``, then _no_ aggregation/resampling is applied to the data.
        row_filter: str or list
            Filter on the rows. Only rows satisfying the filter will be in the dataset.
            See :func:`gordo_dataset.filter_rows.pandas_filter_rows` for
            further documentation of the filter format.
        known_filter_periods: list
            List of periods to drop in the format [~('2020-04-08 04:00:00+00:00' < index < '2020-04-08 10:00:00+00:00')].
            Note the time-zone suffix (+00:00), which is required.
        aggregation_methods
            Aggregation method(s) to use for the resampled buckets. If a single
            resample method is provided then the resulting dataframe will have names
            identical to the names of the series it got in. If several
            aggregation-methods are provided then the resulting dataframe will
            have a multi-level column index, with the series-name as the first level,
            and the aggregation method as the second level.
            See :py:func::`pandas.core.resample.Resampler#aggregate` for more
            information on possible aggregation methods.
        row_filter_buffer_size: int
            Whatever elements are selected for removal based on the ``row_filter``, will also
            have this amount of elements removed fore and aft.
            Default is zero 0
        asset: Optional[str]
            Asset for which the tags are associated with.
        n_samples_threshold: int = 0
            The threshold at which the generated DataFrame is considered to have too few rows of data.
        interpolation_method: str
            How should missing values be interpolated. Either forward fill (`ffill`) or by linear
            interpolation (default, `linear_interpolation`).
        interpolation_limit: str
            Parameter sets how long from last valid data point values will be interpolated/forward filled.
            Default is eight hours (`8H`).
            If None, all missing values are interpolated/forward filled.
        fiter_periods: dict
            Performs a series of algorithms that drops noisy data is specified.
            See `filter_periods` class for details.
        kwargs
            Deprecated arguments
        """
        self.train_start_date = self._validate_dt(train_start_date)
        self.train_end_date = self._validate_dt(train_end_date)

        if self.train_start_date >= self.train_end_date:
            raise ValueError(
                f"train_end_date ({self.train_end_date}) must be after train_start_date ({self.train_start_date})"
            )

        self.asset = asset
        if assets_config is None:
            assets_config = load_assets_config()
        self.assets_config = cast(AssetsConfig, assets_config)

        self.tag_list = self.tag_normalizer(self.assets_config, list(tag_list), asset)
        self.target_tag_list = (
            self.tag_normalizer(self.assets_config, list(target_tag_list), asset)
            if target_tag_list
            else self.tag_list.copy()
        )
        self.resolution = resolution
        if data_provider is None:
            data_provider = self.create_default_data_provider()
        self.data_provider = (
            data_provider
            if not isinstance(data_provider, dict)
            else GordoBaseDataProvider.from_dict(data_provider)
        )
        self.row_filter = row_filter
        self.aggregation_methods = aggregation_methods
        self.row_filter_buffer_size = row_filter_buffer_size
        self.n_samples_threshold = n_samples_threshold
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.interpolation_method = interpolation_method
        self.interpolation_limit = interpolation_limit
        self.filter_periods: Optional[FilterPeriods] = None
        if filter_periods:
            if isinstance(filter_periods, dict):
                self.filter_periods = FilterPeriods(
                    granularity=self.resolution, **filter_periods
                )
            else:
                self.filter_periods = cast(Optional[FilterPeriods], filter_periods)
        self.known_filter_periods = (
            known_filter_periods if known_filter_periods is not None else []
        )

        if not self.train_start_date.tzinfo or not self.train_end_date.tzinfo:
            raise ValueError(
                f"Timestamps ({self.train_start_date}, {self.train_end_date}) need to include timezone "
                f"information"
            )

        for name, value in kwargs.items():
            logger.error(
                "Deprecated argument %s=%s provided for %s",
                name,
                value,
                self.__class__.__name__,
            )

        super().__init__()

    def to_dict(self):
        params = super().to_dict()
        to_str = lambda dt: str(dt) if not hasattr(dt, "isoformat") else dt.isoformat()
        params["train_start_date"] = to_str(params["train_start_date"])
        params["train_end_date"] = to_str(params["train_end_date"])
        return params

    @staticmethod
    def _validate_dt(dt: Union[str, datetime]) -> datetime:
        dt = dt if isinstance(dt, datetime) else isoparse(dt)
        if dt.tzinfo is None:
            raise ValueError(
                "Must provide an ISO formatted datetime string with timezone information"
            )
        return dt

    def _get_tag_list(
        self,
        row_filter: Union[str, list],
        tag_list: List[Tag],
        target_tag_list: List[Tag],
    ) -> Tuple[List[Union[str, SensorTag]], List[Union[str, SensorTag]]]:
        # TODO better docstring
        tags = set(tag_list + target_tag_list)

        triggered_tags = set()
        if row_filter:
            pandas_filter_tags = set(
                self.tag_normalizer(
                    self.assets_config,
                    cast(TagList, parse_pandas_filter_vars(self.row_filter)),
                    self.asset,
                )
            )
            triggered_tags = pandas_filter_tags.difference(tag_list)
            tags.update(triggered_tags)
        return list(tags), list(triggered_tags)

    def _join_timeseries(
        self,
        series_iter: Iterable[Tuple[pd.Series, Tag]],
        process_metadata: bool = True,
    ) -> pd.DataFrame:
        # TODO better docstring
        # Resample if we have a resolution set, otherwise simply join the series.
        if self.resolution:
            data, metadata = join_timeseries(
                series_iter,
                self.train_start_date,
                self.train_end_date,
                self.resolution,
                aggregation_methods=self.aggregation_methods,
                interpolation_method=self.interpolation_method,
                interpolation_limit=self.interpolation_limit,
            )
        else:
            series_list, tags = [], []
            for series, tag in series_iter:
                series_list.append(series)
                tags.append(tag)
            data = pd.concat(series_list, axis=1, join="inner")
            metadata = {"tags": tags_to_json_representation(tags)}
        if process_metadata:
            self._metadata["tag_loading_metadata"] = metadata
        return data

    @staticmethod
    def _check_number_of_samples(data: pd.DataFrame, n_samples_threshold: int):
        # TODO better docstring
        if len(data) <= n_samples_threshold:
            raise InsufficientDataError(
                f"The length of the generated DataFrame ({len(data)}) does not exceed the "
                f"specified required threshold for number of rows ({n_samples_threshold})."
            )

    @staticmethod
    def _apply_row_filter_and_known_filter_periods(
        data: pd.DataFrame,
        known_filter_periods: Optional[list],
        row_filter: Union[str, list],
        triggered_tags: List[Union[str, SensorTag]],
        row_filter_buffer_size: int,
        n_samples_threshold: int,
    ) -> pd.DataFrame:
        # TODO better docstring
        if known_filter_periods:
            data = pandas_filter_rows(data, known_filter_periods, buffer_size=0)
            if len(data) <= n_samples_threshold:
                raise InsufficientDataError(
                    f"The length of the filtered DataFrame ({len(data)}) does not exceed the "
                    f"specified required threshold for number of rows ({n_samples_threshold})"
                    f" after dropping known periods."
                )

        if row_filter:
            data = pandas_filter_rows(
                data, row_filter, buffer_size=row_filter_buffer_size
            )
            if len(data) <= n_samples_threshold:
                raise InsufficientDataError(
                    f"The length of the filtered DataFrame ({len(data)}) does not exceed the "
                    f"specified required threshold for the number of rows ({n_samples_threshold}), "
                    f" after applying the specified numerical row-filter."
                )

        if triggered_tags:
            triggered_columns = [extract_tag_name(tag) for tag in triggered_tags]
            data = data.drop(columns=triggered_columns)

        return data

    @staticmethod
    def _check_thresholds(
        data: pd.DataFrame,
        low_threshold: Optional[int],
        high_threshold: Optional[int],
        n_samples_threshold: int,
    ) -> pd.DataFrame:
        # TODO better docstring
        if isinstance(low_threshold, int) and isinstance(high_threshold, int):
            if low_threshold >= high_threshold:
                raise ConfigurationError(
                    "Low threshold need to be larger than high threshold"
                )
            logger.info("Applying global min/max filtering")
            mask = ((data > low_threshold) & (data < high_threshold)).all(1)
            data = data[mask]
            logger.info("Shape of data after global min/max filtering: %s", data.shape)
            if len(data) <= n_samples_threshold:
                raise InsufficientDataError(
                    f"The length of the filtered DataFrame ({len(data)}) does not exceed the "
                    f"specified required threshold for number of rows ({n_samples_threshold})"
                    f" after filtering global extrema."
                )
        return data

    def _apply_filter_periods(
        self,
        data: pd.DataFrame,
        filter_periods: Optional[FilterPeriods],
        n_samples_threshold: int,
        process_metadata: bool = True,
    ) -> pd.DataFrame:
        # TODO better docstring
        if filter_periods:
            data, drop_periods, _ = filter_periods.filter_data(data)
            if process_metadata:
                self._metadata["filtered_periods"] = drop_periods
            if len(data) <= n_samples_threshold:
                raise InsufficientDataError(
                    f"The length of the filtered DataFrame ({len(data)}) does not exceed the "
                    f"specified required threshold for number of rows ({n_samples_threshold})"
                    f" after applying nuisance filtering algorithm."
                )
        return data

    def _extract_x_and_y(
        self, data: pd.DataFrame
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        # TODO better docstring
        x_tag_names = [extract_tag_name(tag) for tag in self.tag_list]
        y_tag_names = [extract_tag_name(tag) for tag in self.target_tag_list]

        X = data[x_tag_names]
        y = data[y_tag_names] if self.target_tag_list else None
        return X, y

    @staticmethod
    def _additional_metadata(X: pd.DataFrame, y: Optional[pd.DataFrame]) -> dict:
        metadata = {}
        if X.first_valid_index():
            metadata["train_start_date_actual"] = X.index[0]
            metadata["train_end_date_actual"] = X.index[-1]

        metadata["summary_statistics"] = X.describe().to_dict()
        hists = dict()
        for tag in X.columns:
            step = round((X[tag].max() - X[tag].min()) / 100, 6)
            if step < 9e-07:
                hists[str(tag)] = "{}"
                continue
            outs = pd.cut(
                X[tag],
                bins=np.arange(
                    round(X[tag].min() - step, 6),
                    round(X[tag].max() + step, 6),
                    step,
                ),
                retbins=False,
            )
            hists[str(tag)] = outs.value_counts().sort_index().to_json(orient="index")
        metadata["x_hist"] = hists
        return metadata

    def _extract_provider_metadata(self):
        # TODO better docstring
        provider_metadata = self.data_provider.get_metadata()
        if provider_metadata:
            self._metadata["data_provider"] = provider_metadata

    def get_client_data(
        self, build_dataset_metadata: dict
    ) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        # TODO better docstring

        tag_list, triggered_tags = self._get_tag_list(
            self.row_filter, self.tag_list, self.target_tag_list
        )

        tag_names: Set[str] = set()
        for tags in (tag_list, triggered_tags):
            tag_names.update(extract_tag_name(tag) for tag in tags)

        sensor_tags = sensor_tags_from_build_metadata(
            build_dataset_metadata, tag_names, assets_config=self.assets_config
        )

        tag_list = [sensor_tags[extract_tag_name(tag)] for tag in tag_list]
        triggered_tags = [sensor_tags[extract_tag_name(tag)] for tag in triggered_tags]

        series_iter: Iterable[Tuple[pd.Series, Tag]] = self.data_provider.load_series(
            train_start_date=self.train_start_date,
            train_end_date=self.train_end_date,
            tag_list=tag_list,
            resolution=self.resolution,
        )

        data = self._join_timeseries(series_iter)

        self._check_number_of_samples(data, 0)

        data = self._apply_row_filter_and_known_filter_periods(
            data=data,
            known_filter_periods=[],
            row_filter=self.row_filter,
            triggered_tags=triggered_tags,
            row_filter_buffer_size=0,
            n_samples_threshold=0,
        )

        X, y = self._extract_x_and_y(data)

        return X, y

    def get_data(self) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:

        tag_list, triggered_tags = self._get_tag_list(
            self.row_filter, self.tag_list, self.target_tag_list
        )

        series_iter: Iterable[Tuple[pd.Series, Tag]] = self.data_provider.load_series(
            train_start_date=self.train_start_date,
            train_end_date=self.train_end_date,
            tag_list=tag_list,
            resolution=self.resolution,
        )

        data = self._join_timeseries(series_iter)

        self._check_number_of_samples(data, self.n_samples_threshold)

        data = self._apply_row_filter_and_known_filter_periods(
            data=data,
            known_filter_periods=self.known_filter_periods,
            row_filter=self.row_filter,
            triggered_tags=triggered_tags,
            row_filter_buffer_size=self.row_filter_buffer_size,
            n_samples_threshold=self.n_samples_threshold,
        )

        data = self._check_thresholds(
            data, self.low_threshold, self.high_threshold, self.n_samples_threshold
        )

        data = self._apply_filter_periods(
            data=data,
            filter_periods=self.filter_periods,
            n_samples_threshold=self.n_samples_threshold,
        )

        X, y = self._extract_x_and_y(data)

        metadata = self._additional_metadata(X, y)
        if metadata:
            self._metadata.update(metadata)

        self._extract_provider_metadata()

        return X, y

    def get_metadata(self):
        return self._metadata.copy()


class RandomDataset(TimeSeriesDataset):
    """
    Get a TimeSeriesDataset backed by
    gordo_dataset.data_provider.providers.RandomDataProvider
    """

    @compat
    @capture_args
    def __init__(
        self,
        train_start_date: Union[datetime, str],
        train_end_date: Union[datetime, str],
        tag_list: list,
        **kwargs,
    ):
        kwargs.pop("data_provider", None)  # Don't care what you ask for, you get random
        super().__init__(
            data_provider=RandomDataProvider(),
            train_start_date=train_start_date,
            train_end_date=train_end_date,
            tag_list=tag_list,
            **kwargs,
        )
