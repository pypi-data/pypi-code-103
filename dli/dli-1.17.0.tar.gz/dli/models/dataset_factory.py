#
# Copyright (C) 2020 IHS Markit.
# All Rights Reserved
#
from deprecated import deprecated

from platform_services_lib.lib.context.urls import dataset_urls

class DatasetFactory:

    @classmethod
    @deprecated
    def _from_v1_response_to_v2(cls, v1_response):
        response = cls._client.session.get(
            dataset_urls.v2_by_id.format(
                id=v1_response['properties']['datasetId']
            )
        )

        return cls._from_v2_response(response.json())

    @classmethod
    def _from_v2_response(cls, response_json, warn=False, page_size=25):
        return cls._construct_dataset_using(
            response_json['data']['attributes'], response_json['data']['id'], warn, page_size=page_size,
        )

    @classmethod
    def _from_v2_response_unsheathed(cls, response_json, warn=False, page_size=25):
        return cls._construct_dataset_using(
            response_json['attributes'], response_json['id'], warn, page_size=page_size,
        )

    @classmethod
    def _from_v2_list_response(cls, response_json, page_size=25):
        return [
            cls._construct_dataset_using(
                dataset['attributes'], dataset['id'], page_size=page_size,
            )
            for dataset in response_json['data']
        ]

    @classmethod
    def _construct_dataset_using(cls, attributes, dataset_id, warn=False, page_size=25):
        # In the interests of not breaking backwards compatability.
        # TODO find a way to migrate this to the new nested API.
        if 'location' in attributes:
            location = attributes.pop('location')
            # Note: flattens 's3' field in 'location' - old behaviour we have to keep in order to preserve consumption and sql
            if location is not None:
                location = location[next(iter(location))]
                attributes['location'] = location

        if attributes["content_type"] == "Unstructured":
            return cls._client._Unstructured(
                **attributes,
                dataset_id=dataset_id,
                warn=warn
            )
        else:
            return cls._client._Structured(
                **attributes,
                page_size=page_size,
                dataset_id=dataset_id
            )
