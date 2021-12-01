# -*- coding: utf-8 -*-
"""Module for client simulation plugin

This plugin extends tlsmate by a client simulation. For selected entries of the
client data base a handshake is performed, and the result including basic
negotiated parameters is stored in the server profile.
"""
# import basic stuff
import pathlib
import enum

# import own stuff
from tlsmate import utils
from tlsmate import tls
from tlsmate.plugin import Plugin, Worker, Args, BaseCommand
from tlsmate.structs import ConfigItem
from tlsmate.workers.scanner_info import ScanStart, ScanEnd
from tlsmate.plugins.scan import (
    GroupBasicScan,
    GroupX509,
    GroupServerProfile,
    SubcommandScan,
)
from tlsmate.server_profile import (
    SPObject,
    ProfileSchema,
    FieldsEnumString,
    SPVersionEnumSchema,
    SPCipherSuiteSchema,
    SPSupportedGroupEnumSchema,
    ServerProfileSchema,
)
from tlsmate.workers.text_server_profile import (
    Style,
    TextProfileWorker,
    get_style_applied,
)

# import other stuff
from marshmallow import fields
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ed448, dsa, ec

_CLIENT_PROFILES = pathlib.Path(__file__).parent.resolve() / "data/getClients.json"

_client_white_list = [
    56,  # Android 2.3.7
    58,  # Android 4.0.4
    59,  # Android 4.1.1
    60,  # Android 4.2.2
    61,  # Android 4.3
    62,  # Android 4.4.2
    88,  # Android 5.0.0
    129,  # Android 6.0
    167,  # Android 7.0
    168,  # Android 8.0
    157,  # Android 8.1
    158,  # Android 9.0
    94,  # Baidu Jan 2015
    91,  # BingPreview Jan 2015
    136,  # Chrome 49 / XP SP3
    152,  # Chrome 69 / Win 7
    153,  # Chrome 70 / Win 10
    170,  # Chrome 80 / Win 10
    84,  # Firefox 31.3.0 ESR / Win 7
    132,  # Firefox 47 / Win 7
    137,  # Firefox 49 / XP SP3
    151,  # Firefox 62 / Win 7
    171,  # Firefox 73 / Win 10
    145,  # Googlebot Feb 2018
    100,  # IE 6 / XP
    19,  # IE 7 / Vista
    101,  # IE 8 / XP
    113,  # IE 8-10 / Win 7
    143,  # IE 11 / Win 7
    134,  # IE 11 / Win 8.1
    64,  # IE 10 / Win Phone 8.0
    65,  # IE 11 / Win Phone 8.1
    106,  # IE 11 / Win Phone 8.1 Update
    131,  # IE 11 / Win 10
    144,  # Edge 15 / Win 10
    159,  # Edge 16 / Win 10
    160,  # Edge 18 / Win 10
    120,  # Edge 13 / Win Phone 10
    25,  # Java 6u45
    26,  # Java 7u25
    147,  # Java 8u161
    162,  # Java 11.0.3
    163,  # Java 12.0.1
    27,  # OpenSSL 0.9.8y
    99,  # OpenSSL 1.0.1l
    164,  # OpenSSL 1.0.2s
    169,  # OpenSSL 1.1.0k
    165,  # OpenSSL 1.1.1c
    32,  # Safari 5.1.9 / OS X 10.6.8
    33,  # Safari 6 / iOS 6.0.1
    34,  # Safari 6.0.4 / OS X 10.8.4
    63,  # Safari 7 / iOS 7.1
    35,  # Safari 7 / OS X 10.9
    85,  # Safari 8 / iOS 8.4
    87,  # Safari 8 / OS X 10.10
    114,  # Safari 9 / iOS 9
    111,  # Safari 9 / OS X 10.11
    140,  # Safari 10 / iOS 10
    138,  # Safari 10 / OS X 10.12
    161,  # Safari 12.1.2 / MacOS 10.14.6 Beta
    166,  # Safari 12.1.1 / iOS 12.3.1
    112,  # Apple ATS 9 / iOS 9
    92,  # Yahoo Slurp Jan 2015
    93,  # YandexBot Jan 2015
]


class ClientStatus(tls.ExtendedEnum):
    """Enum for client simulation states"""

    OK = enum.auto()
    NOK = enum.auto()
    SKIPPED = enum.auto()


class SPClient(SPObject):
    """Data class for client simulation profile"""

    pass


class SPClientSchema(ProfileSchema):
    """Schema for client simulation profile"""

    __profile_class__ = SPClient
    name = fields.String()
    status = FieldsEnumString(enum_class=ClientStatus)
    version = fields.Nested(SPVersionEnumSchema)
    cipher_suite = fields.Nested(SPCipherSuiteSchema)
    cert_type = FieldsEnumString(enum_class=tls.SignatureAlgorithm)
    cert_pub_key_size = fields.Integer()
    cert_sig_algo = FieldsEnumString(enum_class=tls.SignatureScheme)
    key_ex_type = FieldsEnumString(enum_class=tls.KeyExchangeType)
    key_ex_curve = fields.Nested(SPSupportedGroupEnumSchema)
    key_ex_size = fields.Integer()
    key_ex_sig_algo = FieldsEnumString(enum_class=tls.SignatureScheme)


@ServerProfileSchema.augment
class SPClientSimulation(ProfileSchema):
    """Schema for client simulation"""

    client_simulation = fields.List(fields.Nested(SPClientSchema))


@TextProfileWorker.augment_output
def print_client_simul(text_worker):
    """Extend the output of the client worker

    Arguments:
        text_worker (`tlsmate.workers.text_server_profile.TextProfileWorker`): the
            worker instance for the text profile
    """

    if not hasattr(text_worker.server_profile, "client_simulation"):
        return

    print(Style.HEADLINE.decorate("Handshake simulation"))
    print()
    table = utils.Table(indent=2, sep="  ")
    for client in text_worker.server_profile.client_simulation:
        if client.status is ClientStatus.OK:
            if hasattr(client, "cert_type"):
                if client.cert_type in [
                    tls.SignatureAlgorithm.RSA,
                    tls.SignatureAlgorithm.DSA,
                ]:
                    style = text_worker.style_for_rsa_dh_key_size(
                        client.cert_pub_key_size
                    )

                else:
                    style = text_worker.style_for_ec_key_size(client.cert_pub_key_size)

                cert_type = f"{client.cert_type.name} ({client.cert_pub_key_size} bits)"
                cert_type = style.decorate(cert_type, with_orig_len=True)

            else:
                cert_type = ""

            key_ex = ""
            if client.key_ex_type is tls.KeyExchangeType.ECDH:
                key_ex = f"{client.key_ex_type.name} ({client.key_ex_curve.name})"
                key_ex = get_style_applied(
                    key_ex,
                    text_worker._style,
                    "supported_groups",
                    "groups",
                    client.key_ex_curve.name,
                    with_orig_len=True,
                )

            elif client.key_ex_type is tls.KeyExchangeType.DH:
                key_ex = f"{client.key_ex_type.name} ({client.key_ex_size} bits)"
                key_ex_style = text_worker.style_for_rsa_dh_key_size(client.key_ex_size)
                key_ex = key_ex_style.decorate(key_ex, with_orig_len=True)

            version = get_style_applied(
                client.version.name,
                text_worker._style,
                "version",
                client.version.name,
                "supported",
                "TRUE",
                "style",
                with_orig_len=True,
            )

            cs = client.cipher_suite.name
            table.row(
                Style.GOOD.decorate(client.name, with_orig_len=True),
                version,
                cert_type,
                key_ex,
                text_worker.style_for_cipher_suite(client.cipher_suite).decorate(
                    cs, with_orig_len=True
                ),
            )

        elif client.status is ClientStatus.NOK:
            txt = "handshake simulation failed"
            table.row(
                (Style.BAD.decorate(client.name), len(client.name)),
                (Style.BAD.decorate(txt), 0),
            )

        elif client.status is ClientStatus.SKIPPED:
            table.row(
                (Style.BAD.decorate(client.name), len(client.name)),
                (
                    Style.BAD.decorate(
                        "handshake simulation skipped, no common TLS protocol "
                        "version found"
                    ),
                    0,
                ),
            )

    table.dump()
    print()


class ClientSimulWorker(Worker):
    """Worker for the client simulation"""

    name = "client-simul"
    descr = "simulate clients"
    prio = 100

    def _read_client_file(self):
        self._clients = utils.deserialize_data(self.config.get("client_profiles"))

    @staticmethod
    def _get_versions(data):
        versions = [
            vers
            for vers in tls.Version.all()
            if data["lowestProtocol"] <= vers <= data["highestProtocol"]
        ]
        if any([(cs & 0x1300) == 0x1300 for cs in data["suiteIds"]]):
            if tls.Version.TLS13 not in versions:
                versions.append(tls.Version.TLS13)

        return versions

    @staticmethod
    def _get_compression(data):
        compressions = [tls.CompressionMethod.NULL]
        if data["supportsCompression"]:
            compressions.append(tls.CompressionMethod.DEFLATE)

        return compressions

    @staticmethod
    def _get_cipher_suites(data):
        cipher_suites = []
        for cs_int in data["suiteIds"]:
            if cs_int <= 0xFFFF:
                cs = tls.CipherSuite.val2enum(cs_int)
                if cs is not None:
                    cipher_suites.append(cs)

        return cipher_suites

    @staticmethod
    def _get_supported_groups(data):
        groups = None
        if data["ellipticCurves"]:
            groups = []
            for group in data["ellipticCurves"]:
                try:
                    groups.append(tls.SupportedGroups(group))

                except ValueError:
                    groups.append(group)

        return groups

    @staticmethod
    def _get_sig_algos(data):
        sig_algos = None
        if data["signatureAlgorithms"]:
            sig_algos = []
            for sig in data["signatureAlgorithms"]:
                try:
                    sig_algos.append(tls.SignatureScheme(sig))

                except ValueError:
                    sig_algos.append(sig)

        return sig_algos

    @staticmethod
    def _get_client_name(data):
        client = data["name"] + " " + data["version"]
        if "platform" in data:
            client += " / " + data["platform"]

        return client

    @staticmethod
    def _get_cert_info(cert):
        pub_key = cert.parsed.public_key()
        if isinstance(pub_key, rsa.RSAPublicKey):
            key_type = tls.SignatureAlgorithm.RSA
            key_size = pub_key.key_size

        elif isinstance(pub_key, dsa.DSAPublicKey):
            key_type = tls.SignatureAlgorithm.DSA
            key_size = pub_key.key_size

        elif isinstance(pub_key, ec.EllipticCurvePublicKey):
            key_type = tls.SignatureAlgorithm.ECDSA
            key_size = pub_key.key_size

        elif isinstance(pub_key, ed25519.Ed25519PublicKey):
            key_type = tls.SignatureAlgorithm.ED25519
            key_size = 256

        elif isinstance(pub_key, ed448.Ed448PublicKey):
            key_type = tls.SignatureAlgorithm.ED448
            key_size = 456

        return key_type, key_size

    def _create_client(self, data, conn):
        name = self._get_client_name(data)
        if not conn.handshake_completed:
            return SPClient(name=name, status=ClientStatus.NOK)

        cs_details = utils.get_cipher_suite_details(conn.cipher_suite)
        client = SPClient(name=name, status=ClientStatus.OK)
        client.version = conn.version
        client.cipher_suite = conn.cipher_suite
        cert_msg = conn.msg.server_certificate
        if cert_msg:
            cert = cert_msg.chain.certificates[0]
            client.cert_type, client.cert_pub_key_size = self._get_cert_info(cert)
            client.cert_sig_algo = cert.signature_algorithm

        if conn.version is tls.Version.TLS13:
            key_share_ext = conn.msg.server_hello.get_extension(tls.Extension.KEY_SHARE)
            key_share = key_share_ext.key_shares[0]
            client.key_ex_curve = key_share.group
            if client.key_ex_curve in [
                tls.SupportedGroups.FFDHE2048,
                tls.SupportedGroups.FFDHE3072,
                tls.SupportedGroups.FFDHE4096,
                tls.SupportedGroups.FFDHE6144,
                tls.SupportedGroups.FFDHE8192,
            ]:
                client.key_ex_type = tls.KeyExchangeType.DH

            else:
                client.key_ex_type = tls.KeyExchangeType.ECDH

        elif conn.msg.server_key_exchange:
            ske = conn.msg.server_key_exchange
            if ske.ec:
                client.key_ex_curve = ske.ec.named_curve
                client.key_ex_type = tls.KeyExchangeType.ECDH
                sig_algo = (
                    ske.ec.sig_scheme or cs_details.key_algo_struct.default_sig_scheme
                )
                if sig_algo:
                    client.key_ex_sig_algo = sig_algo

            elif ske.dh:
                client.key_ex_type = tls.KeyExchangeType.DH
                sig_algo = (
                    ske.dh.sig_scheme or cs_details.key_algo_struct.default_sig_scheme
                )
                if sig_algo:
                    client.key_ex_sig_algo = sig_algo
                    client.key_ex_size = len(ske.dh.p_val) * 8

        else:
            client.key_ex_type = tls.KeyExchangeType.RSA

        return client

    def _set_client_prof(self, data):
        self.client.init_profile()
        self.client.alert_on_invalid_cert = False
        self.client.session_state_id = None
        self.client.session_state_ticket = None
        versions = self._get_versions(data)
        if not self._versions.intersection(set(versions)):
            return False

        self.client.profile.versions = versions
        self.client.profile.compression_methods = self._get_compression(data)
        self.client.profile.cipher_suites = self._get_cipher_suites(data)
        if self.client.profile.versions[-1] >= tls.Version.TLS10:
            # TLS extensions supported
            self.client.profile.support_secure_renegotiation = data["supportsRi"]
            self.client.profile.support_sni = data["supportsSni"]
            groups = self._get_supported_groups(data)
            if groups:
                self.client.profile.supported_groups = groups
                if self.client.profile.versions[-1] is tls.Version.TLS13:
                    self.client.profile.key_shares = tls.SupportedGroups.all_tls13()

            self.client.profile.signature_algorithms = self._get_sig_algos(data)
            self.client.profile.support_status_request = data["supportsStapling"]
            self.client.profile.support_session_ticket = data["supportsTickets"]

        return True

    def run(self):
        """The entry point for the worker"""

        self._read_client_file()
        if not hasattr(self.server_profile, "client_simulation"):
            self.server_profile.client_simulation = []

        prof_versions = self.server_profile.get_versions()
        if not prof_versions:
            prof_versions = tls.Version.all()

        self._versions = set(prof_versions)
        for client_prof in self._clients:
            if client_prof["id"] not in _client_white_list:
                continue

            if self._set_client_prof(client_prof):
                with self.client.create_connection() as conn:
                    conn.handshake()

                client = self._create_client(client_prof, conn)

            else:
                client = SPClient(
                    name=self._get_client_name(client_prof), status=ClientStatus.SKIPPED
                )

            self.server_profile.client_simulation.append(client)


class ArgClientSimul(Plugin):
    """Extend the scan command by the --client-simul argument"""

    config = ConfigItem("client_simul", type=bool, default=None)
    cli_args = Args(
        "--client-simul",
        help=("perform a simulation for various clients"),
        action=utils.BooleanOptionalAction,
    )
    workers = [ClientSimulWorker]


class ArgClientProfiles(Plugin):
    """Plugin for the client profile argument"""

    config = ConfigItem("client_profiles", type=str, default=_CLIENT_PROFILES)
    cli_args = Args(
        "--client-profiles",
        default=None,
        help="JSON file containing client profile definitions",
    )


@SubcommandScan.extend
class GroupClientSimul(Plugin):
    """Extend the scan subcommand"""

    group = Args(title="Options for client simulation")
    plugins = [ArgClientSimul, ArgClientProfiles]


@BaseCommand.extend
class SubcommandClientSimul(Plugin):
    """Define new subcommand for the client simulation"""

    subcommand = Args("client-simul", help="simulates different client behaviors")
    plugins = [
        GroupBasicScan,
        GroupX509,
        GroupServerProfile,
        ArgClientProfiles,
    ]
    workers = [ScanStart, ScanEnd, ClientSimulWorker]
