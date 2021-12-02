from ..fragments import FRAGMENT_LOG_CONNECTION

QUERY_ALL_LOGS = (
    """
query AllLogs {
  allLogs {
    ...fragmentLogConnection
  }
}
"""
    + FRAGMENT_LOG_CONNECTION
)
