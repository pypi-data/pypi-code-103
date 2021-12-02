import Levenshtein as L

# from json import loads
# infile = 'labels.json'
# with open(infile, 'r') as jfd:
#    ref_labels = load(jfd)

ref_labels = {
    "remifentanil": [
        "remi 50",
        "uktuva 50",
        "remi",
        "remi.1",
        "ultiva 50",
        "remifantanyl",
        "remy",
    ],
    "propofol": [
        "propo",
        "propofol 10mg/ml",
        "prop",
        "dip\u00e2\u00a8rivan",
        "propof",
        "dirpivan",
        "dip",
        "oropofol 10",
    ],
    "babynoradrenaline": [
        "na dilue",
        "nad 5",
        "nad",
        "nad 5 \u00e2\u00b5g/ml",
        "nad 5gamma/ml",
        "nad 5ug/ml",
        "nad baby",
        "nad diku\u00e3\u00a9e 5 y/ml",
        "nad dilu\u00e3\u00a9e",
        "nad dilu\u00e3\u00a9e 5y/ml",
        "nad diluee",
        "nadn 5\u00e2\u00b5",
        "nora 5",
        "nora5",
        "noradr\u00e3\u00a9naline 5\u00e2\u00b5g/ml",
        "noradr\u00e3\u00a9naline dilu\u00e3\u00a9e 5y/ml",
        "noradre 5gamma",
        "noradre 5ug/ml",
        "noradrenaline",
        "noradrenaline 5 \u00e2\u00b5g/ml",
        "noradrenaline 5\u00e2\u00b5g",
        "noradrenaline 5\u00e2\u00b5g/ml",
        "noradrenaline 5gamma/ml",
        "noradrenaline 5ug/ml",
        "noradrenaline baby",
    ],
}


def is_propofol(lbl):
    for sublbl in lbl.strip().lower().split():
        if match_propofol(sublbl):
            return True
    return False


def match_propofol(lbl):
    if lbl in ref_labels['propofol']:
        return True
    if L.distance(lbl, 'propofol') <= 2:
        return True
    if L.distance(lbl, 'diprivan') <= 2:
        return True
    return False


def is_remifentanil(lbl):
    for sublbl in lbl.strip().lower().split():
        if match_remifentanil(sublbl):
            return True
    return False


def match_remifentanil(lbl):
    if lbl in ref_labels['remifentanil']:
        return True
    if L.distance(lbl, 'remifentanil') <= 2:
        return True
    if L.distance(lbl, 'ultiva') <= 2:
        return True
    return False


def is_babynoradrenaline(lbl):
    for sublbl in lbl.strip().lower().split():
        if match_babynoradrenaline(sublbl):
            return True
    return False


def match_babynoradrenaline(lbl):
    if 'baby' in lbl:
        return True
    if lbl.startswith('bb'):
        return True
    if lbl in ref_labels['babynoradrenaline']:
        return True
    return False


def detect_known_label(lbl: str) -> str:
    if is_babynoradrenaline(lbl):
        return 'babynoradrenaline'
    if is_propofol(lbl):
        return 'propofol'
    if is_remifentanil(lbl):
        return 'remifentanil'
    # Not found. Return original.
    return lbl
