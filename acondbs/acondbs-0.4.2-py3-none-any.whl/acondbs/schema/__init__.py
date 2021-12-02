import graphene
from graphene import relay

from . import (
    version as version_,
    web,
    auth,
    github,
    misc,
    product as p,
)


##__________________________________________________________________||
class QueryPublic(graphene.ObjectType):
    web_config = web.query.web_config_field
    is_signed_in = auth.query.is_signed_in_field
    git_hub_o_auth_app_info = github.query.git_hub_o_auth_app_info_field


class MutationPublic(graphene.ObjectType):
    authenticate_with_git_hub = github.mutation.AuthenticateWithGitHub.Field()
    create_log = misc.mutation.CreateLog.Field()


##__________________________________________________________________||
class QueryPrivate(QueryPublic):

    #
    version = version_.version_field
    alembic_version = version_.alembic_version_field

    node = relay.Node.Field()

    #
    git_hub_viewer = github.query.git_hub_viewer_field

    #
    is_admin = auth.query.is_admin_field

    #
    all_products = p.query.all_products_field
    all_product_file_paths = p.query.all_product_file_paths_field
    all_product_relations = p.query.all_product_relations_field
    all_product_relation_types = p.query.all_product_relation_types_field
    all_product_types = p.query.all_product_types_field
    all_fields = p.query.all_fields_field

    product = p.query.product_field
    product_relation = p.query.product_relation_field
    product_relation_type = p.query.product_relation_type_field
    product_type = p.query.product_type_field
    field = p.query.field_field


class MutationPrivate(MutationPublic):

    #
    create_product = p.mutation.CreateProduct.Field()
    delete_product = p.mutation.DeleteProduct.Field()
    update_product = p.mutation.UpdateProduct.Field()
    convert_product_type = p.mutation.ConvertProductType.Field()

    create_product_file_path = p.mutation.CreateProductFilePath.Field()
    delete_product_file_path = p.mutation.DeleteProductFilePath.Field()
    update_product_file_path = p.mutation.UpdateProductFilePath.Field()

    create_product_relation = p.mutation.CreateProductRelation.Field()
    delete_product_relation = p.mutation.DeleteProductRelation.Field()

    create_product_relation_types = (
        p.mutation.CreateProductRelationTypes.Field()
    )
    delete_product_relation_types = (
        p.mutation.DeleteProductRelationTypes.Field()
    )
    update_product_relation_type = p.mutation.UpdateProductRelationType.Field()

    create_product_type = p.mutation.CreateProductType.Field()
    delete_product_type = p.mutation.DeleteProductType.Field()
    update_product_type = p.mutation.UpdateProductType.Field()

    create_field = p.mutation.CreateField.Field()
    delete_field = p.mutation.DeleteField.Field()
    update_field = p.mutation.UpdateField.Field()


##__________________________________________________________________||
class QueryAdmin(QueryPrivate):

    #
    all_git_hub_orgs = github.query.all_git_hub_orgs_field
    all_git_hub_tokens = github.query.all_git_hub_tokens_field
    all_git_hub_users = github.query.all_git_hub_users_field

    #
    all_logs = misc.query.all_logs_field

    #
    log = misc.query.log_field


class MutationAdmin(MutationPrivate):

    #
    add_git_hub_org = github.mutation.AddGitHubOrg.Field()
    delete_git_hub_org = github.mutation.DeleteGitHubOrg.Field()

    add_git_hub_admin_app_token = (
        github.mutation.AddGitHubAdminAppToken.Field()
    )
    delete_git_hub_admin_app_token = (
        github.mutation.DeleteGitHubAdminAppToken.Field()
    )

    update_git_hub_org_member_lists = (
        github.mutation.UpdateGitHubOrgMemberLists.Field()
    )

    delete_log = misc.mutation.DeleteLog.Field()

    save_web_config = web.mutation.SaveWebconfig.Field()


##__________________________________________________________________||
class Query(QueryAdmin):
    pass


class Mutation(MutationAdmin):
    pass


##__________________________________________________________________||
schema_public = graphene.Schema(query=QueryPublic, mutation=MutationPublic)
schema_private = graphene.Schema(query=QueryPrivate, mutation=MutationPrivate)
schema_admin = graphene.Schema(query=QueryAdmin, mutation=MutationAdmin)

schema = graphene.Schema(query=Query, mutation=Mutation)

##__________________________________________________________________||
