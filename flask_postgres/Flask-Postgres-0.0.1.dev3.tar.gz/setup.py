from setuptools import setup

# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="Flask-Postgres",
    install_requires=[
        "Flask>=1.0",
        "Click>=6.0",
        "SQLAlchemy>=1.2.2",
        "Flask-SQLAlchemy>=2.4",
    ],
    extras_require={
        "tests": [
            "psycopg",
            "pytest>=6.0.1",
            "pytest-env",
            "pytest-cov",
            "pytest-postgresql"
        ]
    },
)
