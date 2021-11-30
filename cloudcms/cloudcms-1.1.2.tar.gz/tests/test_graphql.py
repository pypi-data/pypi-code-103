from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.branch import Branch

class TestGraphql(AbstractWithRepositoryTest):
    
    def test_graphql(self):
        repository = type(self).repository
        master = repository.read_branch('master')

        schema = master.graphql_schema()
        self.assertIsNotNone(schema)

        query = '''query {
                    n_nodes {
                        title
                    }
                }'''

        query_result = master.graphql_query(query)
        self.assertIsNotNone(query_result)


