from .abstract_test import AbstractTest
from cloudcms.repository import Repository
from cloudcms.error import RequestError

class TestRepository(AbstractTest):
    
    def test_repositories(self):
        platform = type(self).platform

        repositories = platform.list_repositories()
        self.assertTrue(len(repositories) > 0)
        for rep in repositories.values():
            self.assertIsInstance(rep, Repository)

        repository = platform.create_repository()
        self.assertIsInstance(repository, Repository)
        self.assertEqual('/repositories/' + repository._doc, repository.uri())

        repositoryRead = platform.read_repository(repository._doc)
        self.assertEqual(repository.data, repositoryRead.data)

        repository.delete()
        ex = False
        repositoryRead = None
        try:
            repositoryRead = platform.read_repository(repository._doc)
        except RequestError:
            ex = True

        self.assertTrue(ex)
        self.assertIsNone(repositoryRead)
