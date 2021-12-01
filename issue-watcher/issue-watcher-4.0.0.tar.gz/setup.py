# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['issue_watcher']

package_data = \
{'': ['*']}

install_requires = \
['packaging', 'requests', 'semver', 'ujson']

setup_kwargs = {
    'name': 'issue-watcher',
    'version': '4.0.0',
    'description': 'Python test cases watching when an issue is closed and failing a test to let you know fixed functionality is available.',
    'long_description': '# issue-watcher\nSometimes it happens that you discover a bug in a library that you are using and have to create a workaround (technical debt). However, it would be good to also remove the workaround once a bugfix is released.\n\nThis library provides several useful assertions that are watching when an issue is closed and failing a test to let you know fixed functionality is available. A good way to automatically manage and reduce known technical debt.\n\n![PyPI - Downloads](https://img.shields.io/pypi/dm/issue-watcher)\n![CircleCI](https://img.shields.io/circleci/build/github/radeklat/issue-watcher)\n![Codecov](https://img.shields.io/codecov/c/github/radeklat/issue-watcher)\n![PyPI - License](https://img.shields.io/pypi/l/issue-watcher)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/issue-watcher)\n![GitHub tag (latest SemVer)](https://img.shields.io/github/tag/radeklat/issue-watcher)\n![Maintenance](https://img.shields.io/maintenance/yes/2021)\n![GitHub last commit](https://img.shields.io/github/last-commit/radeklat/issue-watcher)\n\n# Installation\n\n    pip install issue-watcher\n    \n# Support\n\n## Issue trackers\n\n* GitHub\n    \n# Usage\n\nLet\'s assume you want to watch a [Safety](https://github.com/pyupio/safety) [issue #119](https://github.com/pyupio/safety/issues/119) preventing you from running the tool on Windows. Once fixed, you would like to enable it on Windows.\n\nFollowing examples will show typical steps you would take and automation available from this package.\n\n## Issue is open\n\nYou would like to be notified once the issue is resolved (closed) and enable the currently disabled behaviour. To get notified in relevant place, create the following test case:\n\n    from unittest import TestCase\n    \n    from issuewatcher import AssertGitHubIssue\n    \n    class BugsInSafetyAreFixedTestCase(TestCase):\n        def test_safety_cannot_be_enable_on_windows(self):\n            AssertGitHubIssue("pyupio/safety").is_open(\n                119, "Check if safety can be enabled on Windows."\n            )\n            \nAlternatively, with pytest:\n\n    from issuewatcher import AssertGitHubIssue\n    \n    def test_safety_cannot_be_enable_on_windows(self):\n        AssertGitHubIssue("pyupio/safety").is_open(\n            119, "Check if safety can be enabled on Windows."\n        )\n        \nOnce the issue is closed on GitHub, the test will fail with the following error message:\n\n    GitHub issue #119 from \'pyupio/safety\' is no longer open. Check if safety \n    can be enabled on Windows. Visit https://github.com/pyupio/safety/issues/119.\n    \n## Issues is closed ...\n\nYou can update the test case to watch if issue is not re-opened. Change the test case from:\n\n    def test_safety_cannot_be_enable_on_windows(self):\n        AssertGitHubIssue("pyupio/safety").is_open(\n            119, "Check if safety can be enabled on Windows."\n        )\n        \nto\n\n    def test_safety_can_be_enable_on_windows(self):\n        AssertGitHubIssue("pyupio/safety").is_closed(\n            119, "Check if safety should be disabled on Windows."\n        )\n\nThe updated test case will now fail if issue gets re-opened.\n\n## ... but fix is not released yet\n\nTo watch for the fix to be released, you can add a release watch test.\n\n### I don\'t know which version will contain the fix\n\nAssuming that there are 25 releases at the moment of writing the test:\n\n    def test_safety_fix_has_not_been_released(self):\n        AssertGitHubIssue("pyupio/safety").current_release(25)\n        \nIf you\'re not sure how many releases there are at the moment, you can leave the release number empty:\n\n    def test_safety_fix_has_not_been_released(self):\n        AssertGitHubIssue("pyupio/safety").current_release()\n        \nand the test will report it in the failing test:\n\n    This test does not have any number of releases set. Current number of releases is \'25\'.\n\n### I know the version of a release that will contain the fix\n\nSometimes the maintainer will mention which release will include the fix. Let\'s assume the release will be `2.0.0`. To get notified about it, use:\n\n    def test_safety_fix_has_not_been_released(self):\n        AssertGitHubIssue("pyupio/safety").fixed_in("2.0.0")\n        \n## Fix is released\n        \nOnce a new release is available, the test above will fail with:\n\n    New release of \'pyupio/safety\' is available. Expected 25 releases but 26 are\n    now available. Visit https://github.com/pyupio/safety/releases.\n\nor\n\n    Release \'2.0.0\' of \'pyupio/safety\' is available. Latest version is\n    \'2.2.4\'. Visit https://github.com/pyupio/safety/releases.\n    \nNow you can remove the tech debt and the release test case. However, keep the issue status test case to check for a regression.\n\n# Environment variables\n\n`GITHUB_USER_NAME`, `GITHUB_PERSONAL_ACCESS_TOKEN`: Set to GitHub user name and [personal access token](https://github.com/settings/tokens) to raise API limit from 60 requests/hour for a host to 5000 requests/hour on that API key.\n\n`CACHE_INVALIDATION_IN_SECONDS`: Set to number of seconds for invalidating cached data retrieved from HTTP calls. Default value is `3600` seconds (1 day). Use `0` to disable caching. This is useful if you run tests frequently to speed them up and prevent API quota depletion.',
    'author': 'Radek Lát',
    'author_email': 'radek.lat@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/radeklat/issue-watcher',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<=3.10',
}


setup(**setup_kwargs)
