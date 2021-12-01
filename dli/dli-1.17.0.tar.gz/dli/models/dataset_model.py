#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import logging
import os
import uuid
from abc import ABCMeta
from datetime import timezone
from functools import partial
from typing import List, Optional, Callable, Tuple, Dict
from boto3.session import Session
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
from tqdm import tqdm
import boto3.s3.transfer

from dli.models import get_or_create_os_path, print_model_metadata

from platform_services_lib.lib.services.dlc_attributes_dict import AttributesDict
from platform_services_lib.lib.handlers.s3_dataset_handler import S3DatasetHandler, is_hidden_based_on_path_and_content, S3PathDetails

trace_logger = logging.getLogger('trace_logger')


class DatasetModel(AttributesDict, metaclass=ABCMeta):

    def __init__(self, **kwargs):
        # We have to declare the attribute `load_type` because it is
        # referenced in the code of this class. This means that there will
        # be an `documentation` attribute even when there is zero
        # `documentation` attribute in the Catalogue response JSON.
        self.load_type: Optional[str] = None
        self.__handler: _SDKDatasetHandler = _SDKDatasetHandler(self._client._environment.s3_proxy, self._client.session, self)
        super().__init__(**kwargs, )

    def _check_access(self):
        if not self.has_access:
            # Link to the package page in the Catalogue UI where the user
            # can request access.
            # eg. https://catalogue.datalake.ihsmarkit.com/package/
            # 7eddd22c-2b3c-11eb-9dd7-f64fac425b13
            package_url = f'{self._client._environment.catalogue}/' \
                          f'package/{self.package_id}'
            raise Exception(
                'You require access to this package to retrieve its content. '
                f'To request access, please visit {package_url}'
            )

    @property
    def id(self):
        return self.dataset_id

    def __list(
        self,
        request_id=None,
        custom_filter_func: Callable[[List[S3PathDetails]], List[S3PathDetails]] = None,
        filter_path: Optional[str] = None,
        absolute_path: bool = True,
        skip_hidden_files: bool = True,
    ) -> List[str]:
        """
        List all the paths to files in the dataset. Calls go via the
        Datalake's S3 proxy, so the returned paths will be returned in the
        style of the S3 proxy, so in the pattern
        `s3://organisation_short_code/dataset_short_code/<path>`.
        S3 proxy does not return direct paths to the real location on S3 as
        they may be sensitive.

        The list will filter out paths where:
        * The size is zero bytes.
        * The name of any partition within the path is prefixed with a `.` or
        a `_` as that means it is intended as a hidden file.
        * The name of any partition within the path is exactly the word
        `metadata`.
        * It is a directory rather than a file.
        * Files with the wrong extension for the dataset's type i.e for
        a .parquet dataset we will return only .parquet files, zero .csv
        files.

        This list will filter based on `load_type` of the dataset. When the
        dataset's `load_type` is `Incremental Load` then files will be listed
        from all of the `as_of_date` partitions on S3. When the
        dataset's `load_type` is `Full Load` then files will be listed only
        the most recent `as_of_date` partition on S3.
        Please see the support library documentation for more information
        about how the `load type` affects the data you can access in a dataset:
        https://supportlibrary.ihsmarkit.com/display/DLSL/Exploring+Datasets#ExploringDatasets-Howthe%60loadtype%60affectsthedatayoucanaccessinadataset

        Parameters
        ----------
        :param str request_id: Optional. Automatically generated value
            used by our logs to correlate a user journey across several
            requests and across multiple services.

        :param custom_filter_func: A function which may optionally filter the s3 paths returned during the first
        stage of download (namely path lookup as part of list is filtered).

        :param str filter_path: Optional. If provided only a subpath matching
            the filter_path will be matched. This is less flexible than using
            the `partitions` parameter, so we recommend you pass in
            `partitions` instead. The `partitions` can deal with the
            partitions in the path being in any order, but filter_path relies
            on a fixed order of partitions that the user needs to know ahead
            of time.

            Example usage to get all paths that start with the `as_of_date`
            2020. Note this is a string comparison, not a datetime comparison.

            .. code-block:: python

                ds = client.datasets.get(short_code=dataset_short_code)
                ds.list(filter_path='as_of_date=2020')

        :param bool absolute_path: True (default) for returning an
            absolute path to the path on the S3 proxy. False to return a
            relative path (this is useful if using a TransferManager).

        :param bool skip_hidden_files: True (default) skips files that have
            been uploaded to S3 by Spark jobs. These usually start with a
            `.` or `_`.
        """

        self._check_access()
        paths: Tuple[str]
        sizes: Tuple[int]
        paths, sizes = self.__handler.list_with_size(
            request_id=request_id,
            custom_filter_func=custom_filter_func,
            filter_path=filter_path,
            absolute_path=absolute_path,  # TransferManager uses relative paths.
            skip_hidden_files=skip_hidden_files,
        )

        return list(paths)

    def __download(
        self,
        destination_path: str,
        flatten: Optional[bool] = False,
        filter_path: Optional[str] = None,
        custom_filter_func: Callable[[List[str]], List[str]] = None,
        skip_hidden_files: Optional[bool] = True
    ) -> List[str]:
        """
        Equivalent to the exposed `download` method. Used as a base for
        all models

        Additional Parameters
        ----------
        :param bool flatten: The flatten parameter default behaviour
            (flatten=False) will allow the user to specify that they would
            like to keep the underlying folder structure when writing the
            downloaded files to disk.
            When “flatten” is set to True the
            folder structure and download all data to the specified path in
            and retains only the original file name. This is not useful if the
            file names are identical for multiple files.

        :param custom_filter_func: A function which may optionally filter
        the s3 paths returned during the first stage of download (namely
        path lookup as part of list is filtered).
        """

        self._check_access()
        request_id = str(uuid.uuid4())

        paths: Tuple[str]
        sizes: Tuple[int]
        paths, sizes = self.__handler.list_with_size(
            request_id=request_id,
            custom_filter_func=custom_filter_func,
            filter_path=filter_path,
            absolute_path=False,  # TransferManager uses relative paths.
            skip_hidden_files=skip_hidden_files,
        )

        transfer_manager_context = self.__handler._get_transfer_manager()

        # Use an environment variable to disable the entire progressbar
        # wrapper. This can be necessary for monitors where the bar will not
        # be correctly formatted in DataDog.
        disable_progress_bar = \
            True if os.environ.get('DLI_DISABLE_PROGRESS_BAR', '').lower() \
            == 'true' else False

        progress = tqdm(
            desc='Downloading ',
            total=sum(sizes), unit='B', unit_scale=1,
            position=0,
            disable=disable_progress_bar,
        )

        warns = []
        with transfer_manager_context as transfer_manager:
            with progress as pbar:
                # Create progress_callback outside of the loop.
                progress_callback = boto3.s3.transfer.ProgressCallbackInvoker(
                    pbar.update
                )
                subscribers = [progress_callback]

                _paths_and_futures = []

                for path in paths:

                    if not path.endswith('/'):
                        to_path = get_or_create_os_path(
                            s3_path=path,
                            to=destination_path,
                            flatten=flatten
                        )

                        trace_logger.debug(
                            f'Downloading {path} to: {to_path}...'
                        )

                        if os.path.exists(to_path):
                            warns.append(to_path)

                        # returns a future
                        future = transfer_manager.download(
                            self.organisation_short_code,
                            path,
                            to_path,
                            subscribers=subscribers,
                        )

                        _paths_and_futures.append((to_path, future))

                _successful_paths = []
                for path, future in _paths_and_futures:
                    try:
                        # This will block for this future to complete,
                        # but other futures will keep running in the
                        # background.
                        future.result()
                        _successful_paths.append(path)
                    except Exception as e:
                        message = f'Problem while downloading:' \
                                  f'\nfile path: {path}' \
                                  f'\nError message: {e}\n\n'

                        self._client.logger.error(message)
                        print(message)

            return _successful_paths

    def metadata(self):
        """
        Once you have selected a dataset, you can print the metadata (the
        available fields and values).

        :Example:

            .. code-block:: python

                # Get all datasets.
                >>> datasets = client.datasets()

                # Get metadata of the 'ExampleDatasetShortCode' dataset.
                >>> datasets['ExampleDatasetShortCode'].metadata()

        :Example:

            .. code-block:: python

                # Get an exact dataset using the dataset_short_code and
                # organisation_short_code.
                >>> dataset = client.datasets.get(dataset_short_code='ExampleDatasetShortCode', organisation_short_code='IHSMarkit')
                # Get metadata of the dataset.
                >>> dataset.metadata()

        :Example:

            .. code-block:: python

                # Get all datasets.
                >>> dataset = client.datasets()['ExampleDatasetShortCode']
                # Get metadata of the dataset.
                >>> dataset.metadata()

        :return: Prints the metadata.
        """
        print_model_metadata(self)

    def package(self):
        """
        Returns the parent package of this dataset - see :ref:`PackageModel`.

        """

        # note there is no typing on this method to avoid a circular referencing.
        return list(self._client.packages(search_term=f"package_id={self.package_id}").values())[0]


class _SDKDatasetHandler(S3DatasetHandler):

    KB = 1024
    GB = KB * KB * KB

    def __init__(self, endpoint_url, session, dataset):
        # we have no ttlcache or memcached
        self.endpoint = endpoint_url
        self.session = session
        self.dataset = dataset
        super().__init__(True, None)  # ttl_cache, hash_client

    def endpoint_url(self):
        return self.endpoint

    def __get_s3_resource(self, request_id=None):
        return _SDKDatasetHandler.create_refreshing_session(
            dli_client_session=self.session,
            event_hooks=partial(self.__add_request_id_to_session, request_id)
        ).resource(
            's3',
            endpoint_url=self.endpoint_url()
        )

    def _get_transfer_manager(self):
        # multipart_threshold -- The transfer size threshold for which
        # multipart uploads, downloads, and copies will automatically
        # be triggered.
        # 500 GB should be a large enough number so that the download never
        # triggers multipart download on cloudfront.
        multipart_threshold = 500 * _SDKDatasetHandler.GB

        s3_resource = self.__get_s3_resource()

        return boto3.s3.transfer.create_transfer_manager(
            client=s3_resource.meta.client,
            config=boto3.s3.transfer.TransferConfig(multipart_threshold=multipart_threshold)
        )

    @staticmethod
    def create_refreshing_session(
        dli_client_session, **kwargs
    ) -> Session:
        """
        :param dli_client_session: We must not be closing over the original
        variable in a multi-threaded env as the state can become shared.
        :param kwargs:
        :return:
        """

        def refresh():
            auth_key = dli_client_session.auth_key
            expiry_time = dli_client_session.token_expires_on.replace(
                tzinfo=timezone.utc
            ).isoformat()

            return dict(
                access_key=auth_key,
                secret_key='noop',
                token='noop',
                expiry_time=expiry_time,
            )

        _refresh_meta = refresh()

        session_credentials = RefreshableCredentials.create_from_metadata(
            metadata=_refresh_meta,
            refresh_using=refresh,
            method='noop'
        )

        session = get_session()
        handler = kwargs.pop("event_hooks", None)
        if handler is not None:
            session.register(f'before-send.s3', handler)

        session._credentials = session_credentials
        return Session(
            botocore_session=session,
            **kwargs
        )

    def __add_request_id_to_session(self, request_id, **kwargs):
        if request_id is None:
            request_id = str(uuid.uuid4())

        trace_logger.info(
            f"The following GET Requests to '{self.endpoint_url()}' "
            f"will be using request_id: '{request_id}'"
        )
        kwargs["request"].headers['X-Request-ID'] = request_id

    def handle(self, dataset) -> None:
        pass # not implemented, we use a transfermanager wrapping list

    def list(self, accessible_datasets: List, organisation_shortcode: str, args, method_name: str) -> None:
        pass # need custom function args @see list_with_size

    def list_with_size(
            self,
            request_id=None,
            custom_filter_func: Callable[[List[S3PathDetails]], List[S3PathDetails]] = None,
            filter_path: Optional[str] = None,
            absolute_path: bool = True,
            skip_hidden_files: bool = True,
        ) -> Tuple[List[str], List[int]]:
            """
            List all the paths to files in the dataset. Calls go via the
            Datalake's S3 proxy, so the returned paths will be returned in the
            style of the S3 proxy, so in the pattern
            `s3://organisation_short_code/dataset_short_code/<path>`.
            S3 proxy does not return direct paths to the real location on S3 as
            they may be sensitive.

            The list will filter out paths where:
            * The size is zero bytes.
            * The name of any partition within the path is prefixed with a `.` or
            a `_` as that means it is intended as a hidden file.
            * The name of any partition within the path is exactly the word
            `metadata`.
            * It is a directory rather than a file.
            * Files with the wrong extension for the dataset's type i.e for
            a .parquet dataset we will return only .parquet files, zero .csv
            files.

            This list will filter based on `load_type` of the dataset. When the
            dataset's `load_type` is `Incremental Load` then files will be listed
            from all of the `as_of_date` partitions on S3. When the
            dataset's `load_type` is `Full Load` then files will be listed only
            the most recent `as_of_date` partition on S3.
            Please see the support library documentation for more information
            about how the `load type` affects the data you can access in a dataset:
            https://supportlibrary.ihsmarkit.com/display/DLSL/Exploring+Datasets#ExploringDatasets-Howthe%60loadtype%60affectsthedatayoucanaccessinadataset

            Parameters
            ----------
            :param str request_id: Optional. Automatically generated value
                used by our logs to correlate a user journey across several
                requests and across multiple services.

            :param custom_filter_func: A function which may optionally filter the
            s3 paths returned during the first stage of download (namely path
            lookup as part of list is filtered).

            :param str filter_path: Optional. If provided only a subpath matching
                the filter_path will be matched. This is less flexible than using
                the `partitions` parameter, so we recommend you pass in
                `partitions` instead. The `partitions` can deal with the
                partitions in the path being in any order, but filter_path relies
                on a fixed order of partitions that the user needs to know ahead
                of time.

                Example usage to get all paths that start with the `as_of_date`
                2020. Note this is a string comparison, not a datetime comparison.

                .. code-block:: python

                    >>> dataset = client.datasets.get(dataset_short_code='ExampleDatasetShortCode', organisation_short_code='IHSMarkit')
                    >>> dataset.list(filter_path='as_of_date=2020')

            :param bool absolute_path: True (default) for returning an
                absolute path to the path on the S3 proxy. False to return a
                relative path (this is useful if using a TransferManager).

            :param bool skip_hidden_files: True (default) skips files that have
                been uploaded to S3 by Spark jobs. These usually start with a
                `.` or `_`.
            """

            s3_resource = self.__get_s3_resource(request_id)

            filter_prefix = self.dataset.short_code + (
                '' if self.dataset.short_code.endswith('/') else '/'
            )

            if filter_path:
                filter_prefix = filter_prefix + filter_path.lstrip('/')

            if filter_path is None and skip_hidden_files:
                paths: List[S3PathDetails] = list(
                    self.get_s3_list_filter(
                        resource=s3_resource,
                        bucket_name=self.dataset.organisation_short_code,
                        prefix=filter_prefix,
                        absolute_path=absolute_path,
                        prefix_filter_fn=partial(
                            S3DatasetHandler.filter_hidden_prefixes_by_dataset_content_and_load_type,
                            self.dataset.content_type,
                            self.dataset.load_type,
                            filter_prefix
                        )
                    )
                )
            else:
                # The user provided an explicit filter_path so give the
                # user the S3 list under that path. There is no need to do common
                # prefix filtering as the filter_path will point us to a folder
                # not in the top-level of the dataset (where the .hidden
                # directories usually appear).
                paths: List[Dict] = list(
                    self.get_s3_list(
                        resource=s3_resource,
                        bucket_name=self.dataset.organisation_short_code,
                        prefix=filter_prefix,
                        absolute_path=absolute_path
                    )
                )

            trace_logger.info(
                "Number of paths on S3 for this dataset: "
                f"'{len(paths)}'"
            )

            if skip_hidden_files:
                # Although we have skipped hidden files in the top-level, there
                # could be files under the prefix e.g. sometimes there are Spark
                # _SUCCESS files mixed in with the data at the leaf level of the
                # S3 tree.

                paths: List[Dict] = [
                    path for path in paths
                    if not any(is_hidden_based_on_path_and_content(split, self.dataset.content_type)
                               for split in path["Key"].split('/'))
                ]

                trace_logger.info(
                    f"Number of paths on S3 for this dataset "
                    f"after filtering out hidden files: '{len(paths)}'"
                )

            if custom_filter_func:
                len_before = len(paths)
                trace_logger.info(
                    f'Filtering {len_before} paths according to this dataset '
                    f"type's custom filter logic."
                )

                paths = custom_filter_func(paths=paths)
                trace_logger.info(
                    f'Filtered out {len_before - len(paths)} / {len_before} paths '
                    f'according to constraints.'
                )

                if len(paths) == 0:
                    self.dataset._client.logger.warning(
                        f'There are no items matching your filter settings. Check '
                        f'your filter settings.\n'
                    )
                    return [], []

            if paths:
                key_paths, sizes = zip(*map(lambda x: (x['Key'], x['Size']), paths))
                return key_paths, sizes
            else:
                return [], []

    def __repr__(self):
        return "SDKDatasetHandler"
