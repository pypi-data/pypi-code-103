#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import copy
import json
import os
from requests_toolbelt import MultipartEncoder

from dli.components import _AttributeAdapter, to_snake_case_keys

from platform_services_lib.lib.aspects.base_component import BaseComponent
from platform_services_lib.lib.services.exceptions import CatalogueEntityNotFoundException
from platform_services_lib.lib.context.urls import dataset_urls

TEN_MEGABYTES = 10485760


class DatasetBuilder:
    """
    Dataset is grouping of related datafiles. It provides user with metadata required to consume and use the data.

    This builder object sets sensible defaults and exposes
    helper methods on how to configure its storage options..

    :param str package_id: Package ID to which the dataset belongs to.
    :param str name: A descriptive name of the dataset. It should be unique within the package the dataset
                    belongs to.
    :param str description: A short description of the dataset.
    :param str content_type: A way for the data steward to classify the type of data in the dataset
                        (e.g. Structured or Unstructured).
    :param str data_format: The format of the data: `CSV`, `IMAGE`, `JSON`, `PARQUET`, `TXT`, `TSV`,`XML`, `Other`.
    :param str publishing_frequency: The internal on which data is published. Possible values are: `Hourly`,
                                        `Daily`, `Weekday`, `Weekly`, `Monthly`, `Quarterly`, `Yearly`, `Not Specified`.
    :param list[str] taxonomy: A list of segments to be used for a taxonomy,
                                    the Data-<< Organization >>-<< topic >> prefix will be applied by the catalogue  For
                                    a taxonomy of Data-IHS Markit-Financial Markets-Credit-CDS, you would provide
                                    `taxonomy=["Credit", "CDS"]`
    :param str short_code: Optional. A short code for the dataset, should be an alphanumerical camel-cased string.
                        If not provided, a short_code will be generated based on the name.
    :param list[str] keywords: Optional. User-defined list of separated keywords that can be used to find this dataset
                            through the search interface.
    :param str naming_convention: Optional. Key for how to read the dataset name.
    :param str documentation: Optional. Documentation about this dataset in markdown format.
    :param str load_type: Optional. Whether each datafile in this dataset should be considered as a full version of a
                        dataset or a delta or increment. Accepted types are `Full Load`, `Incremental Load`
    :param str has_datafile_monitoring: Optional. Notify when latest instance is missing
    :param bool details_visible_to_lite_users: Optional. Default value "False".
    :param str data_preview_type: Optional enum of NONE STATIC LIVE. 'NONE' means there is no datapreview. STATIC means to use the file provided. LIVE means to use the latest datafile.
    :param file sample_data: Optional file. File like object. Used in conjuntion with data_preview_type.
    """

    @staticmethod
    def _create_dliv1_payload(
        package_id=None,
        name=None,
        description=None,
        content_type=None,
        data_format=None,
        publishing_frequency=None,
        taxonomy=None,
        keywords=None,
        naming_convention=None,
        documentation=None,
        load_type=None,
        has_datafile_monitoring=None,
        details_visible_to_lite_users=None,
        **kwargs
    ):
        return {
            "packageId": package_id,
            "name": name,
            "description": description,
            "keywords": keywords,
            "contentType": content_type,
            "location": None,
            "dataFormat": data_format,
            "publishingFrequency": publishing_frequency,
            "namingConvention": naming_convention,
            "documentation": documentation,
            "taxonomy": taxonomy,
            "loadType": load_type,
            "has_datafile_monitoring": has_datafile_monitoring,
            "details_visible_to_lite_users": details_visible_to_lite_users,
        }

    def __init__(self, location_builder=None, **kwargs):
        self._data = dict(kwargs)

        self._data['sample_data'] = self._data.get('sample_data')
        if self._data.get('sample_data'):
            self._data['data_preview_type'] = (
                    self._data.get('data_preview_type') or 'STATIC'
            )
            self._validate_preview_type_static(
                self._data.get('data_preview_type')
            )

        # this is just for DLI v1 TODO add deprecated to it.
        self.payload = self._create_dliv1_payload(**self._data)
        self._location_builder = location_builder

    def to_json_api(self):
        attributes = dict(**self._data)
        if self._location_builder is not None:
            attributes.update(**self._location_builder._dliv2())

        # This is a file
        attributes.pop('sample_data', None)
        return {
            'type': 'dataset',
            'data': {'attributes': attributes}
        }

    def to_multipart_body(self):
        data = json.dumps(self.to_json_api())

        fields={
            'data': ('data', data, 'application/json'),
        }

        if self._data['sample_data']:
            fields['sample_data'] = (
                os.path.basename(self._data['sample_data'].name),
                self._data['sample_data'],
                # Mimetyppe is ignored
                'text/plain'
            )

        encoder = MultipartEncoder(fields=fields)

        # NOTE this really should be fixed on the catalogue as well.
        # the way to handle this and deliver an error message more
        # graceful than an arbitary socket closure is for the catalogue
        # to reject the requests with a 'Content-Length' header that's
        # too large.
        if encoder.len > (TEN_MEGABYTES - len(data)):
            raise ValueError(
                f'The sample_data file passed to the'
                ' DatasetBuilder is too large. Please '
                'keep files under 10 megabytes.'
            )

        return encoder

    def with_external_s3_storage(
        self,
        bucket_name,
        aws_account_id,
        prefix
    ):
        """
        Indicate that the dataset will be stored
        in a self-managed S3 bucket outside of the Data Lake.

        :param str bucket_name: Name of the bucket you want to link to this dataset.
        :param str aws_account_id: The AWS account id where this bucket currently resides.
                                   This account needs to be registed on the data lake previously
                                   and your account should have permissions to use it.
        :param str prefix: A valid path that specifies the absolute parent
                           for files in this dataset.
                           This value will be used when issuing access tokens so
                           it is essential that it is as constrained as possible.
                           Cannot end with slash ("/").
        :returns: DatasetBuilder (itself)
        :rtype: dli.client.components.dataset.DatasetBuilder

        - **Sample**

        .. code-block:: python

                from dli.components.dataset import DatasetBuilder

                builder = DatasetBuilder(
                                package_id="package-id",
                                name="my test dataset",
                                description="My dataset description",
                                content_type="Structured",
                                data_format="CSV",
                                publishing_frequency="Weekly",
                                taxonomy=["Credit", "CDS"]
                                data_preview_type='STATIC',
                                sample_data=open('path/to/my/file.csv')
                        )
                builder = builder.with_external_s3_storage(
                    bucket_name="external-s3-bucket-name",
                    aws_account_id=123456789,
                    prefix="/economic-data-package/my-test-dataset"
                )
                client = dli.connect()
                dataset = client.register_dataset(builder)
        """
        self._location_builder = DatasetLocationBuilder().with_external_s3_storage(
            bucket_name=bucket_name,
            aws_account_id=aws_account_id,
            prefix=prefix
        )
        self.payload.update(self._location_builder.build())
        return self

    def with_external_storage(self, location):
        """
        Allows specifying a non S3 location where
        the dataset resides.

        The location will be kept for informational purposes only.

        :param str location: A connection string or identifier where the dataset resides.

        :returns: DatasetBuilder (itself)
        :rtype: dli.client.components.dataset.DatasetBuilder

        - **Sample**

        .. code-block:: python

                from dli.components.dataset import DatasetBuilder

                builder = DatasetBuilder(
                                package_id="package-id",
                                name="my test dataset",
                                description="My dataset description",
                                content_type="Structured",
                                data_format="CSV",
                                publishing_frequency="Weekly",
                                taxonomy=["Credit", "CDS"]
                        )
                builder = builder.with_external_storage("external-storage-location")
                dataset = client.register_dataset(builder)
        """
        self._location_builder = DatasetLocationBuilder().with_external_storage(location)
        self.payload.update(self._location_builder.build())
        return self

    def build(self):
        return copy.copy(self.payload)

    @staticmethod
    def _validate_preview_type_static(preview_type):
        if preview_type != 'STATIC':
            raise ValueError(
                'Field: data_preview_type must be STATIC when '
                'sample_data is provided'
            )


class DatasetLocationBuilder:
    """
        A simple builder to specify dataset location.
    """

    def __init__(self):
        self.payload = {}

    def with_external_s3_storage(
        self,
        bucket_name,
        aws_account_id,
        prefix
    ):
        """
        Indicate that the dataset will be stored
        in a self-managed S3 bucket outside of the Data Lake.

        :param str bucket_name: Name of the bucket you want to link to this dataset.
        :param str aws_account_id: The AWS account id where this bucket currently resides.
                                   This account needs to be registed on the data lake previously
                                   and your account should have permissions to use it.
        :param str prefix: A vaild path that specifies the absolute parent
                           for files in this dataset.
                           This value will be used when issuing access tokens so
                           it is essential that it is as constrained as possible.
                           Cannot end with slash ("/").

        :returns: DatasetBuilder (itself)
        :rtype: dli.client.components.dataset.DatasetLocationBuilder

        - **Sample**

        .. code-block:: python

                from dli.components.dataset import DatasetLocationBuilder

                location_builder = DatasetLocationBuilder().with_external_s3_storage(
                        bucket_name="external-s3-bucket-name",
                        aws_account_id=123456789,
                        prefix="/economic-data-package/my-test-dataset"
                    )
                # Build the location object
                location = location_builder.build()
        """
        self.payload["location"] = {
            "type": "S3",
            "owner": {
                "awsAccountId": str(aws_account_id)
            },
            "bucket": bucket_name,
            "prefix": prefix
        }
        return self

    def with_external_storage(self, location):
        """
        Allows specifying a non S3 location where
        the dataset resides.

        The location will be kept for informational purposes only.

        :param str location: A connection string or identifier where the dataset resides.

        :returns: DatasetBuilder (itself)
        :rtype: dli.client.components.dataset.DatasetLocationBuilder

        - **Sample**

        .. code-block:: python

                from dli.components.dataset import DatasetLocationBuilder

                location_builder = DatasetLocationBuilder().with_external_storage("external-storage-location")
                # Build the location object
                location = location_builder.build()
        """
        self.payload["location"] = {
            "type": "Other",
            "source": location
        }
        return self

    def _dliv2(self):
        """
        The old API used a polymorphic location type.
        The new API uses keys. While more simple we
        have to handle both cases.
        """
        data = {}
        location = None if 'location' not in self.payload else self.payload['location']
        if location and location['type'] == 'S3':
            data['location'] = {
                's3': copy.copy(self.payload['location'])
            }

            if 'owner' in data['location']['s3']:
                data['location']['s3']['owner']['aws_account_id'] = (
                    # Is camel cased in old API but not new api...
                    data['location']['s3']['owner'].pop('awsAccountId')
                )
        else:
            data['location'] = {
                'other': copy.copy(self.payload['location'])
            }

        return data

    def build(self):
        return copy.copy(self.payload)


def ensure_count_is_valid(count):
    count = int(count)
    if count <= 0:
        raise ValueError("`count` should be a positive integer")


# utilities above


class Dataset(BaseComponent):

    def get_s3_access_keys_for_dataset(self, *dataset_ids):
        """
        Retrieve S3 access keys for the specified account to access the
        specified dataset(s).

        :param list dataset_ids: One ore more dataset ids to get access to.
        :returns: A namedtuple containing the AWS keys and session token.
        :rtype: list[collections.namedtuple]

        - **Sample**

        .. code-block:: python

                s3_access_keys = client.get_s3_access_keys_for_dataset(dataset_id1, dataset_id2)
                # print(s3_access_keys)
                # access_key(access_key_id='39D19A440AFE452B9', secret_access_key='F426A93CDECE45C9BFF8F4F19DA5CB81', session_token='C0CC405803F244CA99999')

        """


        payload = {"datasetIds": list(dataset_ids)}

        response = self.session.post(
            dataset_urls.access_keys, json=payload
        )

        response_dict = response.json()
        obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        return obj

    def _get_dataset_id_by_name(self, package_id=None,
                                dataset_name=None,
                                package_name=None):
        if dataset_name and package_name:
            params = {"name": package_name}

            p = self.packages(search_term=[f"name={package_name}"])
            if len(p) == 1:
                package_id = p[package_name].id
            else:
                raise CatalogueEntityNotFoundException("No such package")

        ds = self.datasets(search_term=[f"package_id={package_id}",
                                        f"name={dataset_name}"], warn=False)
        try:
            return next(iter(ds.values())).id
        except StopIteration as s:
            raise Exception(f"No such dataset `{dataset_name}`")

    def register_dataset(self, builder: DatasetBuilder):
        """
        Submit a request to create a new dataset under a specified package in the Data Catalogue.

        :param dli.client.components.dataset.DatasetBuilder builder: An instance of DatasetBuilder. This builder object sets sensible defaults and exposes
                                                           helper methods on how to configure its storage options.

        :returns: A newly created Dataset.
        :rtype: Dataset

        - **Sample**

        .. code-block:: python

                # Please refer to builder docs for examples on
                # how to create an instance of DatasetBuilder.
                client = dli.connect()
                dataset = client.register_dataset(builder)
        """
        mp_encoder = builder.to_multipart_body()

        result = self.session.post(
            dataset_urls.v2_index,
            data=mp_encoder,
            headers={
                'Content-Type': mp_encoder.content_type,
                'Content-Length': str(mp_encoder.len),
            },
        ).json()

        return self._DatasetFactory._from_v2_response(result)

    def edit_dataset(
        self,
        dataset_id,
        location_builder=None,
        **kwargs
    ):
        """
        Updates information on a dataset, returning the updated instance.
        If keyword argument is not specified field keeps its old value.
        Optional enum and text type fields can be unset by passing ``None``.

        :param str dataset_id: Id of the dataset being updated.
        :param DatasetLocationBuilder location_builder: Optional. An instance of DatasetLocationBuilder. This builder object exposes
                                                                            helper methods to configure dataset storage options.

        Keyword arguments:

        :keyword str name: Optional. A descriptive name of a dataset. It should be unique within the package.
        :keyword str description: Optional. A short description of a package.
        :keyword str content_type: Optional. A way for the data steward to classify the type of data in the dataset
                                (e.g. Structured or Unstructured).
        :keyword str data_format: Optional. The format of the data: `CSV`, `IMAGE`, `JSON`, `PARQUET`, `TXT`, `TSV`, XML`, `Other`.
        :keyword str publishing_frequency: Optional. The internal on which data is published. Possible values are: `Hourly`,
                                        `Daily`, `Weekday`, `Weekly`, `Monthly`, `Quarterly`, `Yearly`, `Not Specified`.
        :keyword list[str] keywords: Optional. User-defined list of keywords that can be used to find this dataset through
                                    the search interface.
        :keyword str naming_convention: Optional. Key for how to read the dataset name.
        :keyword str documentation: Optional. Documentation about this dataset in markdown format.
        :keyword list[str] taxonomy: Optional. A list of segments to be used for a taxonomy,
                                    the Data-<< Organization >>-<< topic >> prefix will be applied by the catalogue  For
                                    a taxonomy of Data-IHS Markit-Financial Markets-Credit-CDS, you would provide
                                    `taxonomy=["Credit", "CDS"]`
        :keyword str load_type: Optional. Whether each datafile in this dataset should be considered as a full version
                                of a dataset or a delta or increment. Accepted types are `Full Load`, `Incremental Load`
        :keyword str data_preview_type: Optional enum of NONE STATIC LIVE. 'NONE' means there is no datapreview. STATIC means
                            to use the file provided. LIVE means to use the latest datafile.
        :keyword file sample_data: Optional file. File like object. Used in conjuntion with data_preview_type. Max size 10Megabytes.
        :keyword bool details_visible_to_lite_users: Optional. Default value "False".
        :keyword bool sql_enabled: Optional. Default value "False".


        :returns: Updated Dataset.
        :rtype: Dataset

        - **Sample**

        .. code-block:: python

                # e.g. update dataset description
                client = dli.connect()
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    description="Updated my dataset description"
                )

                # update dataset location. Please note that this is only allowed if the dataset has no datafiles registered.
                builder = DatasetLocationBuilder().with_external_storage("external-storage-location")
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    location_builder=builder
                )

                # update dataset taxonomy
                updated_dataset = client.edit_dataset(
                    "my-dataset-id",
                    taxonomy=["Credit", "CDS"]
                )

        """
        builder = DatasetBuilder(
            location_builder=location_builder,
            **kwargs
        )

        mp_encoder = builder.to_multipart_body()
        result = self.session.patch(
            dataset_urls.v2_by_id.format(id=dataset_id), data=mp_encoder,
            headers={
                'Content-Type': mp_encoder.content_type,
                'Content-Length': str(mp_encoder.len),
            }
        ).json()

        return self._DatasetFactory._from_v2_response(result)

    def delete_dataset(self, dataset_id):
        """
        Marks a particular dataset (and all its datafiles) as deleted.
        This dataset will no longer be accessible by consumers.

        :param str dataset_id: The id of the dataset to be deleted.

        :returns: None

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                client.delete_dataset(dataset_id)

        """
        self.session.delete(
            dataset_urls.v2_by_id.format(id=dataset_id)
        )

    def get_datafiles(self, dataset_id, name_contains=None,
                      as_of_date_start=None, as_of_date_end=None,
                      page=1, count=100):
        """
        Returns a list of all datafiles registered under a dataset.

        :param str dataset_id: The id of the dataset.
        :param str name_contains: Optional. Look up only those datafiles for the dataset where name contains this string.
        :param str as_of_date_start: Optional. Datafiles having data_as_of date greater than or equal to this date. This must be specified in YYYY-MM-DD format.
        :param str as_of_date_end: Optional. Datafiles having data_as_of date less than or equal to this date. This must be specified in YYYY-MM-DD format.
        :param int page: Optional. The page to start retrieving from and ascending per internal paging. Defaults to 1.
        :param int count: Optional. The count of datafiles to be returned per internal paging. Defaults to 100.

        :returns: List of all datafiles registered under the dataset.
        :rtype: List[Datafile]

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                datafiles = client.get_datafiles(
                    dataset_id,
                    name_contains='My Test Data',
                    as_of_date_start='2018-10-11',
                    as_of_date_end='2018-10-15',
                    count=10
                )
        """

        ensure_count_is_valid(count)

        params = {
            'name': name_contains,
            'as_of_date_start': as_of_date_start,
            'as_of_date_end': as_of_date_end,
            'page_size': count,
            'page': page,
        }

        response_dict = self.session.get(
            dataset_urls.datafiles.format(id=dataset_id), params=params
        ).json()
        obj = [type('datafile', (_AttributeAdapter,), to_snake_case_keys(x["properties"]))()
                for x in response_dict['entities'] if x['rel'] == 'datafile']
        return obj

    def get_latest_datafile(self, dataset_id):
        """
        Fetches datafile metadata of latest datafile in the dataset.

        :param str dataset_id: The id of the dataset.

        :returns: The datafile.
        :rtype: Datafile

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                datafile = client.get_latest_datafile(dataset_id)
        """
        response_dict = self.session.get(
                dataset_urls.latest_datafile.format(id=dataset_id)).json()

        obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        return obj

