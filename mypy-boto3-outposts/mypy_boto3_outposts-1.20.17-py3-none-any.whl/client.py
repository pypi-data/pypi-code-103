"""
Type annotations for outposts service client.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html)

Usage::

    ```python
    import boto3
    from mypy_boto3_outposts import OutpostsClient

    client: OutpostsClient = boto3.client("outposts")
    ```
"""
import sys
from typing import Any, Dict, Mapping, Sequence, Type

from botocore.client import BaseClient, ClientMeta

from .literals import (
    AddressTypeType,
    CatalogItemClassType,
    FiberOpticCableTypeType,
    MaximumSupportedWeightLbsType,
    OpticalStandardType,
    PaymentOptionType,
    PowerConnectorType,
    PowerDrawKvaType,
    PowerFeedDropType,
    PowerPhaseType,
    SupportedHardwareTypeType,
    SupportedStorageEnumType,
    UplinkCountType,
    UplinkGbpsType,
)
from .type_defs import (
    AddressTypeDef,
    CreateOrderOutputTypeDef,
    CreateOutpostOutputTypeDef,
    CreateSiteOutputTypeDef,
    GetCatalogItemOutputTypeDef,
    GetOrderOutputTypeDef,
    GetOutpostInstanceTypesOutputTypeDef,
    GetOutpostOutputTypeDef,
    GetSiteAddressOutputTypeDef,
    GetSiteOutputTypeDef,
    LineItemRequestTypeDef,
    ListCatalogItemsOutputTypeDef,
    ListOrdersOutputTypeDef,
    ListOutpostsOutputTypeDef,
    ListSitesOutputTypeDef,
    ListTagsForResourceResponseTypeDef,
    RackPhysicalPropertiesTypeDef,
    UpdateSiteAddressOutputTypeDef,
    UpdateSiteOutputTypeDef,
    UpdateSiteRackPhysicalPropertiesOutputTypeDef,
)

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("OutpostsClient",)


class BotocoreClientError(BaseException):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    NotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class OutpostsClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        OutpostsClient exceptions.
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.can_paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#can_paginate)
        """

    def cancel_order(self, *, OrderId: str) -> Dict[str, Any]:
        """
        Cancels an order for an Outpost.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.cancel_order)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#cancel_order)
        """

    def create_order(
        self,
        *,
        OutpostIdentifier: str,
        LineItems: Sequence["LineItemRequestTypeDef"],
        PaymentOption: PaymentOptionType,
        PaymentTerm: Literal["THREE_YEARS"] = ...
    ) -> CreateOrderOutputTypeDef:
        """
        Creates an order for an Outpost.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.create_order)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#create_order)
        """

    def create_outpost(
        self,
        *,
        Name: str,
        SiteId: str,
        Description: str = ...,
        AvailabilityZone: str = ...,
        AvailabilityZoneId: str = ...,
        Tags: Mapping[str, str] = ...,
        SupportedHardwareType: SupportedHardwareTypeType = ...
    ) -> CreateOutpostOutputTypeDef:
        """
        Creates an Outpost.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.create_outpost)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#create_outpost)
        """

    def create_site(
        self,
        *,
        Name: str,
        Description: str = ...,
        Notes: str = ...,
        Tags: Mapping[str, str] = ...,
        OperatingAddress: "AddressTypeDef" = ...,
        ShippingAddress: "AddressTypeDef" = ...,
        RackPhysicalProperties: "RackPhysicalPropertiesTypeDef" = ...
    ) -> CreateSiteOutputTypeDef:
        """
        Creates a site for an Outpost.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.create_site)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#create_site)
        """

    def delete_outpost(self, *, OutpostId: str) -> Dict[str, Any]:
        """
        Deletes the Outpost.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.delete_outpost)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#delete_outpost)
        """

    def delete_site(self, *, SiteId: str) -> Dict[str, Any]:
        """
        Deletes the site.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.delete_site)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#delete_site)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#generate_presigned_url)
        """

    def get_catalog_item(self, *, CatalogItemId: str) -> GetCatalogItemOutputTypeDef:
        """
        Gets information about a catalog item.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.get_catalog_item)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#get_catalog_item)
        """

    def get_order(self, *, OrderId: str) -> GetOrderOutputTypeDef:
        """
        Gets an order.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.get_order)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#get_order)
        """

    def get_outpost(self, *, OutpostId: str) -> GetOutpostOutputTypeDef:
        """
        Gets information about the specified Outpost.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.get_outpost)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#get_outpost)
        """

    def get_outpost_instance_types(
        self, *, OutpostId: str, NextToken: str = ..., MaxResults: int = ...
    ) -> GetOutpostInstanceTypesOutputTypeDef:
        """
        Lists the instance types for the specified Outpost.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.get_outpost_instance_types)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#get_outpost_instance_types)
        """

    def get_site(self, *, SiteId: str) -> GetSiteOutputTypeDef:
        """
        Gets information about the specified Outpost site.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.get_site)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#get_site)
        """

    def get_site_address(
        self, *, SiteId: str, AddressType: AddressTypeType
    ) -> GetSiteAddressOutputTypeDef:
        """
        Gets the site address.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.get_site_address)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#get_site_address)
        """

    def list_catalog_items(
        self,
        *,
        NextToken: str = ...,
        MaxResults: int = ...,
        ItemClassFilter: Sequence[CatalogItemClassType] = ...,
        SupportedStorageFilter: Sequence[SupportedStorageEnumType] = ...,
        EC2FamilyFilter: Sequence[str] = ...
    ) -> ListCatalogItemsOutputTypeDef:
        """
        Use to create a list of every item in the catalog.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.list_catalog_items)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#list_catalog_items)
        """

    def list_orders(
        self, *, OutpostIdentifierFilter: str = ..., NextToken: str = ..., MaxResults: int = ...
    ) -> ListOrdersOutputTypeDef:
        """
        Create a list of the Outpost orders for your Amazon Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.list_orders)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#list_orders)
        """

    def list_outposts(
        self,
        *,
        NextToken: str = ...,
        MaxResults: int = ...,
        LifeCycleStatusFilter: Sequence[str] = ...,
        AvailabilityZoneFilter: Sequence[str] = ...,
        AvailabilityZoneIdFilter: Sequence[str] = ...
    ) -> ListOutpostsOutputTypeDef:
        """
        Create a list of the Outposts for your Amazon Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.list_outposts)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#list_outposts)
        """

    def list_sites(self, *, NextToken: str = ..., MaxResults: int = ...) -> ListSitesOutputTypeDef:
        """
        Lists the sites for your Amazon Web Services account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.list_sites)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#list_sites)
        """

    def list_tags_for_resource(self, *, ResourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Lists the tags for the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#list_tags_for_resource)
        """

    def tag_resource(self, *, ResourceArn: str, Tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        Adds tags to the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.tag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#tag_resource)
        """

    def untag_resource(self, *, ResourceArn: str, TagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes tags from the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.untag_resource)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#untag_resource)
        """

    def update_site(
        self, *, SiteId: str, Name: str = ..., Description: str = ..., Notes: str = ...
    ) -> UpdateSiteOutputTypeDef:
        """
        Updates the site.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.update_site)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#update_site)
        """

    def update_site_address(
        self, *, SiteId: str, AddressType: AddressTypeType, Address: "AddressTypeDef"
    ) -> UpdateSiteAddressOutputTypeDef:
        """
        Updates the site address.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.update_site_address)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#update_site_address)
        """

    def update_site_rack_physical_properties(
        self,
        *,
        SiteId: str,
        PowerDrawKva: PowerDrawKvaType = ...,
        PowerPhase: PowerPhaseType = ...,
        PowerConnector: PowerConnectorType = ...,
        PowerFeedDrop: PowerFeedDropType = ...,
        UplinkGbps: UplinkGbpsType = ...,
        UplinkCount: UplinkCountType = ...,
        FiberOpticCableType: FiberOpticCableTypeType = ...,
        OpticalStandard: OpticalStandardType = ...,
        MaximumSupportedWeightLbs: MaximumSupportedWeightLbsType = ...
    ) -> UpdateSiteRackPhysicalPropertiesOutputTypeDef:
        """
        Update the physical and logistical details for a rack at a site.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.17/reference/services/outposts.html#Outposts.Client.update_site_rack_physical_properties)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_outposts/client.html#update_site_rack_physical_properties)
        """
