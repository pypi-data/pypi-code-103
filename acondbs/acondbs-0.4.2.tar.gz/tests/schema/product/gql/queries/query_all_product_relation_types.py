from ..fragments import FRAGMENT_PRODUCT_RELATION_TYPE_CONNECTION

QUERY_ALL_PRODUCT_RELATION_TYPES = (
    """
{
  allProductRelationTypes {
    ...fragmentProductRelationTypeConnection
  }
}
"""
    + FRAGMENT_PRODUCT_RELATION_TYPE_CONNECTION
)
