from ..fragments import FRAGMENT_LOG

QUERY_LOG = (
    """
query Log($id_: Int) {
  log(id_: $id_) {
    ...fragmentLog
  }
}
"""
    + FRAGMENT_LOG
)
