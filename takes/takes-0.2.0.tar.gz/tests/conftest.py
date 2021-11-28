import sys
from typing import List


collect_ignore: List[str] = []


if sys.version_info < (3, 8):
    collect_ignore.append("test_posonly_args.py")
