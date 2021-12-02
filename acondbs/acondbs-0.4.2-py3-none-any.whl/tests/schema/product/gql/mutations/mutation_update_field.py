from ..fragments import FRAGMENT_FIELD

MUTATION_UPDATE_FIELD = (
    """
mutation UpdateField($fieldId: Int!, $input: UpdateFieldInput!) {
  updateField(fieldId: $fieldId, input: $input) {
    ok
    field {
      ...fragmentField
    }
  }
}
"""
    + FRAGMENT_FIELD
)
