import os
import time
import typing
import uuid
from abc import ABC
from functools import wraps
from typing import Optional, Iterator, List, Dict, Union
import boto3
from boto3 import Session as Boto3Session
from cachetools import TTLCache, cached
import logging
from collections import defaultdict
from dateutil.parser import isoparse
from datetime import datetime
try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from flask import g
    from injector import inject
    from pymemcache import HashClient
except ModuleNotFoundError:
    # set up an Identity decorator for @inject
    def inject(function): # type: ignore
        def wrapper(*args, **kwargs):
            return function(*args, *kwargs)
        return wrapper


try:
    # these are only present for services, not for the SDK, and we do not wish to impose these in requirements.txt
    from ..providers.memcache_provider import memcached_method
except ModuleNotFoundError:
    def memcached_method(cache_getter, cache_func_name ,key=None, ttl=None, force_cache_refresh=False): # type: ignore
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper
        return decorator

from ..handlers.s3_partition_handler import get_partitions_in_filepath
from ..adapters.s3_io_adapters import S3File
from ..services.abstract_backend_handler_service import AbstractBackendDatasetHandler
from ..services.exceptions import UnableToAccessDataset

logger = logging.getLogger(__name__)

duration_seconds: int = int(os.environ.get(
    'ASSUME_ROLE_DURATION_SECONDS',
    '3600' # ideally we want this a lot longer, or specific to the bucket
))

S3PathDetails = dict


def _shorten(common_prefix: str, prefix: str):
    """
    Path is made by stripping the common prefix of the prefix
    and the delimiter, which S3 returns.

    :param common_prefix: e.g. abc/as_of_date=2019/
    :return: as_of_date=2019
    """

    top_level_path = common_prefix
    if common_prefix.startswith(prefix):
        top_level_path = common_prefix[len(prefix):]
    if common_prefix.endswith('/'):
        top_level_path = top_level_path[:-1]
    return top_level_path


def is_hidden_based_on_path_and_content(path: str, content_type: str) -> bool:
    """
    [DL-4545][DL-4536][DL-5209] Do not read into files or
    directories that are cruft from Spark which Spark will ignore
    on read, e.g. files/dirs starting with `.` or `_` are hidden
    to Spark.

    Skip as_of_*=latest as it is a Spark temporary folder.

    :param content_type: Structured/Unstructured
    :param path: e.g. as_of_date=2019, .latest, as_of_date=latest
    :return: True if the path matches the criteria of a hidden file.
    """
    return (
            path.startswith('.') or
            path.startswith('_') or
            (
                    path == 'metadata' and
                    content_type != "Unstructured"
            ) or
            (
                    path.startswith('as_of_') and
                    path.endswith('=latest')
            )
    )


class S3DatasetHandler(AbstractBackendDatasetHandler, ABC):

    """
    This is an abstract implementation, providing common methods for S3Datasets. The application itself should choose how
    to extend common methods specific for its uses, and any common ones across repos should live here
    """

    @inject
    def __init__(
        self,
        ttl_cache: TTLCache,
        hash_client: 'HashClient',
    ):
        """
        Constructor.

        :param tlc_cache: tbc
        :param hash_client: Used for caching responses from S3.
        """
        logger.debug('DatasetS3Handler constructor')
        super().__init__(ttl_cache=ttl_cache, hash_client=hash_client)

    def __del__(self):
        """Destructor."""
        logger.debug('Destructor called on DatasetS3Handler')

    def create_session(self, role_arn: Optional[str]) -> Boto3Session:
        """
        Assume the role using the role arn and the secret (in the environment
        variables for this environment).

        See https://stackoverflow.com/a/45834847

        The assuming the role takes about 0.3 seconds so this becomes
        expensive, especially for Big Data tools that make many recursive calls.

        :param role_arn: Role to assume.
        :return: A Boto3 Session which used the role_arn to assume the
        role, allowing access to the data on S3. It can automatically refresh
        when it reaches the expiry time.
        """

        @cached(cache=self.ttl_cache)
        def _create_session(_role_arn: Optional[str]) -> Boto3Session:

            # todo - dont think we need to check - as we just wont have access later
            # if not _role_arn:
            #     raise UnableToAuthenticateToS3(
            #         'AWS account has no RoleArn data. This means '
            #         'the business line which owns this AWS account, '
            #         'is still using an insecure way of authenticating to S3.'
            #     )

            # This is expensive as assume role talks to AWS, takes maybe
            # 0.3 seconds.

            # Refreshing session had memory leaks, so instead make a non-refreshing session.
            # https://stackoverflow.com/a/56262329

            # Duration can be up to to the maximum session duration setting for the role. This
            # setting can have a value from 1 hour to 12 hours. Let us try asking for the maximum
            # as we may have long running `dataframe` calls.
            # https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
            # If you exceed the max for the role, you will get this exception message:
            # An error occurred (ValidationError) when calling the AssumeRole operation: The
            # requested DurationSeconds exceeds the MaxSessionDuration set for this role.

            # Re-use this request's request_id so if anyone cared to they could track the
            # request across services all the way to AWS.

            try:
                # this is for testing with localstack, changing the endpoint from real s3
                args = {}
                if os.environ.get("AWS_STS_URL", None):
                    args["endpoint_url"] = os.environ["AWS_STS_URL"]

                credentials = boto3.client("sts", **args).assume_role(
                    RoleSessionName=g.request_id if hasattr(g, "request_id") else str(uuid.uuid4()),
                    RoleArn=_role_arn,
                    DurationSeconds=duration_seconds
                )

                # Translate the keys from PascalCase to snake_case.
                return Boto3Session(
                    aws_access_key_id=credentials["Credentials"]["AccessKeyId"],
                    aws_secret_access_key=credentials["Credentials"]["SecretAccessKey"],
                    aws_session_token=credentials["Credentials"]["SessionToken"]
                )
            except Exception as e:
                logging.warning(e)
                raise e

        return _create_session(_role_arn=role_arn)

    def common_prefixes_on_s3(
        self,
        resource,
        bucket,
        prefix: str,
        is_top_level_call: bool,
    ) -> List[Dict]:
        """
        Checks to see if the common prefixes in cache match the common prefixes
        on S3 now. Returns the refreshed list of common prefixes.

        :param resource:
        :param bucket:
        :param prefix:
        :param is_top_level_call:
        :return: A list of the most recent common prefixes object summaries.
        """

        logger.debug(
            'Fetch common prefixes (likely the `as_of` partition) from '
            'cache',
            extra={
                'Bucket': bucket.name,
                'Prefix': prefix,
                'is_top_level_call': is_top_level_call,
            }
        )
        return list(
            self.get_common_prefixes(
                resource=resource,
                bucket=bucket,
                prefix=prefix,
                force_cache_refresh=is_top_level_call,
            )
        )

    def get_common_prefixes(
        self,
        resource,
        bucket,
        prefix,
        force_cache_refresh: bool,
    ) -> Iterator[Dict]:
        """
        Abstract over the S3 location and return a list of IO objects.

        :param prefix:
        :param bucket:
        :param resource:
        :param force_cache_refresh: When False, will use standard cache
            behaviour of checking if a value is in cache, then return from
            cache, else  make a real call. When True, will make a real call
            and replace the values in the cache.

        :return: Return type is really an iterator of s3.ObjectSummary, but
            s3.ObjectSummary is created by reflection so we cannot use type
            hinting.
        """
        logger.debug(
            'get_common_prefixes - start paginating s3 list from prefix to '
            'delimiter...',
            extra={
                'Bucket': bucket.name,
                'Prefix': prefix,
                'force_cache_refresh': force_cache_refresh,
            }
        )

        list_objects_func = memcached_method(
            lambda *_: self.hash_client,
            force_cache_refresh=force_cache_refresh,
            cache_func_name='list_objects_v2',
        )(resource.meta.client.list_objects_v2)

        delimiter = '/'
        start_after = None  # Used for pagination of S3 results.
        max_loops = 1000000  # Used to prevent infinite loops.
        i = 0

        while i < max_loops and True:
            i += 1  # Counter to prevent infinite loops.
            response: typing.Dict[str, str]

            if start_after:
                logger.debug(
                    'next page of s3 list results...',
                    extra={
                        'Bucket': bucket.name,
                        'Prefix': prefix,
                        'Delimiter': delimiter,
                        'start_after': start_after,
                        'force_cache_refresh': force_cache_refresh,
                    }
                )
                response = list_objects_func(
                    Bucket=bucket.name,
                    Prefix=prefix,
                    Delimiter=delimiter,
                    StartAfter=start_after,
                )
            else:
                # Initial loop
                logger.debug(
                    'start paginating s3 list...',
                    extra={
                        'Bucket': bucket.name,
                        'Prefix': prefix,
                        'Delimiter': delimiter,
                        'start_after': start_after,
                        'force_cache_refresh': force_cache_refresh,
                    }
                )
                response = list_objects_func(
                    Bucket=bucket.name,
                    Prefix=prefix,
                    Delimiter=delimiter,
                    # No StartAfter param in initial loop.,
                )

            response_as_dict: Dict = dict(response)

            # Remove the response metadata from the S3 list response as it
            # is different between requests because it contains the datetime
            # of the request and a unique request ID.
            if 'ResponseMetadata' in response_as_dict:
                del response_as_dict['ResponseMetadata']

            yield response_as_dict

            # Type could be horrible as it comes from a response.
            common_prefixes: Union[
                str,
                Dict[str, str],
                List[Dict[str, str]]
            ] = response.get('CommonPrefixes', [])

            last_prefix = None
            if common_prefixes:
                if isinstance(common_prefixes, str):
                    logger.warning(
                        'common prefix came back as a single string '
                        'instead of a list of dict which was unexpected '
                        'but was handled'
                    )
                    last_prefix = common_prefixes
                if isinstance(common_prefixes, Dict):
                    logger.warning(
                        'common prefix came back as a single dict '
                        'instead of a list of dict which was unexpected '
                        'but was handled',
                        extra={
                            'response first N chars': str(response)[:1000]
                        }
                    )
                    last_prefix = common_prefixes.get(
                        'Prefix',
                        None
                    )
                elif isinstance(common_prefixes, List):
                    # Example of common_prefixes structure:
                    #  [
                    #     {
                    #         "Prefix":
                    #             "short_code/as_of_date=2020-09-22/"
                    #     },
                    #     {
                    #         "Prefix":
                    #             "short_code/as_of_date=2020-09-23/"
                    #     }
                    # ]
                    for current_common_prefix in common_prefixes:
                        last_prefix = current_common_prefix.get(
                            'Prefix',
                            None
                        )
                else:
                    logger.error(
                        'type error for common_prefixes',
                        extra={
                            'common_prefixes': common_prefixes,
                            'type common_prefixes': type(common_prefixes),
                            'response first N chars': str(response)[:1000]
                        }
                    )
                    raise Exception(
                        'type error for common_prefixes - '
                        f'type: {type(common_prefixes)}, '
                        f'common_prefixes: {common_prefixes}'
                    )
            else:
                logger.debug(
                    'Zero common_prefixes',
                    extra={
                        'response first N chars': str(response)[:1000],
                    }
                )
                last_prefix = None

            if response.get('IsTruncated', False) and last_prefix:
                start_after = last_prefix
                logger.debug(
                    'Truncated response, so more results on the next '
                    'page',
                    extra={
                        'start_after': start_after,
                        'response first N chars': str(response)[:1000],
                    }
                )
            else:
                break

    # nonstatic
    def get_s3_list(
        self,
        resource,
        bucket_name: str,
        prefix: str,
        absolute_path: bool
    ) -> Iterator[S3PathDetails]:
        """
        S3 list everything in this bucket under this prefix.

        :param bucket:
        :param prefix: Tell s3-proxy/AWS S3 the exact folder from the S3 structure that you want to
          list inside:
          e.g. dataset-short-code/as_of_date=2019, or dataset-short-code/as_of_date
        :param absolute_path: True returns absolute path to the file on S3 proxy.
        :param bucket_name: The organisation short code is necessary as dataset short
          codes are NOT unique across different organisations.
        :return: S3 proxy path and size.
        """

        def __to_s3_dict(
                object_summary,
                absolute_path: bool,
                bucket_name: str,
        ) -> S3PathDetails:
            if absolute_path:
                key = f"s3://{bucket_name}/{object_summary.key}"
            else:
                key = object_summary.key

            return {
                'Key': key,
                'Size': object_summary.size,
                'LastModified': object_summary.last_modified,
                'ETag': object_summary.e_tag
            }


        logger.debug(f"Get S3 list for prefix '{prefix}'.")

        bucket = resource.Bucket(bucket_name)

        object_summaries = bucket.objects.filter(
            # Prefix searches for exact matches and folders
            Prefix=prefix
        )

        # Convert each object_summary into an S3 proxy path.
        for object_summary in object_summaries:
            if not object_summary.key.endswith('/') and int(object_summary.size) != 0:
                yield __to_s3_dict(
                    object_summary=object_summary,
                    absolute_path=absolute_path,
                    bucket_name=bucket_name
                )
            else:
                logger.debug(
                    'Skip zero size S3 path',
                    extra={
                        'key': object_summary.key,
                        'size': object_summary.size,
                    }
                )

    def get_s3_list_filter(
        self,
        resource,
        bucket_name: str,
        prefix: str,
        absolute_path: bool,
        prefix_filter_fn: typing.Callable[[Iterator[str]], Iterator[str]]
    ) -> typing.Generator[S3PathDetails, None, None]:
        """
        Top-level common prefix filtering. We need to prevent reading into
        hidden folders. In the case of Bilateral the latest folders are
        growing linearly and for us to do an iterative list and post filter
        out folders we do not want is taking too long on prod. We need to
        filter out at the common prefix level!

        :param resource:
        :param bucket:
        :param prefix: e.g. abc/as_of_date=2019, abc/as_of_date
        :param content_type: Structured/Unstructured
        :param load_type: Either None, "Incremental Load" or "Full Load". None
            should have the same behaviour as "Incremental Load".
        :param absolute_path: True returns absolute path to the file on S3 proxy.
        :param bucket_name:
        :return: S3 proxy path and size.
        """

        bucket = resource.Bucket(bucket_name)
        unique_common_prefixes: typing.Set[str] = set([])

        '''
         force_cache_refresh=True -- this is present simply because we do not have memcached on SDK - 
         we can remove and it will still do the real call, but lets be explicit
        '''
        common_prefixes_aws_responses: Iterator[Dict] = self.get_common_prefixes(
            resource=resource,
            bucket=bucket,
            prefix=prefix,
            force_cache_refresh=True
        )

        for aws_response in common_prefixes_aws_responses:
            common_prefixes = aws_response.get('CommonPrefixes', [])
            for cp in common_prefixes:
                unique_common_prefixes.add(cp['Prefix'])

        unique_non_hidden_common_prefixes = prefix_filter_fn(iter(unique_common_prefixes))

        for non_hidden_common_prefix in unique_non_hidden_common_prefixes:
            # To get a list of the contents call s3-proxy with
            # unique prefix plus partition
            # e.g. for
            #   abc/as_of_date
            # the S3 list could return:
            #   abc/as_of_date=2019/file.parquet
            #   abc/as_of_date=2020/file.parquet
            # why dont we cache this call?
            yield from self.get_s3_list(
                resource=resource,
                bucket_name=bucket_name,
                prefix=non_hidden_common_prefix,
                absolute_path=absolute_path
            )

    @staticmethod
    def convert_list_to_file_handles(
        resource,
        bucket_name,
        paths: Iterator[S3PathDetails]
    ) -> Iterator[S3File]:
        """
        List using caching. The intent is that this returns files for the
        `dataframe` and `partitions` endpoints, so we will be removing
        empty files and removing directories. This is NOT the behaviour you
        want for the S3 proxy, where you will want to view all of the files.

        :param resource:
        :param bucket:
        :param prefix:
        :param delimiter: Use with the `prefix` to do matching of path up to
            the delimiter.
        :param filter_out_directories: If True, remove any directories
            from the list so that it only returns files.
        :return: List of S3 files.
        """
        # There are two kinds of data in a datafile.files array. Absolute
        # paths. i.e. s3://bucket/prefix/userdata1.parquet and pointers
        # to folders  i.e s3://bucket/prefix/ which may contain part files
        # ending in 0001...000n. OR they may just contain general data.

        key: S3PathDetails
        try:
            for key in paths:
                # n.b. S3PathAndSize must be non-absolute for this method to work! (absolute_path=False)
                #
                yield S3File(
                    key_dict=key,
                    bucket_name=bucket_name,
                    get_object=resource.meta.client.get_object
                )
        except StopIteration:
            logger.debug("No more files in paths")

    @staticmethod
    def get_most_recent_common_prefix(
        common_prefixes: Iterator[str],
    ) -> List[str]:
        """
        This filtering logic only applies to Structured datasets. For a
        Structured dataset, we expect the first common prefix on S3 to be an
        `as_of_` representing when the data was published. It is expected to be
        in ISO 8601 format as this can be parsed into a Python DateTime.

        Return only the most recent `as_of` common prefix.

        :param common_prefixes: List of common prefixes for this dataset on S3.
        :return:  The most recent common_prefix for this dataset on S3. We return
            a collection because there is an edge case where there are common
            prefixes on S3 that do not have as_of, in which case
        """

        as_of_to_common_prefix: dict = defaultdict(list)
        as_of_warning_shown = False

        # Accumulate the `as_of_` dates from the common prefixes.
        for common_prefix in common_prefixes:
            partitions = {
                k.lower(): v for k, v in dict(
                    get_partitions_in_filepath(common_prefix)
                ).items()
            }

            # Partition cannot be filtered out if does not have an
            # `as_of_`. Get the first instance of a key that begins
            # with `as_of_`.
            as_of_key = next(
                (k for k, v in partitions.items()
                 if k.startswith('as_of_')),
                None
            )

            if not as_of_key:
                # There is not an `as_of_` in this common prefix!
                # Only show the message the first time, otherwise it will
                # spam the logs.
                if not as_of_warning_shown:
                    logger.warning(
                        'as_of_ not in partitions but load type is full, '
                        'so not filtering out this common prefix but will '
                        'consider it as having the oldest as_of_ possible.',
                        extra={
                            'common_prefix': common_prefix,
                        }
                    )
                    as_of_warning_shown = True

                as_of_to_common_prefix[
                    datetime.min
                ].append(common_prefix)
            else:
                # For a `load_type` = `Full Load` dataset, we only want
                # to return the data in the most recent `as_of_`
                # directory. We accumulate a dict of `as_of_` to
                # common_prefix, then at the end we know what the most recent
                # `as_of_` is and only return that common prefix.
                as_of_to_common_prefix[
                    isoparse(partitions[as_of_key])
                ].append(common_prefix)

        if as_of_to_common_prefix:
            # Return only the most recent common prefix.
            # To sort, we have to action the iterator and therefore the type
            # changes to a List.
            most_recent_as_of = sorted(
                as_of_to_common_prefix.keys()
            )[-1]
            logger.debug(
                'Load type is full, so returning most recent '
                f"as_of_ common prefix: '{most_recent_as_of}'"
            )
            return as_of_to_common_prefix[most_recent_as_of]
        else:
            # Edge case - the `load_type` is `Full Load` but
            # there are zero as_of_ keys, so return and empty list. The
            # code calling this filter will have to return a user
            # friendly error message about there being no files in the
            # dataset.
            # Alternatively, the cache might not be up to date causing
            # the most recent as_of_ to not be in the list.
            logger.warning(
                'Zero as_of_ keys in the partitions but load type is '
                'full. We may have returned some paths that did not '
                'have an as_of_ key in their common_prefix. Alternatively, '
                'we may need to wait for the cache to update.'
            )
            return []



    @staticmethod
    def filter_hidden_prefixes_by_dataset_content_and_load_type(
        content_type: str,
        load_type: str,
        prefix: str,
        unique_common_prefixes: Iterator[str]
    ) -> List[str]:

        unique_non_hidden_common_prefixes = set([])

        # Must be a iter type as we iterate more than once.
        non_hidden_common_prefixes: List[str] = sorted(set(
            [
                unique_common_prefix for unique_common_prefix in unique_common_prefixes
                if not is_hidden_based_on_path_and_content(_shorten(unique_common_prefix, prefix), content_type)
            ]
       ))
        # already clear of as_of= latest at this point

        logger.debug(
            f"load_type from Catalogue: '{load_type}'",
            extra={
                'load_type': load_type,
            }
        )

        if load_type == 'Full Load':
            # For a Structured dataset, we expect the first common prefix on S3
            # to be an `as_of` representing when the data was published.
            #
            # If the dataset's load type is "Full Load"
            # then return only data from the most recent `as_of` common prefix.
            unique_non_hidden_common_prefixes.update(S3DatasetHandler.get_most_recent_common_prefix(
                common_prefixes=iter(non_hidden_common_prefixes)
            ))
        else:
            # Else (if the dataset's load type is "Incremental Load" or None),
            # then we return data from all as_of common prefixes.

            for common_prefix in non_hidden_common_prefixes:
                # We are safe to do an S3 list efficiency of asking for `as_of` instead
                # of asking for every `as_of_*=value`. This reduces the number of calls
                # to S3 LIST.
                #
                # We do not need the entire path of each non-hidden
                # common prefix. We only need to know the prefix and the
                # partition name of the common prefix (if exists) knowing
                # it will not be a `.` or `_`. We do not want to keep the
                # unique value of the partition as that will cause use to
                # make an S3 call for each unique partition.
                # e.g. for common_prefix
                #     abc/as_of_date=2020-01-01
                # we only store
                #     abc/as_of_date
                # and so all the as_of_dates are collected in a single
                # S3 list operation with prefix starting abc/as_of_date.
                if '=' in common_prefix:
                    prefix_plus_partition, _ = common_prefix.split('=', 1)
                    unique_non_hidden_common_prefixes.add(prefix_plus_partition)
                else:
                    logger.warning("This dataset's top-level on S3 is not partitioned")
                    # Edge case where the top-level on S3 is not partitioned, so add the whole
                    # common prefix.
                    unique_non_hidden_common_prefixes.add(common_prefix)

        logger.debug(
            f'length of non_hidden_common_prefixes: '
            f'{len(non_hidden_common_prefixes)}'
            f'\nlength of unique_non_hidden_common_prefixes: '
            f'{len(unique_non_hidden_common_prefixes)}'
        )

        return sorted(set(unique_non_hidden_common_prefixes))

    def get_assumed_role_session(self, dataset: Dict):
        s2 = time.time()
        if 'location' in dataset['attributes'] and 's3' in dataset['attributes']['location']:
            logging.debug("Assuming: "+dataset['attributes']['location']['s3']['aws_role_arn'])
            session = self.create_session(
                role_arn=dataset['attributes']['location']['s3']['aws_role_arn']
            )
            s3 = time.time()
            logger.debug(f"STS {s3 - s2}")
            return session
        else:
            raise UnableToAccessDataset(
                details=(
                    'You do not have access to this dataset. You must '
                    'request access to the dataset\'s package.'
                )
            )

    def __repr__(self):
        return "S3DatasetHandler"