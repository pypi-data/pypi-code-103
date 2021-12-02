import graphene
from graphql import GraphQLError

from ...db.sa import sa
from ...db.backup import request_backup_db

from ...models import (
    GitHubToken as GitHubTokenModel,
)
from ...github.ops import (
    update_org_member_lists,
    add_org,
    delete_org,
    store_token_for_code,
    authenticate,
)

from . import type_


##__________________________________________________________________||
class AddGitHubOrg(graphene.Mutation):
    class Arguments:
        login = graphene.String(required=True)

    ok = graphene.Boolean()
    git_hub_org = graphene.Field(lambda: type_.GitHubOrg)

    def mutate(root, info, login):
        model = add_org(login)
        ok = True
        # request_backup_db()
        return AddGitHubOrg(git_hub_org=model, ok=ok)


class DeleteGitHubOrg(graphene.Mutation):
    class Arguments:
        login = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, login):
        delete_org(login)
        ok = True
        # request_backup_db()
        return DeleteGitHubOrg(ok=ok)


##__________________________________________________________________||
class AuthenticateWithGitHub(graphene.Mutation):
    class Arguments:
        code = graphene.String(required=True)

    authPayload = graphene.Field(lambda: type_.AuthPayload)

    def mutate(root, info, code):
        token_dict = authenticate(code)
        if not token_dict:
            raise GraphQLError("Unsuccessful to obtain the token")
        authPayload = type_.AuthPayload(token=token_dict["access_token"])
        return AuthenticateWithGitHub(authPayload=authPayload)


##__________________________________________________________________||
class AddGitHubAdminAppToken(graphene.Mutation):
    """Add a token for a GitHub Admin App"""

    class Arguments:
        code = graphene.String(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, code):
        store_token_for_code(code)
        ok = True
        request_backup_db()
        return AddGitHubAdminAppToken(ok=ok)


##__________________________________________________________________||
class DeleteGitHubAdminAppToken(graphene.Mutation):
    """Delete a token for a GitHub Admin App"""

    class Arguments:
        token_id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, token_id):
        model = GitHubTokenModel.query.filter_by(token_id=token_id).one()
        sa.session.delete(model)
        sa.session.commit()
        ok = True
        request_backup_db()
        return DeleteGitHubAdminAppToken(ok=ok)


##__________________________________________________________________||
class UpdateGitHubOrgMemberLists(graphene.Mutation):
    """Update the member lists of GitHub organizations"""

    ok = graphene.Boolean()

    def mutate(root, info):
        update_org_member_lists()
        ok = True
        # request_backup_db()
        return UpdateGitHubOrgMemberLists(ok=ok)


##__________________________________________________________________||
