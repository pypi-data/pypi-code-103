IMPORT_DBT_MANIFEST = """
mutation importDbtManifest($dbtSchemaVersion: String!, $manifestNodesJson: String!) {
  importDbtManifest(
    dbtSchemaVersion: $dbtSchemaVersion,
    manifestNodesJson: $manifestNodesJson
  ) {
    response {
      nodeIdsImported
    }
  }
}
"""
