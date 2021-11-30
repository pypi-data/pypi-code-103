import re
from robot.utils import normalize, unic


def apply_all(libdoc):
    """Apply all patches."""
    patch_scope(libdoc)
    patch_params(libdoc)


def patch_scope(libdoc):
    """Convert documentation scope to RPA terminology."""
    normalized = normalize(unic(libdoc.scope), ignore="_")
    libdoc.scope = {"testcase": "Task", "testsuite": "Suite", "global": "Global"}.get(
        normalized, libdoc.scope
    )


def patch_params(libdoc):
    """Patch malformed params tables in reST documentation."""
    if libdoc.doc_format.strip().upper() != "REST":
        return

    def _replace_all(text):
        return re.sub(r":param\s+(.*):\s+", r":\1: ", text)

    try:
        libdoc.doc = _replace_all(libdoc.doc)
    except AttributeError:
        libdoc._doc = _replace_all(libdoc.doc)

    for init in libdoc.inits:
        init.doc = _replace_all(init.doc)
    for keyword in libdoc.keywords:
        keyword.doc = _replace_all(keyword.doc)
