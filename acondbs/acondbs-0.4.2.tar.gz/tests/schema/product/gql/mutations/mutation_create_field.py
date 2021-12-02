from ..fragments import FRAGMENT_FIELD

MUTATION_CREATE_FIELD = '''
mutation CreateField($input: CreateFieldInput!) {
  createField(input: $input) {
    ok
    field {
      ...fragmentField
    }
  }
}
''' + FRAGMENT_FIELD
