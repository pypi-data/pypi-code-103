"""Call GitHub APIs

This module contains functions that actually access to GitHub APIs.
Other modules in the sub-package access to GitHub APIs via functions
in this module.

"""

import requests

API_URL = 'https://api.github.com/graphql'

##__________________________________________________________________||
def call_graphql_api(query, variables=None, token=None):
    """Call a GitHub GraphQL API

    Parameters
    ----------
    query : str
        A GraphQL query, e.g.,
        'query User($login: String!) { user(login: $login) { name } }'
    variables: dict, optional
        Variables for the query, e.g., {"login": "octocat"}
    token: str, optional
        An access token

    Returns
    -------
    dict
        The data field of the query results, e.g.,
        { "user": { "name": "The Octocat" } }

    Raises
    ------
    Exception
        If the query results include the field "errors" or don't include the
        field "data."
    """

    headers = {}
    if token:
      headers['Authorization'] = 'token {}'.format(token)

    json = {'query': query }
    if variables:
        json['variables'] = variables

    # example:
    #   headers = {'Authorization': 'token XXXXXXXXXXXXXXXXXXXX'}
    #   json = {
    #       'query': (
    #           'query User($login: String!) '
    #           '{ user(login: $login) { name } }'
    #       ),
    #       'variables': {"login": "octocat"}
    #   }


    response = requests.post(API_URL, json=json, headers=headers)
    response = response.json()
    # examples:
    #   success:
    #     response = {"data": {"user": {"name": "The Octocat"} } }
    #
    #   error: (note: the 'data' field might not exist.)
    #     response = {
    #         "data": {"user": null},
    #         "errors": [
    #             {
    #                 "type": "NOT_FOUND",
    #                 "path": ["user"],
    #                 "locations": [{"line": 7, "column": 3 }],
    #                 "message": "Could not resolve to a User with the login of 'octocat'."
    #             }
    #         ]
    #     }
    #
    #   bad credentials:
    #     response = {
    #         'message': 'Bad credentials',
    #         'documentation_url': 'https://docs.github.com/graphql'
    #     }

    if 'errors' in response:
      raise Exception(response['errors'])

    if 'data' not in response:
      raise Exception(response)

    return response['data']

##__________________________________________________________________||
def exchange_code_for_token(code, token_url, client_id, client_secret, redirect_uri):
    """exchange a OAuth2 authorization code for an access token

    https://docs.github.com/en/free-pro-team@latest/developers/apps/authorizing-oauth-apps#2-users-are-redirected-back-to-your-site-by-github

    Parameters
    ----------
    code : str
        An OAuth2 authorization code
    token_url: str
        The token URL, i.e., 'https://github.com/login/oauth/access_token'
    client_id: str
        The client ID of the OAuth2 app
    client_secret: str
        The client secret of the OAuth2 app
    redirect_uri: str
        The redirect URI of the OAuth2 app

    Returns
    -------
    dict
        E.g., {'access_token': 'XXXXXXXXXXXXXXXXXXXX', 'token_type': 'bearer', 'scope': 'user'}

    Raises
    ------
    Exception
        If an access token is not obtained, for example, because of a
        bad verification code

    """

    params = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code
    }

    headers = {
        'Accept': "application/vnd.github.v3+json, application/json",
    }

    response = requests.post(token_url, json=params, headers=headers)
    response = response.json() # dict
    # examples:
    #   success:
    #     response = {'access_token': 'XXXXXXXXXXXXXXXXXXXX', 'token_type': 'bearer', 'scope': 'user'}
    #
    #   error:
    #     response = {
    #         'error': 'bad_verification_code',
    #         'error_description': 'The code passed is incorrect or expired.',
    #         'error_uri': 'https://docs.github.com/apps/managing-oauth-apps/troubleshooting-oauth-app-access-token-request-errors/#bad-verification-code'
    #     }

    if 'access_token' not in response:
        raise Exception(response)

    return response

##__________________________________________________________________||
