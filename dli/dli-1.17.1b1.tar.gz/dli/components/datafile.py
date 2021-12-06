#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import datetime
import glob
import logging
import multiprocessing
import os
import posixpath
import warnings
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import Dict, List
from urllib.parse import urlparse, ParseResult
import botocore
from boto3.session import Session
from dateutil import tz
from wrapt import ObjectProxy

from dli.components import _AttributeAdapter, object_to_namedtuple, to_snake_case_keys
from dli.models.dataset_model import DatasetModel

from platform_services_lib.lib.aspects.base_component import BaseComponent
from platform_services_lib.lib.services.exceptions import (
    DownloadFailed, DatalakeException, S3FileDoesNotExist,
    InsufficientPrivilegesException, S3BucketDoesNotExist
)
from platform_services_lib.lib.context.urls import datafile_urls

THREADS = multiprocessing.cpu_count()
logger = logging.getLogger(__name__)


class File(ObjectProxy):
    """
    This is only to mantain backwards compatibility with S3FS.
    Ideally we want to deprecate getting files as anything but
    context managers. This provides both the context manager
    and function that returns a files like object
    """
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.__wrapped__.close()


class S3DatafileWrapper:
    def __init__(self, datafile, client):
        # we want to override the files property
        # it isn't really needed for py3 but it is in py2
        self.__dict__ = {
            k: v for k,v in datafile.items() if k != "files"
        }
        self._datafile = datafile
        self._client = client

    def as_dict(self):
        return dict(self._datafile)

    def _asdict(self):
        return self.as_dict()

    def __getitem__(self, path):
        """
        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance
        """
        return self.open_file(path)

    def open_file(self, path):
        """
        Helper method to load an specific file inside a datafile
        without having to download all of it.

        :param str path: The path of the file to retrieve from s3.
        :returns: A S3File instance that can be used as a normal python file
        """
        bucket, _, key = path.partition('/')

        try:
            bucket = self._client.s3_resource.Bucket(bucket)
            response = bucket.Object(key).get()['Body']
            return File(response)
        except (
            self._client.s3_resource.meta.client.exceptions.NoSuchKey,
            self._client.s3_resource.meta.client.exceptions.NoSuchBucket
        ) as e:
            raise S3FileDoesNotExist(path)

    def __repr__(self):
        return str(dict(self._datafile))

    @property
    def files(self):
        """
        Lists all S3 files in this datafile, recursing on folders (if any)
        """
        files = self._datafile["files"]
        if not files:
            return []

        bucket = urlparse(files[0]['path']).netloc

        prefix = os.path.commonprefix([
            urlparse(file_['path']).path for file_ in files
        ]).lstrip('/')

        return [
            '{}/{}'.format(bucket, obj['Key']) for obj in
            self._client._list_objects(bucket, prefix)
        ]


class S3Client:
    """
    A wrapper client providing util methods for boto
    """

    def __init__(self, boto_session):
        # not called directly other than for testing purposes, called from from_dataset[id]
        self.boto_session = boto_session

        self.s3_resource = self.boto_session.resource(
            's3', endpoint_url=os.environ.get('S3_URL'),
        )

        self.s3_client = self.s3_resource.meta.client

    @classmethod
    def from_dataset(cls, client, dataset_id) -> 'S3Client':
        def _credentials():
            keys = client.get_s3_access_keys_for_dataset(dataset_id)
            expiry_time = (
                # expiring the token after an hour. It's conservative
                # but it should just be refreshed. TODO add expiry time
                # to the get_s3_access_keys_for_dataset endpoint
                datetime.datetime.now().replace(tzinfo=tz.tzlocal()) + timedelta(hours=1)
            ).isoformat()

            return dict(
                access_key=keys.access_key_id,
                secret_key=keys.secret_access_key,
                token=keys.session_token,
                expiry_time=expiry_time
            )

        session_credentials: botocore.credentials.RefreshableCredentials = \
            botocore.credentials.RefreshableCredentials.create_from_metadata(
                metadata=_credentials(),
                refresh_using=_credentials,
                method='NOOP'
            )

        session: Dict = botocore.session.get_session()
        # Extremely dirty but it seems to be the 'blessed' way of doing this.
        session._credentials: botocore.credentials.RefreshableCredentials = session_credentials
        return cls(Session(botocore_session=session))

    def _list_objects(self, bucket, prefix):
        # as it turns out the high level boto client is rather expensive
        # when creating objects en-masse. This is at least 50% faster.
        # This is also the exact way that the aws cli lists files.
        paginator = self.s3_client.get_paginator(
            'list_objects_v2'
        )

        paging_args = {'Bucket': bucket, 'Prefix': prefix}
        iterator = paginator.paginate(**paging_args)

        for response_data in iterator:
            for obj in response_data.get('Contents'):
                yield obj

    def download_files_from_s3(self, s3_location, destination, flatten=False):
        """
        Helper function to download a file as a stream from S3
        :param str s3_location: required, example: s3://bucket_name/prefix_part1/prefix_part2/file_name.txt

        :param str destination: required. The path on the system, where the
            files should be saved. must be a directory, if doesn't exist, will
            be created.

        :param bool flatten: The default behaviour (=False) is to use the s3
            file structure when writing the downloaded files to disk. Example:
            [
              'storm/climate/storm_data/storm_fatalities/as_of_date=2019-09-10/type=full/StormEvents_details-ftp_v1.0_d1950_c20170120.csv.gz',
              'storm/climate/storm_data/storm_fatalities/as_of_date=2019-09-10/type=full/StormEvents_details-ftp_v1.0_d1951_c20160223.csv.gz'
            ]

            When flatten = True, we remove the s3 structure. Example:

            Example output for new behaviour:
            [
              './storm-flattened/StormEvents_details-ftp_v1.0_d1950_c20170120.csv.gz',
              './storm-flattened/StormEvents_details-ftp_v1.0_d1951_c20160223.csv.gz'
            ]

        :returns: a list of the paths where the files were downloaded
            to e.g. ['path/git /package/dataset/as_of_date=2019-10-16
            /file.csv.gz'].
            with flatten=True e.g. ['path/file.csv.gz']

        :rtype: str
        """
        if os.path.isfile(destination):
            raise NotADirectoryError(destination)

        parse_result = urlparse(s3_location)
        bucket = parse_result.netloc
        # Removes forward slash
        download_path = parse_result.path.lstrip('/').rstrip('/')

        def _download(obj_summary):
            # Ignore 'folders'
            key = obj_summary['Key']
            destination_key = key
            if not key.endswith('/'):

                def flatten_s3_file_path(s3_path):
                    from urllib.parse import urlparse
                    import ntpath
                    path = urlparse(s3_path)[2]  # [scheme, netloc, path, ...]
                    head, tail = ntpath.split(path)
                    file = tail or ntpath.basename(head)
                    return file

                if flatten:
                    destination_key = flatten_s3_file_path(s3_path=key)

                destinatation_path = os.path.join(destination, destination_key)
                subfolder = os.path.dirname(destinatation_path)
                os.makedirs(subfolder, exist_ok=True)
                logger.info('Downloading File %s to %s', key, destinatation_path)
                self.s3_client.download_file(bucket, key, destinatation_path)
                return destinatation_path

        keys = list(self._list_objects(bucket, download_path))
        threads = min(THREADS, len(keys))
        with ThreadPoolExecutor(max_workers=threads) as executor:
            destination_path = list(executor.map(_download, keys))
        return destination_path

    def upload_files_to_s3(self, files, s3_location) -> List[Dict]:
        """
        Upload multiple files to a specified s3 location. The basename of the
        `files` will be preserved.

        :param List files: An list of filepaths
        :param str s3_location: Path to destination directory in S3, file will be
                 stored under <s3_location><filename>
        :returns: List of path to the files in S3
        :rtype: List[str]
        """

        bucket_name, *prefix = s3_location.partition('/')
        try:
            # Verify that the bucket exists to avoid support tickets of people trying to upload
            # to buckets with wrong spellings or buckets that do not exist.
            # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/migrations3.html#accessing-a-bucket
            bucket = self.s3_client.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError as e:
            # If a client error is thrown, then check that it was a 404 error.
            # If it was a 404 error, then the bucket does not exist.
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise S3BucketDoesNotExist(bucket_name) from e
            elif error_code == '403':
                # AWS permissions are setup in strange ways, like in the case that the user
                # has permission to upload to s3 but cannot call read operations such as
                # `head_bucket`. QA had this issue, so it breaks the code that checks if the
                # bucket exists before uploading.
                bucket = self.s3_resource.Bucket(bucket_name)
            else:
                # All other error_codes should bubble up the original exception.
                raise

        prefix = ''.join(prefix)

        def _files_to_upload_flattened(files):
            files_to_upload = []

            for file in files:
                if not os.path.exists(file):
                    raise Exception('File / directory specified (%s) for upload does not exist.' % file)

                if os.path.isfile(file):
                    logger.info("detected file: %s", file)
                    files_to_upload.append({'file': file,
                                            's3_suffix': os.path.basename(file)})
                elif os.path.isdir(file):
                    logger.info("detected directory: %s", file)
                    all_contents = glob.glob(os.path.join(file, "**/*"), recursive=True)
                    fs = [f for f in all_contents if os.path.isfile(f)]

                    for f in fs:
                        files_to_upload.append({
                            'file': f,
                            's3_suffix': os.path.relpath(f, file).replace("\\", "/")
                        })

            return files_to_upload

        def upload(file, s3_location) -> Dict:
            file_path = file['file']
            s3_suffix = file['s3_suffix']
            target = os.path.join(prefix, s3_suffix)

            logger.info("Uploading %s to %s", file_path, target)

            try:
                self.s3_client.upload_file(
                    file_path, bucket_name, target.lstrip('/')
                )
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'AccessDenied':
                    raise InsufficientPrivilegesException() from e

                raise e

            logger.info(".. %s uploaded successfully.", file_path)

            return {
                "path": ParseResult(
                    scheme='s3',
                    netloc=bucket_name,
                    path=target,
                    params='', query='', fragment=''
                ).geturl(),
                "size": os.path.getsize(file_path)
            }

        files_to_upload = _files_to_upload_flattened(files)
        result = []
        for file in files_to_upload:
            uploaded = upload(file, s3_location)

            result.append(uploaded)

        return result


# utilities above


class Datafile(BaseComponent):

    def register_datafile_metadata(
        self,
        dataset_id,
        name,
        files,
        data_as_of,
        original_name=None
    ):
        """
        Submit a request to create a new datafile under a specified dataset in the Data Catalogue. This function
        ``WILL NOT`` upload files

        Datafile is an instance of the data within a dataset, representing a snapshot of the data at the time of
        publishing. A dataset can be composed by one or more related files that share a single schema. of related
        datafiles. It provides user with metadata required to consume and use the data.

        See description for each parameter, and whether they are optional or mandatory.

        :param str dataset_id: Dataset ID to which the datafile belongs to.
        :param str name: A descriptive name of a datafile. It should be unique within the dataset.
        :param list[dict] files: List of file dictionaries. A file dictionary will contain the full file path
                                and size (optional) as items.
        :param str data_as_of: The effective date for the data within the datafile.
                               Expected format is YYYY-MM-DD.
        :param str original_name: Optional. Name of the data uploaded into the data lake.

        :returns: Registered datafile
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                datafile = client.register_datafile_metadata(
                    dataset_id,
                    name="My Datafile",
                    files=[{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}],
                    data_as_of="2018-05-28"
                )
        """
        ds: Dict[str, DatasetModel] = self.datasets(search_term=[f"id={dataset_id}"])
        num_matches = len(ds)
        if num_matches == 0:
            raise DatalakeException(f"No such dataset ID `{dataset_id}`")
        elif num_matches > 1:
            # This should not be possible, but let's cover this scenario incase Caatlogue returns
            # bad data.
            raise DatalakeException(f"More than one dataset with ID `{dataset_id}`")
        else:
            dataset: DatasetModel = list(ds.values())[0]

        if not files:
            raise DatalakeException("No files to register have been provided.")

        fields = {
            'datasetId': dataset.dataset_id,
            'name': name,
            'originalName': original_name,
            'dataAsOf': self._ensure_iso_date(data_as_of),
            'files': files,
        }

        payload = {k: v for k, v in fields.items() if v is not None}

        response_dict = self.session.post(
                    datafile_urls.datafiles_index, json=payload
                ).json()
        obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        return obj

    def register_s3_datafile(
        self,
        dataset_id,
        name,
        files,
        s3_prefix,
        data_as_of,
        original_name=None
    ):
        """
        Submit a request to create a new datafile under a specified dataset in the Data Catalogue.
        This function will perform an upload of the files to S3 data store.

        Datafile is an instance of the data within a dataset, representing a snapshot of the data at the time of publishing.
        A dataset can be composed by one or more related files that share a single schema. of related datafiles.
        It provides user with metadata required to consume and use the data.

        See description for each parameter, and whether they are optional or mandatory.

        :param str dataset_id: Dataset ID to which the datafile belongs to.
        :param str name: A descriptive name of a datafile. It should be unique within the dataset.
        :param list[str] files: Path of the files or folders to register.
        :param str s3_prefix: location of the files in the destination bucket. Cannot end with slash ("/")
        :param str data_as_of: The effective date for the data within the datafile.
                               Expected format is YYYY-MM-DD.
        :param str original_name: Optional. Name of the data uploaded into the data lake.

        :returns: Registered datafile.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                datafile = client.register_s3_datafile(
                    dataset_id=dataset_id,
                    name="My datafile",
                    files=["./test_sandbox/samples/data/AAPL.csv", "./test_sandbox/samples/data/MSFT.csv"],
                    s3_prefix="quotes/20180518",
                    data_as_of="2018-05-28"
                )
        """
        ds: Dict[str, DatasetModel] = self.datasets(search_term=[f"id={dataset_id}"])
        num_matches = len(ds)
        if num_matches == 0:
            raise Exception(f"No such dataset ID `{dataset_id}`")
        elif num_matches > 1:
            # This should not be possible, but let's cover this scenario incase Caatlogue returns
            # bad data.
            raise Exception(f"More than one dataset with ID `{dataset_id}`")
        else:
            dataset: DatasetModel = list(ds.values())[0]

        if not files:
            raise Exception("No files to register have been provided.")

        # upload files
        location = None if hasattr(dataset, 'location') is False else dataset.location
        if not location:
            raise Exception(
                f"No access to specified dataset.")

        if location.type != 'S3':
            raise Exception(
                "Only datasets backed on S3 are supported. use register_datafile_metadata instead.")

        bucket = location.bucket
        if not bucket:
            raise Exception(
                "Dataset location is S3, however, "
                "there is no bucket associated with the dataset {}".format(
                    dataset_id)
            )

        s3_location = "{}/{}".format(bucket, s3_prefix)
        uploaded = self._process_s3_upload(files, s3_location, dataset_id)


        return self.register_datafile_metadata(
            dataset_id,
            name=name,
            files=uploaded,
            original_name=original_name,
            data_as_of=self._ensure_iso_date(data_as_of),
        )

    def edit_datafile_metadata(
        self,
        datafile_id,
        name=None,
        original_name=None,
        data_as_of=None,
        files=None
    ):
        """
        Edits metadata for an existing datafile.
        This function WILL NOT upload files.
        Fields passed as ``None`` will retain their original value.

        :param str datafile_id: The id of the datafile we want to modify.
        :param str name: Optional. Name of the datafile.
        :param str original_name: Optional. Original Name for the datafile.
        :param str data_as_of: Optional. The effective date for the data within the datafile.
                               Expected format is YYYY-MM-DD.
        :param list[dict] files: Optional. List of file dicts. A file dict will contain file path and size(optional) as items.

        :returns: Registered datafile
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                updated_datafile = client.edit_datafile_metadata(
                    datafile_id,
                    name="My Datafile",
                    files=[{'path': "/path/to/file/A", 'size': 99999}, {'path': "/path/to/file/B", 'size': 88888}]
                )
        """

        datafile = self._get_datafile(datafile_id)

        fields = {
            'datasetId': datafile.datasetId,
            'name': name,
            'originalName': original_name,
            'dataAsOf': self._ensure_iso_date(data_as_of),
            'files': files
        }

        # clean up any unknown fields, and update the entity
        datafile_as_dict = datafile.as_dict()

        for key in list(datafile_as_dict.keys()):
            if key not in fields:
                del datafile_as_dict[key]

        payload = {k: v for k, v in fields.items() if v is not None}
        datafile_as_dict.update(payload)

        # perform the update and return the resulting entity
        response_dict = self.session.put(
            datafile_urls.datafiles_instance.format(id=datafile_id),
            json=datafile_as_dict
        ).json()
        obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        named_tuple_obj = object_to_namedtuple(obj)
        return named_tuple_obj

    def delete_datafile(self, datafile_id):
        """
        Marks a datafile as deleted.

        :param str datafile_id: the unique id for the datafile we want to delete.

        :returns: None

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                client.delete_datafile(datafile_id)
        """
        response = self.session.delete(
            datafile_urls.datafiles_instance.format(id=datafile_id)
        )

    def get_s3_datafile(self, datafile_id):
        """
         .. deprecated:: 1.8.0

            This method is be deprecated and will be removed in release 1.18.0.
            Please change your workflow to instead get the dataset and then call download on
            that dataset. Filters can be provided to target data within the S3 partitions such
            'as `as_of_date` e.g.

            .. code-block:: python

                    dataset = client.datasets.get(
                        dataset_short_code='ExampleDatasetShortCode',
                        organisation_short_code='IHSMarkit'
                    )"

                    dataset.download(partitions=['as_of_date>=2020-01-01','country=US'])

            This dataset `download` call will download using the contents that is on S3.

        Fetches an S3 datafile providing easy access to directly
        stream/load files without the need of downloading them.

        If the datafile is not stored in S3, or you don't have access to it
        then an error will be displayed.

        :param str datafile_id: The id of the datafile we want to load

        :returns: a datafile that can read files from S3
        :rtype: dli.client.components.datafile.S3DatafileWrapper

        .. code-block:: python

                client = dli.connect()
                datafile = client.get_s3_datafile(datafile_id)
                with datafile.open_file("path/to/file/in/datafile") as f:
                    f.read() # do something with the file

                # or if you want a pandas dataframe created from it you can
                pd.read_csv(datafile.open_file("path/to/file/in/datafile"))

                # you can see all the files in the datafile by calling `files`
                datafile.files  # displays a list of files in this datafile

        """
        warnings.warn(
            'This method is be deprecated and will be removed in release 1.18.0. '
            '\nPlease change your workflow to instead get the dataset and then call download on '
            'that dataset. Filters can be provided to target data within the S3 partitions such '
            'as `as_of_date` e.g. '
            "\n\n    dataset = client.datasets.get(dataset_short_code='ExampleDatasetShortCode', "
            "organisation_short_code='IHSMarkit')"
            "\n\n    dataset.download(partitions=['as_of_date>=2020-01-01','country=US'])"
            '\n\nThis dataset `download` call will download using the contents that is on S3.',
            PendingDeprecationWarning
        )

        datafile = self.get_datafile(datafile_id)
        s3_access = S3Client.from_dataset(self, datafile.dataset_id)
        return S3DatafileWrapper(datafile._asdict(), s3_access)

    def download_datafile(self, datafile_id, destination, flatten=False):
        """
         .. deprecated:: 1.17.0
            This method is be deprecated and will be removed in release 1.18.0.
            Please change your workflow to instead get the dataset and then call download on
            that dataset. Filters can be provided to target data within the S3 partitions such
            'as `as_of_date` e.g.

            .. code-block:: python

                    dataset = client.datasets.get(
                        dataset_short_code='ExampleDatasetShortCode',
                        organisation_short_code='IHSMarkit'
                    )"

                    dataset.download(partitions=['as_of_date>=2020-01-01','country=US'])

            This dataset `download` call will download using the contents that is on S3.

        Helper function that downloads all files
        registered in a datafile into a given destination.

        This function is only supported for data-lake managed s3 buckets,
        otherwise an error will be displayed.

        Currently supports:
          - s3

        :param str datafile_id: The id of the datafile we want to download files from.

        :param str destination: required. The path on the system, where the
            files should be saved. must be a directory, if doesn't exist, will
            be created.

        :param bool flatten: Optional. The default behaviour (=False) is to use the s3
            file structure when writing the downloaded files to disk. Example:
            [
              'storm/climate/storm_data/storm_fatalities/as_of_date=2019-09-10/type=full/StormEvents_details-ftp_v1.0_d1950_c20170120.csv.gz',
              'storm/climate/storm_data/storm_fatalities/as_of_date=2019-09-10/type=full/StormEvents_details-ftp_v1.0_d1951_c20160223.csv.gz'
            ]

            When flatten = True, we remove the s3 structure. Example:

            Example output for new behaviour:
            [
              './storm-flattened/StormEvents_details-ftp_v1.0_d1950_c20170120.csv.gz',
              './storm-flattened/StormEvents_details-ftp_v1.0_d1951_c20160223.csv.gz'
            ]

        :returns: a list of the paths where the files were downloaded
            to e.g. ['path/git /package/dataset/as_of_date=2019-10-16
            /file.csv.gz'].
            with flatten=True e.g. ['path/file.csv.gz']

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                client.download_datafile(datafile_id, destination)
        """
        warnings.warn(
            'This method is be deprecated and will be removed in release 1.18.0. '
            '\nPlease change your workflow to instead get the dataset and then call download on '
            'that dataset. Filters can be provided to target data within the S3 partitions such '
            'as `as_of_date` e.g. '
            "\n\n    dataset = client.datasets.get(dataset_short_code='ExampleDatasetShortCode', "
            "organisation_short_code='IHSMarkit')"
            "\n\n    dataset.download(partitions=['as_of_date>=2020-01-01','country=US'])"
            '\n\nThis dataset `download` call will download using the contents that is on S3.',
            PendingDeprecationWarning
        )
        # get the s3 keys
        # this requires access to be granted
        datafile = self._get_datafile(datafile_id)
        s3_access = S3Client.from_dataset(self, datafile.datasetId)
        # for each file/folder in the datafile, attempt to download the file
        # rather than failing at the same error, keep to download as much as
        # possible and fail at the end.
        failed = []
        files = [f["path"] for f in datafile.files]
        filepaths = []
        for file in files:
            try:
                download_path = s3_access.download_files_from_s3(
                    s3_location=file,
                    destination=destination,
                    flatten=flatten,
                )
                filepaths.extend(download_path)
            except Exception:
                logger.exception(
                    "Failed to download file `%s` from datafile `%s`", file, datafile_id)
                failed.append(file)

        if failed:
            raise DownloadFailed(
                "Some files in this datafile could not be downloaded, "
                "see logs for detailed information. Failed:\n%s"
                % "\n".join(failed)
            )
        return filepaths

    def _process_s3_upload(self, files, s3_location, dataset_id):
        s3_client = S3Client.from_dataset(self, dataset_id)
        # Ensure trailing slash is included if missing
        s3_location = posixpath.join(s3_location, '')
        return s3_client.upload_files_to_s3(files, s3_location)

    def get_datafile(self, datafile_id):
        """
        Fetches datafile metadata for an existing datafile.

        :param str datafile_id: the unique id of the datafile we want to fetch.

        :returns: The datafile.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                datafile = client.get_datafile(datafile_id)
        """
        datafile = self._get_datafile(datafile_id, snake_case=True)

        return object_to_namedtuple(datafile)

    def _get_datafile(self, datafile_id, snake_case: bool = False):
        response_dict = self.session.get(
            datafile_urls.datafiles_instance.format(id=datafile_id)
        ).json()
        if snake_case:
            obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        else:
            obj = type(response_dict['class'][0], (_AttributeAdapter,), response_dict["properties"])()
        return obj

    def add_files_to_datafile(self, datafile_id, s3_prefix, files):
        """
        Upload files to existing datafile.

        :param str datafile_id: The id of the datafile to be updated.
        :param str s3_prefix: Location for the files in the destination s3 bucket. Cannot end with slash ("/").
        :param list[str] files: List of files to be added to the datafile.

        :returns: The updated datafile.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                datafile_updated_with_additional_files = client.add_files_to_datafile(
                                                              datafile_id=datafile_id,
                                                              s3_prefix="quotes/20180518",
                                                              files=["./data/AAPL.csv", "./data/MSFT.csv"],
                                                        )
        """
        datafile = self.get_datafile(datafile_id)
        dataset_id = datafile.dataset_id

        ds: Dict[str, DatasetModel] = self.datasets(search_term=[f"id={dataset_id}"])
        num_matches = len(ds)
        if num_matches == 0:
            raise Exception(f"No such dataset ID `{dataset_id}`")
        elif num_matches > 1:
            # This should not be possible, but let's cover this scenario incase Caatlogue returns
            # bad data.
            raise Exception(f"More than one dataset with ID `{dataset_id}`")
        else:
            dataset: DatasetModel = list(ds.values())[0]

        location = None if hasattr(dataset, 'location') is False else dataset.location
        if not location:
            raise Exception("No access to dataset.")

        if dataset.location.type != "S3":
            raise Exception("Can not upload files to non-S3 datasets.")

        s3_location = "{}/{}".format(dataset.location.bucket, s3_prefix)
        uploaded_files = self._process_s3_upload(
            files,
            s3_location,
            datafile.dataset_id
        )

        if datafile.files:
            uploaded_files.extend(datafile.files)

        return self.edit_datafile_metadata(datafile_id, files=uploaded_files)

    @staticmethod
    def _ensure_iso_date(date):
        if date:
            return datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        return date

