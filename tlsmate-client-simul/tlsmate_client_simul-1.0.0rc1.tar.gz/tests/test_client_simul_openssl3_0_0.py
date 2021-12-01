# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate_client_simul.tlsmate_client_simul import (
    ClientSimulWorker,
    _CLIENT_PROFILES,
)
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_out_yaml = "profile_client_simul_openssl3_0_0"
    recorder_yaml = "recorder_client_simul_openssl3_0_0"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa "
        "-- -www -cipher ALL"
    )
    library = TlsLibrary.openssl3_0_0

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        tlsmate.config.set("client_profiles", _CLIENT_PROFILES)
        ClientSimulWorker(tlsmate).run()


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
