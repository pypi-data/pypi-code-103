# -*- coding: utf-8 -*-
"""Implement unit tests for the client simulation.
"""
import re
import yaml
import io

from tlsmate.workers.server_profile import ReadProfileWorker
from tlsmate.workers.text_server_profile import TextProfileWorker
import tlsmate_client_simul  # noqa


def test_openssl3_0_0(tlsmate, style_file, server_profile_openssl3_0_0, capsys):
    tlsmate.config.set("read_profile", str(server_profile_openssl3_0_0))
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    ReadProfileWorker(tlsmate).run()
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert "Handshake simulation" in captured.out
    assert re.match(
        r".*Android 2\.3\.7\s+handshake simulation failed", captured.out, re.DOTALL
    )
    assert re.match(
        (
            r".*Firefox 73 / Win 10\s+TLS13\s+ECDSA \(384 bits\)\s+ECDH "
            r"\(X25519\)\s+TLS_AES_128_GCM_SHA256"
        ),
        captured.out,
        re.DOTALL,
    )


def test_openssl1_0_2_DHE(tlsmate, style_file, server_profile_openssl1_0_2_DHE, capsys):
    tlsmate.config.set("read_profile", str(server_profile_openssl1_0_2_DHE))
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    ReadProfileWorker(tlsmate).run()
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert "Handshake simulation" in captured.out
    assert re.match(
        r".*Android 7\.0\s+handshake simulation failed", captured.out, re.DOTALL
    )
    assert re.match(
        (
            r".*Firefox 73 / Win 10\s+TLS12\s+RSA \(2048 bits\)\s+"
            r"DH \(2048 bits\)\s+TLS_DHE_RSA_WITH_AES_128_CBC_SHA"
        ),
        captured.out,
        re.DOTALL,
    )


def test_status_skipped(tlsmate, style_file, capsys):
    yaml_data = """
client_simulation:
- name: Android 2.3.7
  status: SKIPPED
"""
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert re.match(
        r".*handshake simulation skipped, no common TLS protocol version found",
        captured.out,
        re.DOTALL,
    )


def test_no_simul(tlsmate, style_file, capsys):
    yaml_data = """
versions:
-   support: UNDETERMINED
    version:
        id: 512
        name: SSL20

"""
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert "Handshake simulation" not in captured.out


def test_cert(tlsmate, style_file, capsys):
    yaml_data = """
client_simulation:
- cipher_suite:
    id: 27
    name: TLS_DH_ANON_WITH_3DES_EDE_CBC_SHA
  key_ex_type: DH
  key_ex_size: 2048
  name: Android 4.4.2
  status: OK
  version:
    id: 771
    name: TLS12
"""
    data = yaml.safe_load(io.StringIO(yaml_data))
    tlsmate.server_profile.load(data)
    tlsmate.config.set("style", str(style_file))
    tlsmate.config.set("color", False)
    TextProfileWorker(tlsmate).run()
    captured = capsys.readouterr()
    assert re.match(
        (
            r".*Android 4\.4\.2\s+TLS12\s+DH \(2048 bits\)\s+"
            r"TLS_DH_ANON_WITH_3DES_EDE_CBC_SHA"
        ),
        captured.out,
        re.DOTALL,
    )
