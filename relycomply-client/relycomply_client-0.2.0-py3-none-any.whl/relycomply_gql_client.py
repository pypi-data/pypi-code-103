from gql import Client
from gql.transport.requests import RequestsHTTPTransport
from . import settings
import requests
from .gql_generator import GQLGenerator
from gql import gql

from littleutils import only


class RelyComplyGQLClient:
    """
    A flexible and intelligent GraphQL client for RelyComply. This client will create methods
    that match the mutation sand queries of the RelyComply API, and expose them with familiar
    calling conventions. It also handles paging as well as simplifying the returned structures.

    Queries can be called with their lowerCase field name and any filter arguments as kwargs, e.g.:

        client.products(nameContain="ZA") # Will return a list of products
        client.products(nameContain="ZA", _iter=True) # Will return a lazy generator
        client.products(name="retailZA", _only=True) # Will return only the first object or None

    Mutations can be called in a similar way, but arguments will be lifted into the $input variable

        client.createProduct(name="retailZA", label="South African Retail) # Returns the created product

    The interface is automatically generated from the GQL schema as well as the CLI support templates.
    Thus it should always be in sync. Credentials are drawn from the environment variables:
        * RELYCOMPLY_TOKEN
        * RELYCOMPLY_URL
        * RELYCOMPLY_IMPERSONATE
    """

    def __init__(self):
        # Setup a GQL client, pull creds from env
        transport = RequestsHTTPTransport(
            url=settings.RELYCOMPLY_URL + "/graphql/",
            verify=True,
            retries=3,
            headers={
                "IMPERSONATE": settings.RELYCOMPLY_IMPERSONATE,
                "Authorization": f"Bearer {settings.RELYCOMPLY_TOKEN}",
            },
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

        # Pull support templates
        self.templates = requests.get(
            settings.RELYCOMPLY_URL + "/cli/v1/support_templates/"
        ).json()

        self.schema = self.client.schema

        self.generator = GQLGenerator(self.schema, self.templates)

        self._attach_mutations()
        self._attach_queries()

    def _attach_mutations(self):
        for field in self.schema.mutation_type.fields.keys():
            self._attach_mutation(field)

    def _attach_mutation(self, field):
        def mutation(**variables):
            return self._execute_mutation(field, variables)

        setattr(self, field, mutation)

    def _attach_queries(self):
        for field in self.schema.query_type.fields.keys():
            self._attach_query(field)

    def _attach_query(self, field):
        def query(_iter=False, _only=False, **variables):
            return self._execute_query(field, variables, _iter, _only)

        setattr(self, field, query)

    def _collapse_edges(self, value):

        if isinstance(value, list):
            return [self._collapse_edges(child) for child in value]

        if isinstance(value, dict):
            replacement = {}
            for key, child in value.items():
                if (
                    isinstance(child, dict)
                    and len(child) == 1
                    and "edges" in child
                    and isinstance(child["edges"], list)
                ):
                    replacement[key] = [
                        self._collapse_edges(edge["node"]) for edge in child["edges"]
                    ]
                else:
                    replacement[key] = self._collapse_edges(child)
            return replacement
        else:
            return value

    def _only_value(self, result):
        return only(result.values())

    def _execute(self, query, variables):
        result = self.client.execute(query, variable_values=variables)
        return self._only_value(result)

    def _endpoint_graphql(self, action, endpoint):
        return self.generator.generate_endpoint(action, endpoint)

    def _execute_endpoint(self, action, endpoint, variables):
        graphql = self._endpoint_graphql(action, endpoint)
        query = gql(graphql)
        return self._execute(query, variables)

    def _execute_query(self, endpoint, variables, _iter, _only):
        if _only:
            try:
                return next(self._execute_query_iter(endpoint, variables))
            except StopIteration:
                return None

        if _iter:
            return self._execute_query_iter(endpoint, variables)
        else:
            return list(self._execute_query_iter(endpoint, variables))

    def _execute_query_iter(self, endpoint, variables):
        after = None
        hasNextPage = True

        while hasNextPage:
            result = self._execute_endpoint("query", endpoint, variables)
            hasNextPage = result["pageInfo"]["hasNextPage"]

            for edge in result["edges"]:
                node = edge["node"]
                yield self._collapse_edges(node)

            if not hasNextPage:
                break
            else:
                after = result["pageInfo"]["endCursor"]
                variables["after"] = after

    def _execute_mutation(self, endpoint, variables):
        result = self._execute_endpoint("mutation", endpoint, dict(input=variables))
        return self._only_value(self._collapse_edges(result))
