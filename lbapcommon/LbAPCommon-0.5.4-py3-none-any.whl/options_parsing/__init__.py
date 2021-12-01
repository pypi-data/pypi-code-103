###############################################################################
# (c) Copyright 2021 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################

import json

import uproot


def validate_options(json_file: str, ntuple_fn: str):
    "Comparing the expected tuples with the output"

    with open(json_file, "rb") as fp:
        json_dump = json.load(fp)

    file = uproot.open(ntuple_fn)
    tupleKeys = file.keys(cycle=False)

    errorList = []

    # Checking DecayTreeTuples
    for nTuple in json_dump["DecayTreeTuple"]:
        if nTuple not in tupleKeys:
            errorList.append(f"ERROR: DecayTreeTuple {nTuple} missing in test result")

    # Checking MCDecayTreeTuples
    for nTuple in json_dump["MCDecayTreeTuple"]:
        if nTuple not in tupleKeys:
            errorList.append(f"ERROR: MCDecayTreeTuple {nTuple} missing in test result")

    # Checking MCDecayTreeTuples
    for nTuple in json_dump["EventTuple"]:
        if nTuple not in tupleKeys:
            errorList.append(f"ERROR: EventTuple {nTuple} missing in test result")

    return errorList
