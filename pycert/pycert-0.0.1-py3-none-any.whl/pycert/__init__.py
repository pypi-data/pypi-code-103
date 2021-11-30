__author__ = 'Andrey Komissarov'
__date__ = '2021'

import ssl
from datetime import datetime
from typing import Union

from OpenSSL import crypto
from OpenSSL.crypto import X509
from cryptography import x509
from cryptography.hazmat._oid import ObjectIdentifier
from dateutil.parser import parse


class CertClient:
    """Tool to work with server certs"""

    def __init__(self, host: str, port: int = 443):
        """
        :param host:
        :param port:
        """

        self.host = host
        self.port = port
        self.cert = self.load_certificate()

    def get_certificate(self) -> str:
        """Retrieve the certificate from the server and return it as a PEM-encoded string"""

        return ssl.get_server_certificate((self.host, self.port))

    def load_certificate(self) -> X509:
        """Load a certificate (X509) from the string or bytes encoded.

        :return: x509
        """

        try:
            return crypto.load_certificate(crypto.FILETYPE_PEM, self.get_certificate())
        except crypto.Error as err:
            raise LookupError(f'Cannot load certificate: {err}')

    def get_all_methods(self) -> list:
        """Service method to get all available methods"""

        x509_cert = self.load_certificate()
        return [i for i in dir(x509_cert) if not i.startswith('_')]

    def get_version(self) -> str:
        """Get certificate version. i.e. v3"""
        return self.cert.to_cryptography().version.name

    def get_expiration_date(self) -> datetime:
        """Validity Not After"""

        date_str = self.cert.get_notAfter().decode()
        return parse(date_str, ignoretz=True)

    def get_start_date(self) -> datetime:
        """Validity Not Before"""

        date_str = self.cert.get_notBefore()
        return parse(date_str, ignoretz=True)

    def is_valid(self) -> bool:
        now = datetime.now()
        return self.get_start_date() < now < self.get_expiration_date()

    def get_issuer(self, human: bool = True) -> Union[crypto.X509Name, dict]:
        """Get issuer info

        :param human: Return human readable dict or X509Name class
        :return:
        """

        result = self.cert.get_issuer()
        if human:
            issuer = {
                'common_name': result.commonName,
                'organizational_name': result.organizationName,
                'organizational_unit_name': result.organizationalUnitName,
                'country_name': result.countryName,
                'email': result.emailAddress,
                'state_or_province_name': result.stateOrProvinceName,
            }

            return issuer
        return result

    def get_subject(self, human: bool = True) -> Union[crypto.X509Name, dict]:
        """Get subject info

        :param human: Return human readable dict or X509Name class
        :return:
        """

        result = self.cert.get_subject()
        if human:
            issuer = {
                'common_name': result.commonName,
                'organizational_name': result.organizationName,
                'organizational_unit_name': result.organizationalUnitName,
                'country_name': result.countryName,
                'email': result.emailAddress,
                'state_or_province_name': result.stateOrProvinceName,
            }

            return issuer
        return result

    # Issuer INFO
    def get_issuer_common_name(self):
        """Get Issuer Common Name. CN | commonName"""

        try:
            return self.get_issuer(human=False).commonName
        except AttributeError:
            ...

    def get_issuer_organization_name(self):
        """Get Issuer Organization name. O | organizationName"""

        try:
            return self.get_issuer(human=False).organizationName
        except AttributeError:
            ...

    def get_issuer_organization_unit_name(self):
        """Get Issuer Organization Unit Name. OU | organizationalUnitName"""

        try:
            return self.get_issuer(human=False).organizationalUnitName
        except AttributeError:
            ...

    def get_issuer_email(self):
        """Get Issuer Email Address. emailAddress"""

        try:
            return self.get_issuer(human=False).emailAddress
        except AttributeError:
            ...

    def get_issuer_country_name(self):
        """Get Issuer Country: C/countryName"""

        try:
            return self.get_issuer(human=False).countryName
        except AttributeError:
            ...

    def get_issuer_state_or_province_name(self):
        """Get Issuer State or province name.

        ST: stateOrProvinceName
        """

        try:
            return self.get_issuer(human=False).stateOrProvinceName
        except AttributeError:
            ...

    # Subject INFO
    def get_subject_common_name(self):
        """Get Subject Common Name. CN | commonName"""

        try:
            return self.get_subject(human=False).commonName
        except AttributeError:
            ...

    def get_subject_organization_name(self):
        """Get Subject Organization name. O | organizationName"""

        try:
            return self.get_subject(human=False).organizationName
        except AttributeError:
            ...

    def get_subject_organization_unit_name(self):
        """Get Subject Organization Unit Name. OU | organizationalUnitName"""

        try:
            return self.get_subject(human=False).organizationalUnitName
        except AttributeError:
            ...

    def get_subject_email(self):
        """Get Subject Email Address. emailAddress"""

        try:
            return self.get_subject(human=False).emailAddress
        except AttributeError:
            ...

    def get_subject_country_name(self):
        """Get Subject Country: C/countryName"""

        try:
            return self.get_subject(human=False).countryName
        except AttributeError:
            ...

    def get_subject_state_or_province_name(self):
        """Get Subject State or province name.

        ST: stateOrProvinceName
        """

        try:
            return self.get_subject(human=False).stateOrProvinceName
        except AttributeError:
            ...

    # -------------- END ---------------------

    def get_locality_name(self):
        """Get locality name.

        L: localityName
        """

        try:
            return self.get_issuer().localityName
        except AttributeError:
            ...

    def get_signature_algorithm(self):
        return self.cert.get_signature_algorithm().decode()

    def get_serial_number(self):
        return self.cert.get_serial_number()

    def get_alt_name(self) -> list:
        """Get Subject Alternative Name"""

        for ext in range(self.cert.get_extension_count()):
            ext_info = self.cert.get_extension(ext)
            if ext_info.get_short_name().decode() == 'subjectAltName':
                # return [dns[4:] for dns in ext_info.__str__().split(', ') if dns.startswith('DNS:')]
                return [dns for dns in ext_info.__str__().split(', ')]
        else:
            ...

    # Extensions
    def get_extensions(self) -> Union[x509.extensions.Extensions, None]:
        """Get all available extensions"""
        try:
            return self.load_certificate().to_cryptography().extensions
        except x509.ExtensionNotFound:
            return None

    def get_extension_for_oid(self, oid: str):
        """Get extension by oid.

        https://oidref.com/2.5.4

        :param oid: i.e, "2.5.4.3" for Common name
        :return:
        """

        obj_oid = ObjectIdentifier(oid)
        return self.cert.to_cryptography().extensions.get_extension_for_oid(obj_oid)

    def get_all_info(self) -> dict:
        """Get all consolidated info"""

        data = {
            'version': self.get_version(),
            'valid_from': self.get_start_date(),
            'valid_to': self.get_expiration_date(),
            'is_valid': self.is_valid(),
            'issuer': self.get_issuer(human=True),
            'subject': self.get_subject(human=True),
            'signature_algorithm': self.get_signature_algorithm(),
            'serial_number': self.get_serial_number(),
            'alternative_name': self.get_alt_name(),
        }

        return data
