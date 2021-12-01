import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

from pretix_batch_emailer import __version__


try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except Exception:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="pretix-batch-emailer",
    version=__version__,
    description="Send a Batch Email to all currently displayed orders.",
    long_description=long_description,
    url="https://github.com/bockstaller/pretix-batch-emailer",
    author="Lukas Bockstaller",
    author_email="lukas.bockstaller@posteo.de",
    license="Apache",
    install_requires=[],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretix.plugin]
pretix_batch_emailer=pretix_batch_emailer:PretixPluginMeta
""",
)
