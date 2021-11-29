"""Test functions for Aracnid API import.
"""
import aracnid_api

def test_version():
    """Tests that Aracnid API was imported successfully.
    """
    assert aracnid_api.__version__
