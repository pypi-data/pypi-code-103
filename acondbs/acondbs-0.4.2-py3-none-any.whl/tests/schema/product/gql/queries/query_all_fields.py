from ..fragments import FRAGMENT_FIELD_CONNECTION

QUERY_ALL_FIELDS = (
    """
query AllFields {
  allFields {
    ...fragmentFieldConnection
  }
}
"""
    + FRAGMENT_FIELD_CONNECTION
)
