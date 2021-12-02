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
from textwrap import dedent

import pytest

import LbAPCommon
from LbAPCommon import checks

pytest.importorskip("XRootD")


def test_num_entries_parsing_to_JSON():
    rendered_yaml = dedent(
        """\
    checks:
        check_num_entries:
            type: num_entries
            count: 1000
            tree_pattern: DecayTree

    job_1:
        application: DaVinci/v45r8
        input:
            bk_query: /bookkeeping/path/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
        checks:
            - check_num_entries
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)

    job_name = list(jobs_data.keys())[0]
    check_name = list(checks_data.keys())[0]

    result = checks.num_entries(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        checks_data[check_name]["count"],
        checks_data[check_name]["tree_pattern"],
    )

    check_results_with_job = {
        job_name: {
            check_name: result,
        }
    }

    checks_json = checks.checks_to_JSON(checks_data, check_results_with_job)

    json_expected = dedent(
        """\
    {
      "job_1": {
        "check_num_entries": {
          "passed": true,
          "messages": [
            "Found 5135823 in DecayTree (1000 required)"
          ],
          "input": {
            "type": "num_entries",
            "count": 1000,
            "tree_pattern": "DecayTree"
          },
          "output": {
            "DecayTree": {
              "num_entries": 5135823
            }
          }
        }
      }
    }"""
    )

    assert checks_json == json_expected


def test_range_parsing_to_JSON():
    rendered_yaml = dedent(
        """\
    checks:
        check_range:
            type: range
            expression: H1_PZ
            limits:
                min: 0
                max: 500000
            blind_ranges:
                -
                    min: 80000
                    max: 100000
                -
                    min: 180000
                    max: 200000
            tree_pattern: DecayTree

    job_1:
        application: DaVinci/v45r8
        input:
            bk_query: /bookkeeping/path/ALLSTREAMS.DST
        output: FILETYPE.ROOT
        options:
            - options.py
            - $VAR/a.py
        wg: Charm
        inform: a.b@c.d
        checks:
            - check_range
    """
    )
    jobs_data, checks_data = LbAPCommon.parse_yaml(rendered_yaml)

    job_name = list(jobs_data.keys())[0]
    check_name = list(checks_data.keys())[0]

    result = checks.range_check(
        [
            "root://eospublic.cern.ch//eos/opendata/lhcb/AntimatterMatters2017/data/B2HHH_MagnetDown.root"
        ],
        checks_data[check_name]["expression"],
        checks_data[check_name]["limits"],
        checks_data[check_name]["blind_ranges"],
        checks_data[check_name]["tree_pattern"],
    )

    check_results_with_job = {
        job_name: {
            check_name: result,
        }
    }

    checks_json = checks.checks_to_JSON(checks_data, check_results_with_job)

    json_expected = dedent(
        """\
    {
      "job_1": {
        "check_range": {
          "passed": true,
          "messages": [
            "Histogram of H1_PZ successfully filled from TTree DecayTree (contains 4776546.0 events)"
          ],
          "input": {
            "type": "range",
            "expression": "H1_PZ",
            "limits": {
              "min": 0.0,
              "max": 500000.0
            },
            "blind_ranges": [
              {
                "min": 80000.0,
                "max": 100000.0
              },
              {
                "min": 180000.0,
                "max": 200000.0
              }
            ],
            "tree_pattern": "DecayTree"
          },
          "output": {
            "DecayTree": {
              "histograms": [
                "placeholder"
              ],
              "num_entries": 4776546,
              "mean": 44931.44209225662,
              "variance": 2682154203.3712554,
              "stddev": 51789.51827707278,
              "num_entries_in_mean_window": 0
            }
          }
        }
      }
    }"""
    )

    assert checks_json == json_expected
