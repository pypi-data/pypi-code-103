#!/bin/python3

import pytest
from GitAutoVersion import *
from git import Repo

class Validation:


    version_string = "12.3.2-pre.1+23!DIRTY#commit=2432de.branch=master"

    def test_StringValidation(self, version_string):

        version_string = parseVersionString(version_string)


# print(GitAutoVersion)
# print(GitAutoVersion.__file__)

git_repo = Repo("../..")
print(getVersionString(git_repo))

# print(Validation.test_StringValidation)