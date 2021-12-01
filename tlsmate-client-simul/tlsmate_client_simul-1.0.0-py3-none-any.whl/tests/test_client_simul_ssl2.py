# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate_client_simul.tlsmate_client_simul import (
    ClientSimulWorker,
    _CLIENT_PROFILES,
    ClientStatus,
)
from tlsmate.tlssuite import TlsSuiteTester
from tlsmate.tlssuite import TlsLibrary


class TestCase(TlsSuiteTester):
    """Class used for tests with pytest.

    For more information refer to the documentation of the TcRecorder class.
    """

    sp_in_yaml = "profile_basic_ssl2"
    recorder_yaml = "recorder_client_simul_ssl2"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-rsa --cert2 server-ecdsa --no-cert-chain "
        "-- -www -cipher ALL -ssl2"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        tlsmate.config.set("client_profiles", _CLIENT_PROFILES)
        ClientSimulWorker(tlsmate).run()
        assert (
            tlsmate.server_profile.client_simulation[0].status is ClientStatus.SKIPPED
        )


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
