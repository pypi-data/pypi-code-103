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
import re
from pathlib import Path

import pytest

from LbAPCommon import checks

pytest.importorskip("XRootD")


def test_num_entries_passing():
    result = checks.num_entries(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        1000,
        "DecayTree",
    )
    assert result.passed
    assert result.messages == ["Found 5135823 in DecayTree (1000 required)"]
    assert result.tree_data["DecayTree"]["num_entries"] == 5135823


def test_num_entries_passing_multiple_files():
    result = checks.num_entries(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root",
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetUp.root",
        ],
        1000,
        "DecayTree",
    )
    assert result.passed
    assert result.messages == ["Found 8556118 in DecayTree (1000 required)"]
    assert result.tree_data["DecayTree"]["num_entries"] == 8556118


def test_num_entries_failing():
    result = checks.num_entries(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        1000000000,
        "DecayTree",
    )
    assert not result.passed
    assert result.messages == ["Found 5135823 in DecayTree (1000000000 required)"]
    assert result.tree_data["DecayTree"]["num_entries"] == 5135823


def test_num_entries_failing_tree_name():
    result = checks.num_entries(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        1000000000,
        "RandomName",
    )
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    for _key, data in result.tree_data.items():
        assert data["histograms"] == []


def test_num_entries_per_invpb_passing():
    file_list = [Path(__file__).parent.absolute() / "example_tuple_with_lumi.root"]
    result = checks.num_entries_per_invpb(file_list, 10000, "DecayTree", "LumiTuple")
    assert result.passed
    assert result.messages == [
        "Found 23026.2 entries per unit luminosity (pb-1) in DecayTree (10000 required)"
    ]
    assert result.tree_data["DecayTree"]["num_entries_per_invpb"] == 23026.2


def test_num_entries_per_invpb_failing():
    file_list = [Path(__file__).parent.absolute() / "example_tuple_with_lumi.root"]
    result = checks.num_entries_per_invpb(file_list, 100000, "DecayTree", "LumiTuple")
    assert not result.passed
    assert result.messages == [
        "Found 23026.2 entries per unit luminosity (pb-1) in DecayTree (100000 required)"
    ]
    assert result.tree_data["DecayTree"]["num_entries_per_invpb"] == 23026.2


def test_num_entries_per_invpb_failing_MC():
    result = checks.num_entries_per_invpb(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        10000,
        "DecayTree",
    )
    assert not result.passed
    assert result.messages == [
        "Failed to get luminosity information (total luminosity = 0)"
    ]


def test_num_entries_per_invpb_failing_MC_nameTTree():
    result = checks.num_entries_per_invpb(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        10000,
        "RandomName",
    )
    assert not result.passed
    assert result.messages == [
        "No TTree objects found that match RandomName",
    ]


def test_range_check_passing():
    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        "H1_PZ",
        {"min": 0.0, "max": 500000.0},
        [],
        "DecayTree",
    )
    assert result.passed
    assert result.messages == [
        "Histogram of H1_PZ successfully filled from TTree DecayTree (contains 5134459.0 events)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 5134459


def test_range_check_passing_multiple_files():
    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root",
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetUp.root",
        ],
        "H1_PZ",
        {"min": 0.0, "max": 500000.0},
        [],
        "DecayTree",
    )
    assert result.passed
    assert result.messages == [
        "Histogram of H1_PZ successfully filled from TTree DecayTree (contains 8553802.0 events)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 8553802


def test_range_check_failing_range():
    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        "H1_PZ",
        {"min": -100000.0, "max": -99999.0},
        [],
        "DecayTree",
    )
    assert not result.passed
    assert result.messages == ["No events found in range for Tree DecayTree"]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_failing_missing_branch():
    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        "Dst_M",
        {"min": 1800.0, "max": 2300.0},
        [],
        "DecayTree",
    )
    message = result.messages[0]
    pattern = r"Missing branch in "
    matched = False
    if re.match(pattern, message):
        matched = True
    assert not result.passed
    assert matched
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_failing_tree_name():
    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        "H1_PZ",
        {"min": 0.0, "max": 500000.0},
        [],
        "RandomName",
    )
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    assert list(result.tree_data.keys()) == []


def test_range_check_failing_bad_mean():
    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        "H1_PZ",
        {"min": 0.0, "max": 500000.0},
        [],
        "DecayTree",
        500000.0,
        0.0,
        1.0,
        0.0,
    )
    assert not result.passed
    assert result.messages == [
        "The observed mean (49110.65313794501) differs from the expected value by 450889.346862055 (<=1.0 required)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 5134459


def test_range_check_failing_bad_stddev():
    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        "H1_PZ",
        {"min": 0.0, "max": 500000.0},
        [],
        "DecayTree",
        0.0,
        500000.0,
        0.0,
        1.0,
    )
    assert not result.passed
    assert result.messages == [
        "The observed standard deviation (53099.76473607609) differs from the expected value by 446900.2352639239 (<=1.0 required)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []
    assert result.tree_data["DecayTree"]["num_entries"] == 5134459


def test_range_check_nd_passing():
    result = checks.range_check_nd(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        {"x": "H1_PZ", "y": "H2_PZ"},
        {"x": {"min": 0.0, "max": 500000.0}, "y": {"min": 0.0, "max": 500000.0}},
        [
            {
                "x": {"min": 20000.0, "max": 40000.0},
                "y": {"min": 20000.0, "max": 40000.0},
            }
        ],
        "DecayTree",
    )
    assert result.passed
    assert result.messages == [
        "Histogram of {'x': 'H1_PZ', 'y': 'H2_PZ'} successfully filled from TTree DecayTree (contains 4879124.0 events)"
    ]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    assert not result.tree_data["DecayTree"]["histograms"] == []


def test_range_check_nd_failing_num_var():
    result = checks.range_check_nd(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        {"x": "H1_PZ"},
        {"x": {"min": 0.0, "max": 500000.0}},
        [],
        "DecayTree",
    )
    assert not result.passed
    assert result.messages == [
        "Expected at least two variables, but not more than four."
    ]
    assert list(result.tree_data.keys()) == []


def test_range_check_nd_failing_missing_limit():
    result = checks.range_check_nd(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        {"x": "H1_PZ", "y": "H2_PZ"},
        {"x": {"min": 0.0, "max": 500000.0}},
        [],
        "DecayTree",
    )
    assert not result.passed
    assert result.messages == [
        "For each variable, a corresponding range should be defined."
    ]
    assert list(result.tree_data.keys()) == []


def test_range_check_nd_failing_missing_branch():
    result = checks.range_check_nd(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        {"x": "H1_PZ", "y": "Dst_M-D0_M"},
        {"x": {"min": 0.0, "max": 500000.0}, "y": {"min": 138.0, "max": 150.0}},
        [],
        "DecayTree",
    )
    message = result.messages[0]
    pattern = r"Missing branch in "
    matched = False
    if re.match(pattern, message):
        matched = True
    assert not result.passed
    assert matched
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_nd_failing_range():
    result = checks.range_check_nd(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        {"x": "H1_PZ", "y": "H2_PZ"},
        {
            "x": {"min": -1000000.0, "max": -999999.0},
            "y": {"min": -1000000.0, "max": -999999.0},
        },
        [],
        "DecayTree",
    )
    assert not result.passed
    assert result.messages == ["No events found in range for Tree DecayTree"]
    assert list(result.tree_data.keys()) == ["DecayTree"]
    for h in result.tree_data["DecayTree"]["histograms"]:
        assert h.sum() == 0


def test_range_check_nd_failing_tree_name():
    result = checks.range_check_nd(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        {"x": "H1_PZ", "y": "H2_PZ"},
        {"x": {"min": 0.0, "max": 1.0}, "y": {"min": 0.0, "max": 1.0}},
        [],
        "RandomName",
    )
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    assert list(result.tree_data.keys()) == []


def test_range_check_bkg_subtracted_passing():
    result = checks.range_check_bkg_subtracted(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
        "D0_PT",
        {"min": 0.0, "max": 500000.0},
        "D0_MM",
        1865.0,
        30.0,
        10.0,
        20.0,
        [],
        "DecayTree",
    )
    assert result.passed
    assert (
        result.messages[0]
        == "Background subtraction performed successfully for Tree DecayTree"
    )
    assert list(result.tree_data.keys())[0] == "DecayTree"
    assert not result.tree_data["DecayTree"]["histograms"] == []


def test_range_check_bkg_subtracted_failing_range():
    result = checks.range_check_bkg_subtracted(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
        "D0_PT",
        {"min": -1000000.0, "max": -99999.0},
        "D0_MM",
        1865.0,
        30.0,
        10.0,
        20.0,
        [],
        "DecayTree",
    )
    assert not result.passed
    assert (
        result.messages[0]
        == "Not enough events for background subtraction found in range for Tree DecayTree"
    )
    assert list(result.tree_data.keys())[0] == "DecayTree"


def test_range_check_bkg_subtracted_failing_missing_branch():
    result = checks.range_check_bkg_subtracted(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
        "D0_PT",
        {"min": -1000000.0, "max": -99999.0},
        "Dst_M",
        1865.0,
        30.0,
        10.0,
        20.0,
        [],
        "DecayTree",
    )
    message = result.messages[0]
    print(message)
    pattern = r"Missing branch in "
    matched = False
    if re.match(pattern, message):
        matched = True
    assert not result.passed
    assert matched
    assert list(result.tree_data.keys())[0] == "DecayTree"


def test_range_check_bkg_subtracted_failing_tree_name():
    result = checks.range_check_bkg_subtracted(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/MasterclassDatasets/D0lifetime/2014/MasterclassData.root"
        ],
        "D0_PT",
        {"min": -1000000.0, "max": -99999.0},
        "D0_MM",
        1865.0,
        30.0,
        10.0,
        20.0,
        [],
        "RandomName",
    )
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
    assert list(result.tree_data.keys()) == []


def test_branches_exist_passing():
    result = checks.branches_exist(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        ["H1_PZ", "H2_PZ"],
        "DecayTree",
    )
    assert result.passed
    assert result.messages == ["All required branches were found in Tree DecayTree"]


def test_branches_exist_failing_missing_branches():
    result = checks.branches_exist(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        ["H1_PZ", "H2_PZ", "RandomName"],
        "DecayTree",
    )
    assert not result.passed
    assert result.messages == [
        "Required branches not found in Tree DecayTree: ['RandomName']"
    ]


def test_branches_exist_failing_tree_name():
    result = checks.branches_exist(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        ["H1_PZ", "H2_PZ", "RandomName"],
        "RandomName",
    )
    assert not result.passed
    assert result.messages == ["No TTree objects found that match RandomName"]
