import logging
from typing import List

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.models.resource_list import SummaryList
from cognite.well_model.models import DurationRange, MeasurementType, MeasurementTypeItems, SummaryCount, SummaryItems

logger = logging.getLogger(__name__)


class SummariesAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)

    def welltypes(self) -> SummaryList:
        """Get all well types

        Returns:
            SummaryList: list of well types
        """
        output: SummaryList = self._summary("welltypes")
        return output

    def measurement_types(self) -> List[MeasurementType]:
        """Get all active measurement types

        Returns:
            List[MeasurementType]: A list of measurement types that are in use
        """
        path: str = self._get_path("/summaries/measurementtypes")
        response: Response = self.client.get(url_path=path)
        items: List[MeasurementType] = MeasurementTypeItems.parse_raw(response.text).items
        return items

    def npt_codes(self) -> SummaryList:
        """Get all Npt codes

        Returns:
            SummaryList: list of Npt codes
        """
        # For some reason I need to be explicit about types here.
        output: SummaryList = self._summary("npt/codes")
        return output

    def npt_detail_codes(self) -> SummaryList:
        """Get all Npt detail codes

        Returns:
            SummaryList: list of Npt detail codes
        """
        output: SummaryList = self._summary("npt/detailcodes")
        return output

    def npt_durations(self) -> DurationRange:
        """Get the minimum and maximum NPT duration

        Returns:
            DurationRange: describing min and max duration
        """
        path: str = self._get_path("/summaries/npt/durations")
        response: Response = self.client.get(url_path=path)
        return DurationRange.parse_raw(response.text)

    def nds_risk_types(self) -> SummaryList:
        """Get all Nds risk types

        Returns:
            SummaryList: list of Nds risk types
        """
        output: SummaryList = self._summary("nds/risktypes")
        return output

    def _summary(self, route: str) -> SummaryList:
        path: str = self._get_path(f"/summaries/{route}")
        response: Response = self.client.get(url_path=path)
        items: List[SummaryCount] = SummaryItems.parse_raw(response.text).items
        return SummaryList(items)
