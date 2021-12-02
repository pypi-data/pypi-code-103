from ..fragments import FRAGMENT_LOG

MUTATION_CREATE_LOG = '''
mutation CreateLog($input: CreateLogInput!) {
  createLog(input: $input) {
    ok
    log {
      ...fragmentLog
    }
  }
}
''' + FRAGMENT_LOG
