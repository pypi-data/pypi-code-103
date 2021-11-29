

class _SharedAPI:
    def is_general(self):
        """ Return whether name is general or not.

            :param generalpackager.api.pypi.PyPI or generalpackager.api.local_module.LocalModule or generalpackager.api.local_repo.LocalRepo or generalpackager.api.github.GitHub self: """
        return self.name.startswith("general") or self.name in ("manderageneral", )
