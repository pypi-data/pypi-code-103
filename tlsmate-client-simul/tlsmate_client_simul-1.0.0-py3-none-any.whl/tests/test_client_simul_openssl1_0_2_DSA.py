# -*- coding: utf-8 -*-
"""Implements a class to be used for unit testing.
"""
import pathlib
from tlsmate import tls
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

    recorder_yaml = "recorder_client_simul_openssl1_0_2_DSA"
    path = pathlib.Path(__file__)
    server_cmd = (
        "utils/start_openssl --version {library} --port {server_port} "
        "--cert1 server-dsa -- -www -cipher ALL"
    )
    library = TlsLibrary.openssl1_0_2

    server = "localhost"

    def run(self, tlsmate, is_replaying):
        tlsmate.config.set("client_profiles", _CLIENT_PROFILES)
        ClientSimulWorker(tlsmate).run()
        client_prof = tlsmate.server_profile.client_simulation[0]
        assert client_prof.cert_type is tls.SignatureAlgorithm.DSA
        assert client_prof.cert_pub_key_size == 3072


if __name__ == "__main__":
    TestCase().entry(is_replaying=False)
