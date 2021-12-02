MUTATION_DELETE_LOG = """
mutation DeleteLog($id_: Int!) {
  deleteLog(id_: $id_) {
    ok
  }
}
"""
