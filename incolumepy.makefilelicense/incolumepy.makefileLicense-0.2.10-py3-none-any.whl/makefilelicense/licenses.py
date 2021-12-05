#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "@britodfbr"  # pragma: no cover
from incolumepy.makefilelicense.exceptions import LicenseUnavailable
from functools import partial
from pathlib import Path


def licenses(license: str = "", outputfile: str = "") -> bool:
    """
    Got license text
    :param license: [agpl apache bsl cc0 gpl lgpl mit mpl unlicense] default=mit
    :param outputfile: Output filename within license choiced.
    :return: A file named into outpufile with the license of reference
    """
    license = license.casefold() or "mit"
    outputfile = outputfile or "LICENSE"
    repo = Path(__file__).parents[0].joinpath("licenses")

    try:
        license_file = repo.joinpath(f"{license}.txt")
        Path(outputfile).write_text(license_file.read_text())
        return True
    except (AttributeError, FileNotFoundError):
        raise LicenseUnavailable("license unavailable")


license_agpl = partial(licenses, "agpl")
license_apache = partial(licenses, "apache")
license_bsl = partial(licenses, "bsl")
license_cc0 = partial(licenses, "cc0")
license_gpl = partial(licenses, "gpl")
license_lgpl = partial(licenses, "lgpl")
license_mit = partial(licenses, "MIT")
license_mpl = partial(licenses, "mpl")
unlicense = partial(licenses, "unlicense")

if __name__ == "__main__":  # pragma: no cover
    print(licenses("xpto"))
