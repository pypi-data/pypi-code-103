# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pydupes']
install_requires = \
['click', 'tqdm>=4,<5']

entry_points = \
{'console_scripts': ['pydupes = pydupes:main']}

setup_kwargs = {
    'name': 'pydupes',
    'version': '0.4.0',
    'description': 'A duplicate file finder that may be faster in environments with millions of files and terabytes of data.',
    'long_description': '`pydupes` is yet another duplicate file finder like rdfind/fdupes et al\nthat may be faster in environments with millions of files and terabytes\nof data or over high latency filesystems (e.g. NFS).\n\n[![PyPI version](https://badge.fury.io/py/pydupes.svg)](https://badge.fury.io/py/pydupes)\n\n-------------------\n\nThe algorithm is similar to [rdfind](https://github.com/pauldreik/rdfind) with threading and consolidation of\nfiltering logic (instead of separate passes).\n- traverse the input paths, collecting the inodes and file sizes\n- for each set of files with the same size:\n  - further split by matching 4KB on beginning/ends of files\n  - for each non-unique (by size, boundaries) candidate set, compute the sha256 and emit pairs with matching hash\n\nConstraints:\n- traversals do not span multiple devices\n- symlink following not implemented\n- concurrent modification of a traversed directory could produce false duplicate pairs \n(modification after hash computation)\n\n## Setup\n```bash\n# via pip\npip3 install --user --upgrade pydupes\n\n# or simply if pipx installed:\npipx run pydupes --help\n```\n\n## Usage\n\n```bash\n# Collect counts and stage the duplicate files, null-delimited source-target pairs:\npydupes /path1 /path2 --progress --output dupes.txt\n\n# Sanity check a hardlinking of all matches:\nxargs -0 -n2 echo ln --force --verbose < dupes.txt\n```\n\n## Benchmarks\nHardware is a 6 spinning disk RAID5 ext4 with\n250GB memory, Ubuntu 18.04. Peak memory and runtimes via:\n```/usr/bin/time -v```.\n\n### Dataset 1:\n- Directories: ~33k\n- Files: ~14 million, 1 million duplicate\n- Total size: ~11TB, 300GB duplicate\n\n#### pydupes\n- Elapsed (wall clock) time (h:mm:ss or m:ss): 39:04.73\n- Maximum resident set size (kbytes): 3356936 (~3GB)\n```\nINFO:pydupes:Traversing input paths: [\'/raid/erik\']\nINFO:pydupes:Traversal time: 209.6s\nINFO:pydupes:Cursory file count: 14416742 (10.9TiB), excluding symlinks and dupe inodes\nINFO:pydupes:Directory count: 33376\nINFO:pydupes:Number of candidate groups: 720263\nINFO:pydupes:Size filter reduced file count to: 14114518 (7.3TiB)\nINFO:pydupes:Comparison time: 2134.6s\nINFO:pydupes:Total time elapsed: 2344.2s\nINFO:pydupes:Number of duplicate files: 936948\nINFO:pydupes:Size of duplicate content: 304.1GiB\n```\n\n#### rdfind\n- Elapsed (wall clock) time (h:mm:ss or m:ss): 1:57:20\n- Maximum resident set size (kbytes): 3636396 (~3GB)\n```\nNow scanning "/raid/erik", found 14419182 files.\nNow have 14419182 files in total.\nRemoved 44 files due to nonunique device and inode.\nNow removing files with zero size from list...removed 2396 files\nTotal size is 11961280180699 bytes or 11 TiB\nNow sorting on size:removed 301978 files due to unique sizes from list.14114764 files left.\nNow eliminating candidates based on first bytes:removed 8678999 files from list.5435765 files left.\nNow eliminating candidates based on last bytes:removed 3633992 files from list.1801773 files left.\nNow eliminating candidates based on md5 checksum:removed 158638 files from list.1643135 files left.\nIt seems like you have 1643135 files that are not unique\nTotally, 304 GiB can be reduced.\n```\n\n#### fdupes\nNote that this isn\'t a fair comparison since fdupes additionally performs a byte-by-byte comparison on\nMD5 match. Invocation with "fdupes --size --summarize --recurse --quiet".\n- Elapsed (wall clock) time (h:mm:ss or m:ss): 2:58:32\n- Maximum resident set size (kbytes): 3649420 (~3GB)\n```\n939588 duplicate files (in 705943 sets), occupying 326547.7 megabytes\n```\n',
    'author': 'Erik Reed',
    'author_email': 'erik.reed@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/erikreed/pydupes',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
