#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
import warnings
from typing import Dict

from dli.components import to_camel_cased_dict, _AttributeAdapter, object_to_namedtuple, to_snake_case_keys
from dli.models.dataset_model import DatasetModel

from platform_services_lib.lib.aspects.base_component import BaseComponent
from platform_services_lib.lib.services.exceptions import CatalogueEntityNotFoundException
from platform_services_lib.lib.context.urls import autoreg_urls


class AutoRegMetadata(BaseComponent):

    def set_auto_registration_metadata(
        self,
        dataset_id,
        path_template,
        name_template,
        as_of_date_template,
        active,
        sns_topic_for_s3_events,
        handle_files=False,
        has_auto_registry_failure_notifications=True
    ):
        """
        Submit a request to set up the auto registration metadata for a dataset.

        See description for each parameter, and whether they are optional or mandatory.

        :param str dataset_id: Dataset ID for which the auto registration metadata is being set up.
        :param str path_template: Path template for the files stored under the dataset.
        :param str name_template: Name template for the datafiles registered under the dataset.
        :param str as_of_date_template: As of date template for the datafiles registered under the dataset.
        :param bool active: Flag to indicate the auto registration status of the dataset
                            i.e. True => Active, False => Inactive or disabled
        :param str sns_topic_for_s3_events: Name of SNS topic where the S3 notification events are published when
                            files are added, updated or deleted from the S3 bucket for this dataset.
        :param bool handle_files: Optional. Flag to indicate whether the individual files (for e.g. parquet part files
                                    in case of a parquet dataset) are to be registered under the datafile for the dataset. Defaults to false.
        :param bool has_auto_registry_failure_notifications: Optional. Controls whether auto-registry sends email notifications on error. Defaults to true.
        :returns: Created auto registration metadata object.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # For example if the files for dataset id `xyz` are stored in the s3 bucket along
                `region=US/as_of_date=2019-02-18`

                client = dli.connect()
                auto_reg_metadata = client.set_auto_registration_metadata(
                    dataset_id="xyz",
                    path_template="region={{ region }}/as_of_date={{ year }}-{{ month }}-{{ day }}",
                    name_template="Datafile_name_{{ region }}_{{ year }}-{{ month }}-{{ day }}",
                    as_of_date_template="{{ year }}-{{ month }}-{{ day }}",
                    active=True,
                    sns_topic_for_s3_events='s3-notifications-sns-topic'
                )
        """
        warnings.warn(
            'Setting up the auto registration metadata for datasets will be '
            'deprecated. Please use register_dataset_metadata instead.',
            PendingDeprecationWarning
        )

        ds: Dict[str, DatasetModel] = self.datasets(search_term=[f"id={dataset_id}"])
        num_matches = len(ds)
        if num_matches == 0:
            raise CatalogueEntityNotFoundException(f"No such dataset ID `{dataset_id}`")
        elif num_matches > 1:
            # This should not be possible, but let's cover this scenario incase Caatlogue returns
            # bad data.
            raise Exception(f"More than one dataset with ID `{dataset_id}`")
        else:
            dataset: DatasetModel = list(ds.values())[0]

        fields = {
            'datasetId': dataset.dataset_id,
            'pathTemplate': path_template,
            'nameTemplate': name_template,
            'asOfDateTemplate': as_of_date_template,
            'active': active,
            'snsTopicForS3Events': sns_topic_for_s3_events,
            'handlePartFiles': handle_files,
            "hasAutoRegistryFailureNotifications": has_auto_registry_failure_notifications
        }

        payload = {k: v for k, v in fields.items() if v is not None}
        response_dict = self.session.post(
                    autoreg_urls.autoreg_index, json=payload
                ).json()
        obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        return obj

    def get_auto_registration_metadata(self, dataset_id=None, auto_reg_metadata_id=None):
        """
        Fetches the auto registration metadata for a dataset.

        :param str dataset_id: Optional. The dataset id for which auto registration metadata is being fetched.
                            Either this or auto_reg_metadata_id is required for the look up
        :param str auto_reg_metadata_id: Optional. The id of the auto registration metadata.
                            Either this or dataset_id is required for the look up
        :returns: The auto registration metadata object.
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # Look up by dataset id
                client = dli.connect()
                auto_reg_metadata = client.get_auto_registration_metadata('my_dataset_id')

                # If auto reg metadata id is known
                auto_reg_metadata = client.get_auto_registration_metadata(auto_reg_metadata_id='my_auto_reg_id')
        """
        warnings.warn(
            'Auto registration of datasets will be deprecated.',
            PendingDeprecationWarning
        )
        if dataset_id and auto_reg_metadata_id:
            return self._get_auto_reg_metadata(
                    auto_reg_metadata_id=auto_reg_metadata_id,
                    dataset_id=dataset_id
                )

        elif auto_reg_metadata_id:
            return self._get_auto_reg_metadata(
                    auto_reg_metadata_id=auto_reg_metadata_id
                )

        elif dataset_id:
            return self._get_auto_reg_metadata(
                    dataset_id=dataset_id
                )

        raise ValueError(
            "Either dataset id or auto reg metadata id must be specified "
            "to look up auto registration details for the dataset")

    def _get_auto_reg_metadata(self, **kwargs):
        response_dict = self.session.get(
            autoreg_urls.autoreg_index, params=kwargs
        ).json()
        obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        return obj

    def edit_auto_registration_metadata(
        self,
        auto_reg_metadata_id,
        path_template=None,
        name_template=None,
        as_of_date_template=None,
        active=None,
        sns_topic_for_s3_events=None,
        handle_files=None,
        has_auto_registry_failure_notifications=None
    ):
        """
        Edits existing auto registration metadata for a dataset.
        Fields passed as ``None`` will retain their original value.

        :param str auto_reg_metadata_id: The id of the auto registration metadata we want to modify.
        :param str path_template: Optional. Path template for the files stored under the dataset.
        :param str name_template: Optional. Name template for the datafiles registered under the dataset.
        :param str as_of_date_template: Optional. As of date template for the datafiles registered under the dataset.
        :param bool active: Optional. Boolean flag to indicate the auto registration status of the dataset
                            i.e. True => Active, False => Inactive or disabled
        :param str sns_topic_for_s3_events: Optional. Name of SNS topic where the S3 notification events are published when
                            files are added, updated or deleted from the S3 bucket for this dataset.
        :param bool handle_files: Optional. Flag to indicate whether the individual files (for e.g. parquet part files
                                    in case of a parquet dataset) are to be registered under the datafile for the dataset.
        :param bool has_auto_registry_failure_notifications: Optional. Controls whether auto-registry sends email notifications on error.
        :returns: Updated auto registration metadata object
        :rtype: collections.namedtuple

        - **Sample**

        .. code-block:: python

                # For example edit metadata to make it inactive

                client = dli.connect()
                updated_auto_reg_metadata = client.edit_auto_registration_metadata(
                    auto_reg_metadata_id="test-auto-reg-metadata-id",
                    active=False
                )
        """
        warnings.warn(
            'Auto registration of datasets will be deprecated. '
            'Please use update_dataset_metadata instead.',
            PendingDeprecationWarning
        )
        auto_reg_metadata = self._get_auto_reg_metadata(auto_reg_metadata_id=auto_reg_metadata_id)


        fields = {
            'datasetId': auto_reg_metadata.dataset_id,
            'pathTemplate': path_template,
            'nameTemplate': name_template,
            'asOfDateTemplate': as_of_date_template,
            'active': active,
            'snsTopicForS3Events': sns_topic_for_s3_events,
            'handlePartFiles': handle_files,
            "hasAutoRegistryFailureNotifications": has_auto_registry_failure_notifications
        }

        # clean up any unknown fields, and update the entity
        auto_reg_metadata_dict = to_camel_cased_dict(auto_reg_metadata.as_dict())
        for key in list(auto_reg_metadata_dict.keys()):
            if key not in fields:
                del auto_reg_metadata_dict[key]

        payload = {k: v for k, v in fields.items() if v is not None}
        auto_reg_metadata_dict.update(payload)

        # perform the update and return the resulting entity
        response_dict = self.session.put(
            autoreg_urls.autoreg_instance.format(id=auto_reg_metadata_id),
            json=auto_reg_metadata_dict
        ).json()
        obj = type(response_dict['class'][0], (_AttributeAdapter,), to_snake_case_keys(response_dict["properties"]))()
        return object_to_namedtuple(obj)

    def delete_auto_registration_metadata(self, auto_reg_metadata_id):
        """
        Marks auto registration metadata as deleted.

        :param str auto_reg_metadata_id: the id for the metadata we want to delete.

        :returns: None

        - **Sample**

        .. code-block:: python

                client = dli.connect()
                client.delete_auto_registration_metadata(auto_reg_metadata_id)
        """
        warnings.warn(
            'Auto registration of datasets will be deprecated.',
            PendingDeprecationWarning
        )

        self.session.delete(
            autoreg_urls.autoreg_instance.format(id=auto_reg_metadata_id),
        )
