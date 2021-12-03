# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""Unit tests for checking if (subscription_id, tenant_id) pair is eyes-off"""
from shrike._core import is_eyesoff_helper
import pytest


@pytest.mark.parametrize(
    "eyes_off_subscription_id, is_eyesoff",
    [
        ("60d27411-7736-4355-ac95-ac033929fe9d", True),
        ("2ffad2ef-10c3-4793-aacc-093dc4ad2e63", False),
    ],
)
def test_is_eyesoff_Torus(eyes_off_subscription_id, is_eyesoff):
    eyes_off_tenant_id = "cdc5aeea-15c5-4db6-b079-fcadd2505dc2"

    assert is_eyesoff_helper(eyes_off_tenant_id, eyes_off_subscription_id) == is_eyesoff
