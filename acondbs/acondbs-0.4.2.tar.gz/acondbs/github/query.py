"""Queries to GitHub API
"""

import base64

from .call import call_graphql_api

##__________________________________________________________________||
def org(login, token):
    query = """
      query Organization($login: String!) {
        organization(login: $login) {
          id
          login
          avatarUrl
          url
        }
      }
    """
    variables = { "login": login }
    r = call_graphql_api(query=query, variables=variables, token=token)
    # e.g.,
    #   {
    #       "organization": {
    #           "id": "MDEyOk9yZ2FuaXphdGlvbjc1NjMxODQ0",
    #           "login": "urban-octo-disco",
    #           "avatarUrl": "https://avatars0.githubusercontent.com/u/75631844?v=4",
    #           "url": "https://github.com/urban-octo-disco"
    #       }
    #   }

    r['organization']['id'] = _decode_id(r['organization']['id'])
    # e.g., "012:Organization75631844"

    return r['organization']

##__________________________________________________________________||
def org_members(org_login, token):

    first = 100

    query = """
      query OrganizationMembers($org_login: String!, $first: Int!, $after: String) {
        organization(login: $org_login) {
          login
          membersWithRole(first: $first, after: $after) {
            pageInfo {
              endCursor
              hasNextPage
            }
            edges {
              cursor
              role
              node {
                id
                login
                name
                avatarUrl
                url
              }
            }
          }
        }
      }
    """

    # an example query result:
    #   {'organization': {
    #       'login': 'urban-octo-disco',
    #       'membersWithRole': {
    #           'pageInfo': {
    #               'endCursor': 'Y3Vyc29yOnYyOpHOAO9YQQ==',
    #               'hasNextPage': False
    #           },
    #           'edges': [
    #               {
    #                   'cursor': 'Y3Vyc29yOnYyOpHOABUuMQ==',
    #                   'node': {
    #                       'id': 'MDQ6VXNlcjEzODgwODE=',
    #                       'login': 'TaiSakuma',
    #                       'name': 'Tai Sakuma',
    #                       'avatarUrl': 'https://avatars0.githubusercontent.com/u/1388081?v=4',
    #                       'url': 'https://github.com/TaiSakuma'
    #                   },
    #                   'role': 'MEMBER'
    #               },
    #               {
    #                   'cursor': 'Y3Vyc29yOnYyOpHOAO9YQQ==',
    #                   'node': {
    #                       'id': 'MDQ6VXNlcjE1Njg1Njk3',
    #                       'login': 'tai-sakuma',
    #                       'name': None,
    #                       'avatarUrl': 'https://avatars0.githubusercontent.com/u/15685697?v=4',
    #                       'url': 'https://github.com/tai-sakuma'
    #                   },
    #                   'role': 'ADMIN'
    #               }
    #           ],
    #       }}}

    variables = {"org_login": org_login, "first": first}

    edges = []
    while True:
        r = call_graphql_api(query=query, variables=variables, token=token)
        membersWithRole = r['organization']['membersWithRole']
        edges.extend(membersWithRole['edges'])
        pageInfo = membersWithRole['pageInfo']
        if not pageInfo['hasNextPage']:
            break
        variables["after"] = pageInfo['endCursor']

    for e in edges:
        e['node']['id'] = _decode_id(e['node']['id'])

    return edges

##__________________________________________________________________||
def viewer(token):
    """Return info about the GitHub user for a token

    Parameters
    ----------
    token : str
        An access token, e.g, '4d5dc8b74eccdf65859d6ac64358a3a98300c351'

    Returns
    -------
    dict
        e.g.,
            {
                "id": "04:User583231",
                "login": "octocat",
                "name": "The Octocat",
                "avatarUrl": "https://avatars3.githubusercontent.com/u/583231?u=a59fef2a493e2b67dd13754231daf220c82ba84d&v=4",
                "url": "https://github.com/octocat"
            }
    """

    query = '{ viewer { login id name avatarUrl url } }'
    r = call_graphql_api(query=query, token=token)
    # e.g., https://github.com/octocat
    # {
    #     "viewer": {
    #         "id": "MDQ6VXNlcjU4MzIzMQ==",
    #         "login": "octocat",
    #         "name": "The Octocat",
    #         "avatarUrl": "https://avatars3.githubusercontent.com/u/583231?u=a59fef2a493e2b67dd13754231daf220c82ba84d&v=4",
    #         "url": "https://github.com/octocat"
    #     }
    # }

    viewer = r['viewer']

    viewer['id'] = _decode_id(viewer['id'])
    # e.g., '04:User583231'

    return viewer

##__________________________________________________________________||
def _decode_id(id_):
    """Decode a GitHub user or organization ID returned from GitHub GraphQL API

    Parameters
    ----------
    id_ : str
        An encoded GitHub user or GitHub organization ID returned from
        GitHub GraphQL API, e.g., "MDQ6VXNlcjU4MzIzMQ=="

    Returns
    -------
    str
        The decoded ID, e.g., "04:User583231", "012:Organization75631844"

    """
    return base64.b64decode(id_).decode()

##__________________________________________________________________||

