import logging
from typing import List, Optional

from requests import Response

from cognite.well_model.client._api_client import APIClient
from cognite.well_model.client.api.api_base import BaseAPI
from cognite.well_model.client.api.merge_rules.wells import WellMergeRulesAPI
from cognite.well_model.client.models.property_filter import PropertyFilter, filter_to_model
from cognite.well_model.client.models.resource_list import WellList
from cognite.well_model.client.utils._identifier_list import identifier_items, identifier_items_single
from cognite.well_model.client.utils.constants import DEFAULT_LIMIT
from cognite.well_model.client.utils.multi_request import cursor_multi_request
from cognite.well_model.models import (
    AssetSource,
    DateRange,
    DeleteWells,
    DistanceRange,
    IdentifierItems,
    PolygonFilter,
    Well,
    WellDepthMeasurementFilter,
    WellFilter,
    WellFilterRequest,
    WellIngestion,
    WellIngestionItems,
    WellItems,
    WellNdsFilter,
    WellNptFilter,
    WellSearch,
    WellTimeMeasurementFilter,
    WellTopFilter,
    WellTrajectoryFilter,
)

logger = logging.getLogger(__name__)


class WellsAPI(BaseAPI):
    def __init__(self, client: APIClient):
        super().__init__(client)
        self.merge_rules = WellMergeRulesAPI(client)

    def ingest(self, ingestions: List[WellIngestion]) -> WellList:
        """Ingest wells

        Args:
            ingestions (List[WellIngestion]): List of WellIngestions

        Returns:
            List[Well]: List of wells
        """
        path = self._get_path("/wells")
        json = WellIngestionItems(items=ingestions).json()
        response: Response = self.client.post(path, json)
        well_items: WellItems = WellItems.parse_obj(response.json())
        items: List[Well] = well_items.items
        return WellList(items)

    def delete(self, well_sources: List[AssetSource]):
        path = self._get_path("/wells/delete")
        json = DeleteWells(items=well_sources).json()
        self.client.post(path, json)

    # guranteed to be non-empty list
    def _retrieve_multiple(self, identifiers: IdentifierItems) -> List[Well]:
        path: str = self._get_path("/wells/byids")
        response: Response = self.client.post(url_path=path, json=identifiers.json())
        wells: List[Well] = WellItems.parse_raw(response.text).items
        return wells

    def retrieve(self, asset_external_id: Optional[str] = None, matching_id: Optional[str] = None) -> Well:
        """Get well by asset external id or matching id

        Args:
            asset_external_id (str, optional)
            matching_id (str, optional)
        Returns:
            Well:
        Raises:
            CogniteAPIError: If well is not found
        Examples:
            Get well by asset external id
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> well = wm.wells.retrieve(asset_external_id="EDM:15/9-F-15")

            Get well by matching_id
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> well = wm.wells.retrieve(matching_id="15/9-F-15")
        """
        identifiers = identifier_items_single(asset_external_id, matching_id)
        return self._retrieve_multiple(identifiers)[0]

    def retrieve_multiple(
        self, asset_external_ids: Optional[List[str]] = None, matching_ids: Optional[List[str]] = None
    ) -> WellList:
        """Get wells by a list of asset external ids and matching ids

        Args:
            asset_external_ids: list of well asset external ids
            matching_ids: List of well matching ids
        Returns:
            List[Well]: List of wells
        """
        identifiers = identifier_items(asset_external_ids, matching_ids)
        return WellList(self._retrieve_multiple(identifiers))

    def list(
        self,
        string_matching: Optional[str] = None,
        quadrants: PropertyFilter = None,
        regions: PropertyFilter = None,
        blocks: PropertyFilter = None,
        fields: PropertyFilter = None,
        operators: PropertyFilter = None,
        sources: Optional[List[str]] = None,
        water_depth: Optional[DistanceRange] = None,
        datum: Optional[DistanceRange] = None,
        spud_date: Optional[DateRange] = None,
        well_types: PropertyFilter = None,
        licenses: PropertyFilter = None,
        trajectories: Optional[WellTrajectoryFilter] = None,
        depth_measurements: Optional[WellDepthMeasurementFilter] = None,
        time_measurements: Optional[WellTimeMeasurementFilter] = None,
        npt: Optional[WellNptFilter] = None,
        nds: Optional[WellNdsFilter] = None,
        polygon: Optional[PolygonFilter] = None,
        output_crs: Optional[str] = None,
        well_tops: Optional[WellTopFilter] = None,
        limit: Optional[int] = DEFAULT_LIMIT,
    ) -> WellList:
        """Get wells that matches the filter

        The result of this request is a list of wells with wellbores. If you are
        filtering only on well data, then each well in the response will contain
        all its wellbores. However, if you are filtering on *wellbore data*
        (trajectories, depth and time measurements, npt, nds, and well tops),
        then each well will only contain the wellbores that matched the request.

        Args:
            string_matching (Optional[str], optional): Fuzzy match on description and name.
            quadrants (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of quadrants or :class:`~cognite.well_model.NotSet`
            regions (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of regions or :class:`~cognite.well_model.NotSet`
            blocks (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of blocks or :class:`~cognite.well_model.NotSet`
            fields (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of fields or :class:`~cognite.well_model.NotSet`
            operators (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of operators or :class:`~cognite.well_model.NotSet`
            sources (Optional[List[str]], optional): List of sources on wells
            water_depth (Optional[DistanceRange], optional):
            datum: Optional[DistanceRange] optional,: Distance range for datum of the wells
            spud_date (Optional[DateRange], optional):
            well_types (List[str] | :class:`~cognite.well_model.NotSet`, optional): List of well types or :class:`~cognite.well_model.NotSet`
            licenses (List[str] | :class:`~cognite.well_model.NotSet`, optional):  List of licenses or :class:`~cognite.well_model.NotSet`
            trajectories (Optional[WellTrajectoryFilter], optional):
            depth_measurements (Optional[WellDepthMeasurementFilter], optional):
                Filter wellbores which have measurements in certain depths.
            time_measurements (Optional[WellTimeMeasurementFilter], optional):
            npt (Optional[WellNptFilter], optional):
            nds (Optional[WellNdsFilter], optional):
            polygon (Optional[PolygonFilter], optional):
            output_crs (Optional[str], optional):
                The CRS you want the wellheads to be in. Default=EPSG:4326 (WGS84)
            well_tops (Optional[WellTopFilter], optional):
            limit (Optional[int], optional): [description]. Defaults to DEFAULT_LIMIT.

        Returns:
            WellList: List of wells

        Examples:
            Get all wells
                >>> from cognite.well_model import CogniteWellsClient
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list()

            Get wells within a polygon
                >>> from cognite.well_model import CogniteWellsClient
                >>> from cognite.well_model.models import PolygonFilter
                >>> wm = CogniteWellsClient()
                >>> polygon = "POLYGON((3.4 60.7,6.08 57.44,1.16 58.44,3.40 60.7))"
                >>> wells = wm.wells.list(polygon=PolygonFilter(
                ...     geometry=polygon,
                ...     crs="EPSG:4326",
                ...     geometry_type="WKT",
                ... ))

            Get wells without a block
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list(blocks=NotSet)

            Get wells with gamma ray measurements between 500 and 1000 feet
                >>> from cognite.well_model import CogniteWellsClient, NotSet
                >>> from cognite.well_model.models import (
                ...     ContainsAllOrAny,
                ...     DistanceRange,
                ...     WellDepthMeasurementFilter,
                ... )
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list(depth_measurements=WellDepthMeasurementFilter(
                ...     measured_depth=DistanceRange(unit="foot", min=500.0, max=1000.0),
                ...     measurement_types=ContainsAllOrAny(
                ...         contains_any=["gamma ray"]
                ...     )
                ... ))

            Get wellbores from wells list
                >>> from cognite.well_model import CogniteWellsClient
                >>> from cognite.well_model.models import WellNdsFilter
                >>> wm = CogniteWellsClient()
                >>> wells = wm.wells.list(nds = WellNdsFilter())
                >>> wellbores = wells.wellbores()

        """  # noqa: E501

        def request(cursor, limit):
            search = WellSearch(query=string_matching) if string_matching else None
            well_filter = WellFilterRequest(
                filter=WellFilter(
                    quadrant=filter_to_model(quadrants),
                    region=filter_to_model(regions),
                    block=filter_to_model(blocks),
                    field=filter_to_model(fields),
                    operator=filter_to_model(operators),
                    well_type=filter_to_model(well_types),
                    license=filter_to_model(licenses),
                    sources=sources,
                    water_depth=water_depth,
                    datum=datum,
                    spud_date=spud_date,
                    trajectories=trajectories,
                    depth_measurements=depth_measurements,
                    time_measurements=time_measurements,
                    polygon=polygon,
                    npt=npt,
                    nds=nds,
                    well_tops=well_tops,
                ),
                search=search,
                output_crs=output_crs,
                cursor=cursor,
                limit=limit,
            )
            path: str = self._get_path("/wells/list")
            response: Response = self.client.post(url_path=path, json=well_filter.json())
            well_items_data: WellItems = WellItems.parse_raw(response.text)
            return well_items_data

        items = cursor_multi_request(
            get_cursor=lambda x: x.next_cursor, get_items=lambda x: x.items, limit=limit, request=request
        )
        return WellList(items)
