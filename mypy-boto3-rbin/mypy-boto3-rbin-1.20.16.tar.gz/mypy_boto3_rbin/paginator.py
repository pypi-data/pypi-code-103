"""
Type annotations for rbin service client paginators.

[Open documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_rbin/paginators.html)

Usage::

    ```python
    import boto3

    from mypy_boto3_rbin import RecycleBinClient
    from mypy_boto3_rbin.paginator import (
        ListRulesPaginator,
    )

    client: RecycleBinClient = boto3.client("rbin")

    list_rules_paginator: ListRulesPaginator = client.get_paginator("list_rules")
    ```
"""
import sys
from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator
from botocore.paginate import Paginator as Boto3Paginator

from .type_defs import ListRulesResponseTypeDef, PaginatorConfigTypeDef, ResourceTagTypeDef

if sys.version_info >= (3, 9):
    from typing import Literal
else:
    from typing_extensions import Literal


__all__ = ("ListRulesPaginator",)


_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListRulesPaginator(Boto3Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.16/reference/services/rbin.html#RecycleBin.Paginator.ListRules)
    [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_rbin/paginators.html#listrulespaginator)
    """

    def paginate(
        self,
        *,
        ResourceType: Literal["EBS_SNAPSHOT"],
        ResourceTags: Sequence["ResourceTagTypeDef"] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRulesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/1.20.16/reference/services/rbin.html#RecycleBin.Paginator.ListRules.paginate)
        [Show boto3-stubs documentation](https://vemel.github.io/boto3_stubs_docs/mypy_boto3_rbin/paginators.html#listrulespaginator)
        """
