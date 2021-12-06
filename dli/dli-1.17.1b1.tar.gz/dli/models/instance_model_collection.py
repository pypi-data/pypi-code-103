import warnings
from typing import List

from dli.models.instance_model import InstanceModel

from platform_services_lib.lib.adapters.pagination_adapters import Paginator
from platform_services_lib.lib.context.urls import dataset_urls
from platform_services_lib.lib.aspects.decorators import analytics_decorator, logging_decorator, log_public_functions_calls_using
from platform_services_lib.lib.services.dlc_attributes_dict import AttributesDict


class InstanceModelCollection(AttributesDict):

    def __init__(self, dataset=None, page_size=25):
        self._dataset = dataset
        self._paginator = Paginator(
            dataset_urls.datafiles.format(id=self._dataset.id),
            self._client._Instance, self._client._Instance._from_v1_entity,
            page_size=page_size,
        )

    def latest(self) -> InstanceModel:
        """:return: The latest instance."""
        response = self._client.session.get(
            dataset_urls.latest_datafile.format(id=self._dataset.id)
        ).json()

        return self._client._Instance._from_v1_entity(response)

    def all(self) -> List[InstanceModel]:
        """:return: All the instances."""
        warnings.warn(
            'The result of calling `.all` will be cached. If you want fresh '
            'results the next time you call `.all`, then please re-create the '
            'dataset variable before calling `.all`.'
        )
        yield from self._paginator

log_public_functions_calls_using(
    [analytics_decorator, logging_decorator],
    class_fields_to_log=['_dataset.dataset_id']
)(InstanceModelCollection)

