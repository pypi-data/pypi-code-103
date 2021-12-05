

class _PackagerMetadata:
    def _topics_to_classifiers(self, *topics):
        """ :param generalpackager.Packager self: """
        classifiers = []
        for topic in topics:
            if topic.startswith("python"):
                major = topic[6]
                minor = topic[7:]
                classifiers.append(f"Programming Language :: Python :: {major}.{minor}")
            else:
                classifiers.append(self._lib[topic])
        return classifiers

    def get_topics(self):
        """ Get a complete list of topics by using package specific as well as hardcoded magic values.

            :param generalpackager.Packager self: """
        topics = self.localrepo.topics.copy()
        topics.extend([f"python{ver.replace('.', '')}" for ver in self.python])
        topics.append(f"{self.license}-license")
        topics.extend(self.os)
        return topics

    def get_classifiers(self):
        """ Get a complete list of classifiers generated from topics and other metadata.

            :param generalpackager.Packager self: """
        return self._topics_to_classifiers(*self.get_topics())

    def is_bumped(self):
        """ Return whether this package has been bumped by comparing PyPI and LocalRepo's versions.

            :param generalpackager.Packager self: """
        return self.pypi.get_version() is None or self.localrepo.version > self.pypi.get_version()

    _lib = {
        "planning": "Development Status :: 1 - Planning",
        "pre-alpha": "Development Status :: 2 - Pre-Alpha",
        "alpha": "Development Status :: 3 - Alpha",
        "beta": "Development Status :: 4 - Beta",
        "production/Stable": "Development Status :: 5 - Production/Stable",
        "mature": "Development Status :: 6 - Mature",
        "inactive": "Development Status :: 7 - Inactive",

        "utility": "Topic :: Utilities",

        "tool": "Topic :: Software Development :: Build Tools",
        "library": "Topic :: Software Development :: Libraries",
        "gui": "Topic :: Software Development :: User Interfaces",

        "file-manager": "Topic :: Desktop Environment :: File Managers",

        "mit-license": "License :: OSI Approved :: MIT License",

        "windows": "Operating System :: Microsoft :: Windows",
        "macos": "Operating System :: MacOS",
        "ubuntu": "Operating System :: POSIX :: Linux",
    }
