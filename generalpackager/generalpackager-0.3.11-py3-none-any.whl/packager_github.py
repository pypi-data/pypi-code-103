
from generalpackager import PACKAGER_GITHUB_API

from git import Repo


class _PackagerGitHub:
    """ Sync metadata. """
    def __init__(self):
        self.commit_sha = "master"

    def sync_github_metadata(self):
        """ Sync GitHub with local metadata.

            :param generalpackager.Packager self: """
        self.github.set_website(self.pypi.url)
        self.github.set_description(self.localrepo.description)
        self.github.set_topics(*self.get_topics())

    def commit_and_push(self, message=None, tag=False):
        """ Commit and push this local repo to GitHub.
            Return short sha1 of pushed commit.

            :param generalpackager.Packager self:
            :param message:
            :param tag: """
        repo = Repo(str(self.path))
        repo.git.add(A=True)
        repo.index.commit(message=str(message) or "Automatic commit.")
        remote = repo.remote()
        remote.set_url(f"https://Mandera:{PACKAGER_GITHUB_API}@github.com/{self.github.owner}/{self.name}.git")

        if tag:
            tag_ref = repo.create_tag(f"v{self.localrepo.version}", force=True)
            remote.push(refspec=tag_ref)
        try:
            self.commit_sha = remote.push()[0].summary.split("..")[1].rstrip()
        except OSError:  # Just suppressing weird invalid handle error
            pass
        return self.commit_sha













