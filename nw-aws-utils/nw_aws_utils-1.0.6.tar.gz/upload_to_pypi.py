#!/usr/bin/env python3
from subprocess import call
from new_version import get_current_version

v = get_current_version()
call(["python3", "setup.py", "sdist", "bdist_wheel"])
call(["python3", "-m", "twine", "upload", "dist/nw_aws_utils-{}*".format(v)])
