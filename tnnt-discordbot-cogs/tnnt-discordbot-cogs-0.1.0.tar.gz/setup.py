"""
Application setup
"""

import os

from setuptools import find_packages, setup

from tnnt_discordbot_cogs import __version__

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

package_name = "tnnt-discordbot-cogs"
package_description = "TN-NT customized cogs for aa-discordbot"
package_license = "GPLv3"
package_author = "Peter Pfeufer"
package_author_email = "development@ppfeufer.de"
package_git_url = "https://github.com/terra-nanotech/tn-nt-discordbot-cogs"
package_issues_url = f"{package_git_url}/issues"
package_changelog_url = f"{package_git_url}/blob/master/CHANGELOG.md"
project_homepage_url = package_git_url
project_python_requires = "~=3.7"
package_install_requirements = ["allianceauth>=2.9.3", "allianceauth-discordbot>=0.5.3"]
package_classifiers = [
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 3.2",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
]

# URLs are listed in reverse on Pypi
project_urls = {
    "Issue / Bug Reports": package_issues_url,
    "Change Log": package_changelog_url,
    "Git Repository": package_git_url,
}

setup(
    name=package_name,
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license=package_license,
    description=package_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=project_homepage_url,
    project_urls=project_urls,
    author=package_author,
    author_email=package_author_email,
    classifiers=package_classifiers,
    python_requires=project_python_requires,
    install_requires=package_install_requirements,
)
