import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

version_info = json.load(BASE_DIR.joinpath('version', 'version.json').open())

__version__ = version_info.get('version')

__epilog__ = '''ConfigFile Example:\n
\b
    #script memory  [depend_scripts] [thread]
    test1.sh 2G
    test2.sh 3G 4
    test3.sh 1G test1.sh,test2.sh
    test4.sh 1M test3.sh 5

Use Examples:\n
\b
    makejob --help
    makejob test.conf
    makejob test.conf -o test.job
    makejob test.conf -o test.job -q demo.q

Contact: {author} <{author_email}>
'''.format(**version_info)
