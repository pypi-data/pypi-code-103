from ..fragments import FRAGMENT_FIELD

QUERY_FIELD = (
    """
query Field($fieldId: Int, $name: String) {
  field(fieldId: $fieldId, name: $name) {
    ...fragmentField
  }
}
"""
    + FRAGMENT_FIELD
)
