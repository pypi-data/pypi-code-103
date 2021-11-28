# =============================================================================
#             _____           _ _               ____            _               _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \ __ _  ___| | ____ _  __ _(_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) / _` |/ __| |/ / _` |/ _` | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  __/ (_| | (__|   < (_| | (_| | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   \__,_|\___|_|\_\__,_|\__, |_|_| |_|\__, |
# |_|    |___/                          |___/                             |___/         |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python package:     A set of helper functions to describe a Python package for setuptools.
#
# License:
# ============================================================================
# Copyright 2021-2021 Patrick Lehmann - Bötzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
"""\
A set of helper functions to describe a Python package for setuptools.
"""
from dataclasses  import dataclass
from ast          import parse as ast_parse, iter_child_nodes, Assign, Constant, Name
from pathlib      import Path
from setuptools   import (
	setup as setuptools_setup,
	find_packages as setuptools_find_packages,
	find_namespace_packages as setuptools_find_namespace_packages
)
from typing       import List, Iterable, Dict

try:
	from pyTooling.Decorators   import export
except ModuleNotFoundError:
	print("\nERROR: Could not import 'export' from 'pyTooling.Decorators' !\n")

	from typing import Callable
	def export(value: Callable) -> Callable:
		return value


__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2021-2021, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "0.3.0"


@export
@dataclass
class Readme:
	"""Encapsulates the READMEs file content and MIME type."""
	Content:  str
	MimeType: str


@export
def loadReadmeFile(readmeFile: Path) -> Readme:
	"""
	Read the README file (e.g. in Markdown format), so it can be used as long description for the package.

	Supported formats:

	  * Markdown (``*.md``)

	:param readmeFile: Path to the `README` file as an instance of :class:`Path`.
	:return:           A tuple containing the file content and the MIME type.
	"""
	if readmeFile.suffix == ".md":
		with readmeFile.open("r") as file:
			return Readme(
				Content=file.read(),
				MimeType="text/markdown"
			)
	else:
		raise ValueError("Unsupported README format.")


@export
def loadRequirementsFile(requirementsFile: Path) -> List[str]:
	"""
	Reads a `requirements.txt` file and extracts all specified dependencies into an array.

	Special dependency entries like Git repository references are translates to match the syntax expected by setuptools.

	:param requirementsFile: Path to the `requirements.txt` file as an instance of :class:`Path`.
	:return:                 A list of dependencies.
	"""

	requirements = []
	with requirementsFile.open("r") as file:
		for line in file.readlines():
			if line.startswith("#") or line == "":
				continue
			elif line.startswith("-r"):
				# Remove the first word/argument (-r)
				filename = " ".join(line.split(" ")[1:])
				requirements += loadRequirementsFile(requirementsFile.parent / filename)
			elif line.startswith("https"):
				# Convert 'URL#NAME' to 'NAME @ URL'
				splitItems = line.split("#")
				requirements.append(f"{splitItems[1]} @ {splitItems[0]}")
			else:
				requirements.append(line)

	return requirements


@export
@dataclass
class VersionInformation:
	"""Encapsulates version information extracted from a Python source file."""
	Author:    str
	Email:     str
	Copyright: str
	Version:   str


@export
def extractVersionInformation(sourceFile: Path) -> VersionInformation:
	"""
	Extract double underscored variables from a Python source file, so these can be used for single-sourcing information.

	Supported variables:

	  * ``__author__``
	  * ``__email__``
	  * ``__copyright__``
	  * ``__version__``

	:param sourceFile: Path to a Python source file as an instance of :class:`Path`.
	:return:
	"""
	_author =     None
	_email =      None
	_copyright =  None
	_version =    None

	with sourceFile.open("r") as file:
		for item in iter_child_nodes(ast_parse(file.read())):
			if isinstance(item, Assign) and len(item.targets) == 1:
				target = item.targets[0]
				value = item.value
				if isinstance(target, Name) and target.id == "__author__" and isinstance(value, Constant) and isinstance(value.value, str):
					_author = value.value
				if isinstance(target, Name) and target.id == "__email__" and isinstance(value, Constant) and isinstance(value.value, str):
					_email = value.value
				if isinstance(target, Name) and target.id == "__copyright__" and isinstance(value, Constant) and isinstance(value.value, str):
					_copyright = value.value
				if isinstance(target, Name) and target.id == "__version__" and isinstance(value, Constant) and isinstance(value.value, str):
					_version = value.value

	if _author is None:
		raise AssertionError(f"Could not extract '__author__' from '{sourceFile}'.")
	if _email is None:
		raise AssertionError(f"Could not extract '__email__' from '{sourceFile}'.")
	if _copyright is None:
		raise AssertionError(f"Could not extract '__copyright__' from '{sourceFile}'.")
	if _version is None:
		raise AssertionError(f"Could not extract '__version__' from '{sourceFile}'.")

	return VersionInformation(_author, _email, _copyright, _version)


LICENSES: Dict[str, str] = {
	# MIT
	# BSD 3-Clause
	"Apache 2.0": "License :: OSI Approved :: Apache Software License"
}

STATUS: Dict[str, str] = {
	"alpha":  "Development Status :: 3 - Alpha",
	"beta":   "Development Status :: 4 - Beta",
	"stable": "Development Status :: 5 - Production/Stable"
}

@export
def DescribePythonPackage(
	packageName: str,
	description: str,
	keywords: str,
	projectURL: str,
	sourceCodeURL: str,
	documentationURL: str,
	issueTrackerCodeURL: str,
	license: str = "Apache 2.0",
	readmeFile: Path = Path("README.md"),
	requirementsFile: Path = Path("requirements.txt"),
	sourceFileWithVersion: Path = Path("__init__.py"),
	classifiers: Iterable[str] = (
		"Operating System :: OS Independent",
		"Intended Audience :: Developers",
		"Topic :: Utilities"
	),
	developmentStatus: str = "stable",
	pythonVersions: Iterable[str] = ("3.6", "3.7", "3.8", "3.9", "3.10")
) -> None:
	# Read README for upload to PyPI
	readme = loadReadmeFile(readmeFile)

	# Read requirements file and add them to package dependency list (remove duplicates)
	requirements = list(set(loadRequirementsFile(requirementsFile)))

	# Read __author__, __email__, __version__ from source file
	versionInformation = extractVersionInformation(sourceFileWithVersion)

	# Scan for packages and source files
	exclude = ["doc", "doc.*", "tests", "tests.*"]
	if "." in packageName:
		packages = setuptools_find_namespace_packages(exclude=exclude)
		if packageName.endswith(".*"):
			packageName = packageName[:-2]
	else:
		packages = setuptools_find_packages(exclude=exclude)

	# Assemble classifiers
	classifiers = list(classifiers)

	# Translate license to classifier
	try:
		classifiers.append(LICENSES[license])
	except KeyError:
		raise ValueError(f"Unsupported license '{license}'.")

	# Translate Python versions to classifiers
	classifiers.append("Programming Language :: Python :: 3 :: Only")
	for v in pythonVersions:
		classifiers.append(f"Programming Language :: Python :: {v}")

	# Translate status to classifier
	try:
		classifiers.append(STATUS[developmentStatus])
	except KeyError:
		raise ValueError(f"Unsupported development status '{developmentStatus}'.")

	# Assemble all package information
	parameters = {
		"name": packageName,
		"version": versionInformation.Version,
		"author": versionInformation.Author,
		"author_email": versionInformation.Email,
		"license": license,
		"description": description,
		"long_description": readme.Content,
		"long_description_content_type": readme.MimeType,
		"url": projectURL,
		"project_urls": {
			'Documentation': documentationURL,
			'Source Code':   sourceCodeURL,
			'Issue Tracker': issueTrackerCodeURL
		},
		"packages": packages,
		"classifiers": classifiers,
		"keywords": keywords,
		"python_requires": f">={pythonVersions[0]}",
	  "install_requires": requirements,
	}

	setuptools_setup(**parameters)

@export
def DescribePythonPackageHostedOnGitHub(
	packageName: str,
	description: str,
	keywords: str,
	gitHubNamespace: str,
	gitHubRepository: str = None,
	projectURL: str = None,
	license: str = "Apache 2.0",
	readmeFile: Path = Path("README.md"),
	requirementsFile: Path = Path("requirements.txt"),
	sourceFileWithVersion: Path = Path("__init__.py"),
	classifiers: Iterable[str] = (
		"Operating System :: OS Independent",
		"Intended Audience :: Developers",
		"Topic :: Utilities"
	),
	developmentStatus: str = "stable",
	pythonVersions: Iterable[str] = ("3.6", "3.7", "3.8", "3.9", "3.10")
):
	gitHubRepository = gitHubRepository if gitHubRepository is not None else packageName

	# Derive URLs
	sourceCodeURL = f"https://GitHub.com/{gitHubNamespace}/{gitHubRepository}"
	documentationURL = f"https://{gitHubNamespace}.GitHub.io/{gitHubRepository}"
	issueTrackerCodeURL = f"{sourceCodeURL}/issues"

	projectURL = projectURL if projectURL is not None else sourceCodeURL

	DescribePythonPackage(
		packageName=packageName,
		description=description,
		keywords=keywords,
		projectURL=projectURL,
		sourceCodeURL=sourceCodeURL,
		documentationURL=documentationURL,
		issueTrackerCodeURL=issueTrackerCodeURL,
		license=license,
		readmeFile=readmeFile,
		requirementsFile=requirementsFile,
		sourceFileWithVersion=sourceFileWithVersion,
		classifiers=classifiers,
		developmentStatus=developmentStatus,
		pythonVersions=pythonVersions
	)
