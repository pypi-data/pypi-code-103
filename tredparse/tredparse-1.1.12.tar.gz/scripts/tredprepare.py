#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Copyright (c) 2015-2017 Human Longevity Inc.

Author: Haibao Tang <htang@humanlongevity.com>
License: Non-Commercial Use Only. For details, see `LICENSE` file

Prepare details of an STR locus for computation with TREDPARSE.

The script progresses by asking a few key questions:
- Locus name
- Motif
- Expected number of motifs
- Chromosomal start location
"""

import sys
import json

from pyfaidx import Fasta
from tredparse.jcvi import mkdir
from tredparse.meta import TREDsRepo


def survey_var(s, cast=str, default=""):
    """Convenience function to get variable from command line survey."""
    res = input("{} [{}]: ".format(s, default))
    if res == "":
        res = default
    return cast(res)


def main():
    # Conduct survey
    name = survey_var("Enter the locus name", default="HD")
    repeat = survey_var("Sequence motif", default="CAG")
    nrepeat = survey_var("Number of motifs in reference", cast=int, default=19)
    location = survey_var(
        "Chromosomal start location (1-based)", default="chr4:3074877"
    )
    ref = survey_var("Enter the FASTA path", default="/mnt/ref/hg38.upper.fa")

    # Extract sequences
    f = Fasta(ref)
    c, start = location.split(":")
    start = int(start)
    size = len(repeat) * nrepeat
    end = start + size - 1
    tract = f[c][start - 1 : end].seq.lower()
    flank = 18
    prefix = f[c][start - flank - 1 : start - 1].seq.upper()
    suffix = f[c][end : end + flank].seq.upper()
    print("|".join((prefix, tract, suffix)), file=sys.stderr)

    # Populate the TRED
    repo = TREDsRepo()
    s = repo.create_tred()
    s["id"] = "{}_{}_{}".format(c, start, repeat)
    s["prefix"] = prefix
    s["suffix"] = suffix
    s["repeat"] = "CAG"
    s["repeat_location"] = "{}:{}-{}".format(c, start, end)
    tred = {name: s}

    # Serialize
    mkdir("sites")
    outfile = "sites/{}.json".format(name)
    fw = open(outfile, "w")
    print(json.dumps(tred, sort_keys=True, indent=2), file=fw)
    fw.close()

    print(file=sys.stderr)
    print("Template json file is written to `{}`".format(outfile), file=sys.stderr)
    print("Please manually fill in the remaining details", file=sys.stderr)


if __name__ == "__main__":
    main()
