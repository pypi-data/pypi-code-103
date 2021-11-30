#!/usr/bin/env python3

# Libervia: an XMPP client
# Copyright (C) 2009-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""TLS handling with twisted"""

from sat.core.log import getLogger
from sat.core import exceptions
from sat.tools import config as tools_config


try:
    import OpenSSL
    from twisted.internet import ssl
except ImportError:
    ssl = None


log = getLogger(__name__)


def getOptionsFromConfig(config, section=""):
    options = {}
    for option in ('tls_certificate', 'tls_private_key', 'tls_chain'):
        options[option] = tools_config.getConfig(config, section, option)
    return options


def TLSOptionsCheck(options):
    """Check options coherence if TLS is activated, and update missing values

    Must be called only if TLS is activated
    """
    if not options["tls_certificate"]:
        raise exceptions.ConfigError(
            "a TLS certificate is needed to activate HTTPS connection")
    if not options["tls_private_key"]:
        options["tls_private_key"] = options["tls_certificate"]


def loadCertificates(f):
    """Read a .pem file with a list of certificates

    @param f (file): file obj (opened .pem file)
    @return (list[OpenSSL.crypto.X509]): list of certificates
    @raise OpenSSL.crypto.Error: error while parsing the file
    """
    # XXX: didn't found any method to load a .pem file with several certificates
    #      so the certificates split is done here
    certificates = []
    buf = []
    while True:
        line = f.readline()
        buf.append(line)
        if "-----END CERTIFICATE-----" in line:
            certificates.append(
                OpenSSL.crypto.load_certificate(
                    OpenSSL.crypto.FILETYPE_PEM, "".join(buf)
                )
            )
            buf = []
        elif not line:
            log.debug(f"{len(certificates)} certificate(s) found")
            return certificates


def loadPKey(f):
    """Read a private key from a .pem file

    @param f (file): file obj (opened .pem file)
    @return (list[OpenSSL.crypto.PKey]): private key object
    @raise OpenSSL.crypto.Error: error while parsing the file
    """
    return OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, f.read())


def loadCertificate(f):
    """Read a public certificate from a .pem file

    @param f (file): file obj (opened .pem file)
    @return (list[OpenSSL.crypto.X509]): public certificate
    @raise OpenSSL.crypto.Error: error while parsing the file
    """
    return OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, f.read())


def getTLSContextFactory(options):
    """Load TLS certificate and build the context factory needed for listenSSL"""
    if ssl is None:
        raise ImportError("Python module pyOpenSSL is not installed!")

    cert_options = {}

    for name, option, method in [
        ("privateKey", "tls_private_key", loadPKey),
        ("certificate", "tls_certificate", loadCertificate),
        ("extraCertChain", "tls_chain", loadCertificates),
    ]:
        path = options[option]
        if not path:
            assert option == "tls_chain"
            continue
        log.debug(f"loading {option} from {path}")
        try:
            with open(path) as f:
                cert_options[name] = method(f)
        except IOError as e:
            raise exceptions.DataError(
                f"Error while reading file {path} for option {option}: {e}"
            )
        except OpenSSL.crypto.Error:
            raise exceptions.DataError(
                f"Error while parsing file {path} for option {option}, are you sure "
                f"it is a valid .pem file?"
            )
            if (
                option == "tls_private_key"
                and options["tls_certificate"] == path
            ):
                raise exceptions.ConfigError(
                    f"You are using the same file for private key and public "
                    f"certificate, make sure that both a in {path} or use "
                    f"--tls_private_key option"
                )

    return ssl.CertificateOptions(**cert_options)
