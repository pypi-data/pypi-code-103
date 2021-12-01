from herre.wards.graphql import ParsedQuery


GET_WHALE = ParsedQuery(
    """
query Whale($id: ID, $template: ID){
  whale(id: $id, template: $template){
    id
    template
    githubrepo {
      user
      branch
      repo
      id
    }
    config
  }
}
"""
)


GET_GITHUBREPO = ParsedQuery(
    """
query GithubRepo($id: ID, $template: ID){
  githubRepo(id: $id){
    id
    user
    branch
    repo
  }
}
"""
)
