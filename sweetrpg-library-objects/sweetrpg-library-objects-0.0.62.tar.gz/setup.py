from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="sweetrpg-library-objects",
    install_requires=[
        "Flask==2.0.2",
        "mongoengine",
        "sweetrpg-db",
        "sweetrpg-model-core",
        "sweetrpg-api-core",
        "marshmallow-jsonapi",
    ],
)
