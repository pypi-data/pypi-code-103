MUTATION_SAVE_WEB_CONFIG = """
mutation SaveWebConfig($json: String!) {
  saveWebConfig(json: $json) {
    ok
    webConfig {
      id_
      json
    }
  }
}
"""
