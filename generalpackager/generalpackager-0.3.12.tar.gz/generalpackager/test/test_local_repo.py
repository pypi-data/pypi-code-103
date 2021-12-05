
from generallibrary import Ver
from generalpackager.api.local_repo import LocalRepo

import unittest


class TestLocalRepo(unittest.TestCase):
    """ Skipped tests:
        pip_install
        pip_uninstall
        unittest
        create_sdist
        upload
        get_path_from_name
        get_repo_path_parent
        write_metadata
    """

    def test_has_metadata(self):
        self.assertEqual(True, LocalRepo().has_metadata())
        self.assertEqual(False, LocalRepo("doesntexist").has_metadata())

    def test_load_metadata(self):
        self.assertEqual(True, LocalRepo().enabled)
        self.assertEqual("generalpackager", LocalRepo().name)
        self.assertIsInstance(LocalRepo().version, Ver)
        self.assertIsInstance(LocalRepo().description, str)
        self.assertIsInstance(LocalRepo().install_requires, list)
        self.assertIsInstance(LocalRepo().extras_require, dict)
        self.assertIsInstance(LocalRepo().topics, list)
        self.assertIsInstance(LocalRepo().manifest, list)

    def test_get_metadata_dict(self):
        self.assertEqual(True, LocalRepo().get_metadata_dict()["enabled"])

    def test_exists(self):
        self.assertEqual(True, LocalRepo().exists())
        self.assertEqual(True, LocalRepo.path_exists(LocalRepo().path))

    def test_get_local_repos(self):
        self.assertEqual(LocalRepo().path.get_parent(), LocalRepo.get_repos_path())

    def test_paths(self):
        method_names = (
            "get_readme_path",
            "get_metadata_path",
            "get_git_exclude_path",
            "get_setup_path",
            "get_manifest_path",
            "get_license_path",
            "get_workflow_path",
            "get_test_path",
            "get_init_path",
        )
        local_repo = LocalRepo()
        for name in method_names:
            self.assertEqual(True, getattr(local_repo, name)().exists())

    def test_get_test_paths(self):
        self.assertLess(2, len(list(LocalRepo().get_test_paths())))

    def test_text_in_tests(self):
        self.assertEqual(True, LocalRepo().text_in_tests("stringthatexists"))
        self.assertEqual(False, LocalRepo().text_in_tests("stringthat" + "doesntexist"))

    def test_get_package_paths(self):
        package_paths = list(LocalRepo().get_package_paths_gen())
        self.assertIn(LocalRepo().get_test_path(), package_paths)
        self.assertIn(LocalRepo().path / LocalRepo().name, package_paths)
        self.assertNotIn(LocalRepo().path, package_paths)

    def test_get_changed_files(self):
        local_repo = LocalRepo()
        version = local_repo.version
        local_repo.bump_version()
        self.assertNotEqual(local_repo.version, version)
        self.assertIn("metadata.json", local_repo.git_changed_files())
        local_repo.version = version
        self.assertEqual(local_repo.version, version)

    def test_get_repo_path_child(self):
        self.assertNotEqual(None, LocalRepo.get_repo_path_child(LocalRepo().path.get_parent()))
        self.assertEqual(None, LocalRepo.get_repo_path_child(LocalRepo().path))































