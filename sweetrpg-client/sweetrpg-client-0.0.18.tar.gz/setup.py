from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-client",
    install_requires=["marshmallow==3.14.1",
                      "sweetrpg-model-core",
                      "sweetrpg-api-core",
                      "sweetrpg-library-objects",
                      "requests", "jsonapi-client"],
    extras_require={},
)
