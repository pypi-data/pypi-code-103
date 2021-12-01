# -*- coding: utf-8 -*-
"""Define common fixtures
"""
import pytest
import pathlib

from tlsmate.tlsmate import TlsMate


@pytest.fixture
def style_file():
    from tlsmate import __file__ as tlsmate_file

    return pathlib.Path(tlsmate_file).parent.resolve() / "styles/default.yaml"


@pytest.fixture
def tlsmate():
    return TlsMate()


@pytest.fixture
def server_profile_openssl3_0_0():
    return (
        pathlib.Path(__file__).parent.resolve()
        / "recordings/profile_client_simul_openssl3_0_0.yaml"
    )


@pytest.fixture
def server_profile_openssl1_0_2_DHE():
    return (
        pathlib.Path(__file__).parent.resolve()
        / "recordings/profile_client_simul_openssl1_0_2_DHE.yaml"
    )
