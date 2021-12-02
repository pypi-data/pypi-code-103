from setuptools import setup, find_packages
import versioneer

from pathlib import Path

here = Path(__file__).resolve().parent
long_description = here.joinpath("README.md").read_text()

setup(
    name="acondbs",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="A GraphQL server for product DB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Simons Observatory",
    author_email="so_software@simonsobservatory.org",
    url="https://github.com/simonsobs/acondbs",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(exclude=["docs", "tests"]),
    include_package_data=True,
    install_requires=[
        "SQLAlchemy>=1.4",
        "SQLAlchemy-Utils>=0.37",
        "Flask>=2.0",
        "Flask-Cors>=3.0",
        "Flask-GraphQL>=2.0",
        "Flask-Migrate>=3.1",
        "Flask-SQLAlchemy>=2.5",
        "graphene-sqlalchemy>=2.3",
        "graphene-sqlalchemy-filter>=1.10",
        "cryptography>=3.2",
        "gitpython>=3.1",
        "requests>=2.24",
        "a2wsgi>=1.4"
    ],
    extras_require={
        "tests": [
            "pytest>=6.2",
            "pytest-cov>=2.12",
            'pytest-asyncio>=0.14',
            "snapshottest>=0.6",
            "async-asgi-testclient>=1.4.6",
            "sqlparse",
        ]
    },
)
