from ..fragments import FRAGMENT_PRODUCT_RELATION_CONNECTION

QUERY_ALL_PRODUCT_RELATIONS = (
    """
{
  allProductRelations {
    ...fragmentProductRelationConnection
  }
}
"""
    + FRAGMENT_PRODUCT_RELATION_CONNECTION
)
