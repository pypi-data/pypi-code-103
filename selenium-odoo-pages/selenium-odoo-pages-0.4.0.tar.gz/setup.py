import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent


def parse_requirements(file):
    required = []
    with open(file) as f:
        for req in f.read().splitlines():
            if not req.strip().startswith("#"):
                required.append(req)
    return required


version = "0.4.0"
requires = parse_requirements("requirements.txt")
tests_requires = parse_requirements("requirements.tests.txt")
README = (HERE / "README.md").read_text()

setup(
    name="selenium-odoo-pages",
    version=version,
    description="A set of pages and elements used to interact "
    "with odoo pages and widget using the page selenium objects pattern",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
    author="Pierre Verkest",
    author_email="pierreverkest84@gmail.com",
    url="https://gitlab.com/micro-entreprise/selenium-odoo-pages",
    packages=["sop", "sop.odoo", "sop.testing"],
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires + tests_requires,
    entry_points="""
    """,
)
