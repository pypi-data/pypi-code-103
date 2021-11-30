from typing import Union, List
import asyncio
from graphql import GraphQLField, GraphQLObjectType, GraphQLInterfaceType, GraphQLResolveInfo
from ariadne import load_schema_from_path, make_executable_schema, SchemaDirectiveVisitor
from ariadne.graphql import GraphQLError
from ariadne.asgi import GraphQL
from ariadne.types import Extension, SchemaBindable

# Directives


class NoAuthenticationDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
            self,
            field: GraphQLField,
            object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        field.__require_authentication__ = False
        return field

    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__require_authentication__ = False
        return object_


class NeedPermissionDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        if self.args['strict'] or object_type.name == 'Mutation':
            field.__require_scope__ = self.args['scope']
        else:
            field.__hide_noscope__ = self.args['scope']
        return field

    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        if self.args['strict']:
            object_.__require_scope__ = self.args['scope']
        else:
            object_.__hide_noscope__ = self.args['scope']
        return object_


class DBModelDirective(SchemaDirectiveVisitor):
    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__db_model__ = True
        object_.__primary_keys__ = self.args['primary_keys']
        return object_


class AllFilterDirective(SchemaDirectiveVisitor):
    def visit_object(self, object_: GraphQLObjectType) -> GraphQLObjectType:
        object_.__all_filter__ = True
        return object_


class FilterDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        field.__filter__ = True
        return field


class NoFilterDirective(SchemaDirectiveVisitor):
    def visit_field_definition(
        self,
        field: GraphQLField,
        object_type: Union[GraphQLObjectType, GraphQLInterfaceType],
    ) -> GraphQLField:
        field.__filter__ = False
        return field


# Middleware

async def check_permission_middleware(resolver, obj, info: GraphQLResolveInfo, **args):
    """ GraphQL middleware that requires authentication by default """
    request = info.context['request']
    field = info.parent_type.fields[info.field_name]

    # Check for Authentication
    if hasattr(field, '__require_authentication__'):
        needs_auth = field.__require_authentication__
    elif hasattr(info.parent_type, '__require_authentication__'):
        needs_auth = info.parent_type.__require_authentication__
    else:
        needs_auth = True

    if needs_auth and not request.user.is_authenticated:
        raise GraphQLError(message='Requires Authentication')

    # check for Strict Permission
    if hasattr(field, '__require_scope__'):
        needs_scope = field.__require_scope__
    elif hasattr(info.parent_type, '__require_scope__'):
        needs_scope = info.parent_type.__require_scope__
    else:
        needs_scope = None

    if needs_scope is not None and needs_scope not in request.auth.scopes:
        raise GraphQLError(message=f'Requires Scope: {needs_scope}')

    # check for Loose Permission
    if hasattr(field, '__hide_noscope__'):
        hide_noscope = field.__hide_noscope__
    elif hasattr(info.parent_type, '__hide_noscope__'):
        hide_noscope = info.parent_type.__hide_noscope__
    else:
        hide_noscope = None

    if hide_noscope is not None and hide_noscope not in request.auth.scopes:
        return None

    # Return resolver
    if asyncio.iscoroutinefunction(resolver):
        return await resolver(obj, info, **args)
    else:
        return resolver(obj, info, **args)


class DBRollbackExtension(Extension):
    def has_errors(self, errors, context) -> None:
        context['request'].state.dbsession.rollback()


# Exported

def create_graphql(schema_path, bindables: List[SchemaBindable], debug: bool):
    type_defs = load_schema_from_path(schema_path)

    schema = make_executable_schema(type_defs, bindables, directives={
        'no_authentication': NoAuthenticationDirective,
        'need_permission': NeedPermissionDirective,
        'db_model': DBModelDirective,
        'all_filter': AllFilterDirective,
        'filter': FilterDirective,
        'no_filter': NoFilterDirective
    })

    return GraphQL(schema, debug=debug, middleware=[check_permission_middleware], extensions=[DBRollbackExtension])
