from .abstract_with_repository_test import AbstractWithRepositoryTest

class TestRelease(AbstractWithRepositoryTest):
    def test_releases(self):
        repository = type(self).repository
        platform = type(self).platform

        releaseJobId = repository.start_create_release({ 'title': 'blah' })
        platform.wait_for_job_completion(releaseJobId)

        releases = repository.list_releases()
        self.assertEqual(1, len(releases))
        firstRelease = list(releases.values())[0]

        release = repository.read_release(firstRelease._doc)
        self.assertIsNotNone(release)

        queried_releases = repository.query_releases({})
        self.assertEqual(1, len(queried_releases))
