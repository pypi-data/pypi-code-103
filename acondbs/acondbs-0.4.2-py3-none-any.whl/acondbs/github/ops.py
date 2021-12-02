"""Operations on DB
"""

from flask import current_app

from ..db.sa import sa

from ..models import (
    GitHubOrg,
    GitHubUser,
    GitHubToken,
    GitHubOrgMembership,
    AccountAdmin
)

from . import call, query

##__________________________________________________________________||
def get_github_oauth_app_info():
    """Return GitHub OAuth App information

    Returns
    -------
    dict
        e.g.,
            {
                'authorize_url': 'https://github.com/login/oauth/authorize',
                'token_url': 'https://github.com/login/oauth/access_token',
                'client_id': '2a868f8903ce767aa372',
                'client_secret': 'a3b5c532fc28f6ceca8fd284635d915300beb7d3',
                'redirect_uri': 'https://example.org/redirect'
            }
    """
    ret = dict(
        authorize_url=current_app.config['GITHUB_AUTH_AUTHORIZE_URL'],
        token_url=current_app.config['GITHUB_AUTH_TOKEN_URL'],
        client_id=current_app.config['GITHUB_AUTH_CLIENT_ID'],
        client_secret=current_app.config['GITHUB_AUTH_CLIENT_SECRET'],
        redirect_uri=current_app.config['GITHUB_AUTH_REDIRECT_URI']
    )
    return ret

##__________________________________________________________________||
def exchange_code_for_token(code):
    """Exchange an OAuth authentication code for a access token

    Parameters
    ----------
    code : str
        An OAuth authentication code, e.g, '7a31b6726dd2927b0af7'

    Returns
    -------
    dict
        e.g.,
            {
                'access_token': 'cc539c02d5c086e200db6aff212ace633a8c5e77',
                'token_type': 'bearer',
                'scope': ''
            }

    """
    oauth_app_info = get_github_oauth_app_info()
    return call.exchange_code_for_token(
        code,
        token_url=oauth_app_info['token_url'],
        client_id=oauth_app_info['client_id'],
        client_secret=current_app.config['GITHUB_AUTH_CLIENT_SECRET'],
        redirect_uri=current_app.config['GITHUB_AUTH_REDIRECT_URI']
        )

##__________________________________________________________________||
def add_org(login):
    if GitHubOrg.query.filter_by(login=login).one_or_none() is not None:
        raise Exception(f'already exists: {login}')
    if not (tokens := GitHubToken.query.all()):
        raise Exception('No tokens available.')
    r = None
    for token in tokens:
        try:
            r = query.org(login, token.token)
        except:
            continue
        break
    if r is None:
        raise Exception(f'Unable to find an org: {login}')
    model = GitHubOrg(
        login=login,
        git_hub_id=r['id'],
        avatar_url=r['avatarUrl'],
        url=r['url']
    )
    sa.session.add(model)
    sa.session.commit()
    return model

def delete_org(login):
    if (model := GitHubOrg.query.filter_by(login=login).one_or_none()) is None:
        raise Exception(f'does not exist: {login}')
    sa.session.delete(model)
    sa.session.commit()

##__________________________________________________________________||
def update_org_member_lists():
    if not (tokens := GitHubToken.query.filter(GitHubToken.scope.like('%read:org%')).all()):
        raise Exception('No tokens with relevant scopes available.')
    if not (orgs := GitHubOrg.query.all()):
        raise Exception('No orgs found.')
    with sa.session.no_autoflush:
        memberships = GitHubOrgMembership.query.all()
        for membership in memberships:
            sa.session.delete(membership)
        for org in orgs:
            edges = None
            for token in tokens:
                try:
                    edges = query.org_members(org.login, token.token)
                except Exception as e:
                    print(e)
                    continue
                break
            if edges is None:
                raise Exception(f'Unable to find an org: {org.login}')
            for edge in edges:
                node = edge['node']
                if (member := GitHubUser.query.filter_by(git_hub_id=node['id']).one_or_none()) is None:
                    member = GitHubUser(git_hub_id=node['id'])
                member.login = node['login']
                member.name = node['name']
                member.avatar_url = node['avatarUrl']
                member.url = node['url']
                membership = GitHubOrgMembership(org=org, member=member)
                sa.session.add(membership)
    sa.session.commit()

##__________________________________________________________________||
def store_token_for_code(code):
    token_dict = exchange_code_for_token(code)
    viewer = query.viewer(token_dict['access_token'])
    if (user_model := GitHubUser.query.filter_by(git_hub_id=viewer['id']).one_or_none()) is None:
        user_model = GitHubUser(git_hub_id=viewer['id'])
    user_model.login = viewer['login']
    user_model.name = viewer['name']
    user_model.avatar_url = viewer['avatarUrl']
    user_model.url = viewer['url']
    token_model = GitHubToken(
        token=token_dict['access_token'],
        scope=token_dict['scope'],
        user=user_model)
    sa.session.add(token_model)
    sa.session.commit()

##__________________________________________________________________||
def authenticate(code):
    """Authenticate a GitHub user with an OAuth authentication code

    This function authenticates a GitHub user with an OAuth
    authentication code. It also checks the membership of GitHub
    organizations and updates the DB.

    Parameters
    ----------
    code : str
        An OAuth authentication code, e.g, '7a31b6726dd2927b0af7'

    Returns
    -------
    dict
        e.g.,
            {
                'access_token': 'cc539c02d5c086e200db6aff212ace633a8c5e77',
                'token_type': 'bearer',
                'scope': ''
            }

    Raises
    ------
    Exception
        If the authentication is unsuccessful.

    """

    token_dict = exchange_code_for_token(code)
    viewer = query.viewer(token_dict['access_token'])
    account_admin_model = AccountAdmin.query.filter_by(git_hub_login=viewer['login']).one_or_none()
    user_model= GitHubUser.query.filter_by(git_hub_id=viewer['id']).one_or_none()
    if account_admin_model is None:
        if user_model is None:
            raise Exception(f'{viewer["login"]} is not a member.')
        if not user_model.memberships:
            raise Exception(f'{viewer["login"]} is not a member!')
    else:
        if user_model is None:
            user_model = GitHubUser(git_hub_id=viewer['id'])
    user_model.login = viewer['login']
    user_model.name = viewer['name']
    user_model.avatar_url = viewer['avatarUrl']
    user_model.url = viewer['url']
    token_model = GitHubToken(
        token=token_dict['access_token'],
        scope=token_dict['scope'],
        user=user_model)
    sa.session.add(token_model)
    sa.session.commit()
    return token_dict

##__________________________________________________________________||
def get_user_for_token(token):
    """
    """
    user = GitHubUser.query.join(GitHubToken). \
        filter(GitHubToken.token==token). \
        one()
    return user

##__________________________________________________________________||
