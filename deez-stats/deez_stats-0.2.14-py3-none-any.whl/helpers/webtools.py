import pathlib

HERE = (pathlib.Path(__file__).parent)

CONSTITUTION_FILE = (HERE / 'files/constitution.md')
FORMAT_FILE = (HERE / 'files/img/ranks.json')


def get_league_constitution():
    lc = open(CONSTITUTION_FILE, encoding="utf8")
    return lc
