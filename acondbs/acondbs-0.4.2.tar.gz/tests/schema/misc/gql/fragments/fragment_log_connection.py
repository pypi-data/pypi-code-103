from .fragment_log import FRAGMENT_LOG

FRAGMENT_LOG_CONNECTION = '''
fragment fragmentLogConnection on LogConnection {
  totalCount
  edges {
    node {
     ...fragmentLog
    }
  }
}
''' + FRAGMENT_LOG
