from argparse import ArgumentParser

from monutils.db import Mode

MODES = ['NONE' if m == Mode.NONE else m.value.upper() for m in Mode]


class CopyArgParser(object):
    @property
    def from_host(self) -> str:
        """
        :return: The source database host. By default, localhost.
        """
        return self._args.from_host

    @property
    def to_host(self) -> str:
        """
        :return: The target database host. By default, localhost.
        """
        return self._args.to_host

    @property
    def from_port(self) -> int:
        """
        :return: The source database port. By default, 27017.
        """
        return self._args.from_port

    @property
    def to_port(self) -> int:
        """
        :return: The target database port. By default, 27017.
        """
        return self._args.to_port

    @property
    def from_replicaset(self) -> str:
        """
        :return: The source replicaset.
        """
        return self._args.from_replicaset

    @property
    def to_replicaset(self) -> str:
        """
        :return: The target replicaset.
        """
        return self._args.to_replicaset

    @property
    def from_user(self) -> str:
        """
        :return: The username for the source database. By default, it is not used.
        """
        return self._args.from_user

    @property
    def to_user(self) -> str:
        """
        :return: The username for the target database. By default, it is not used.
        """
        return self._args.to_user

    @property
    def from_password(self) -> str:
        """
        :return: The password for the source database. By default, it is not used.
        """
        return self._args.from_password

    @property
    def to_password(self) -> str:
        """
        :return: The password for the source database. By default, it is not used.
        """
        return self._args.to_password

    @property
    def from_database(self) -> str:
        """
        :return: The source database name.
        """
        return self._args.from_database

    @property
    def to_database(self) -> str:
        """
        :return: The target database name.
        """
        return self._args.to_database

    @property
    def from_collection(self) -> str:
        """
        :return: The source database collection.
        """
        return self._args.from_collection

    @property
    def to_collection(self) -> str:
        """
        :return: The target database collection.
        """
        return self._args.to_collection

    @property
    def from_mode(self) -> Mode:
        """
        :return: The authentication model for the source MongoDB database. By default, try all.
        """
        return Mode.NONE if self._args.from_mode == 'NONE' else Mode[self._args.from_mode]

    @property
    def to_mode(self) -> Mode:
        """
        :return: The authentication model for the target MongoDB database. By default, it try all.
        """
        return Mode.NONE if self._args.to_mode == 'NONE' else Mode[self._args.to_mode]

    @property
    def from_cert(self) -> str:
        """
        :return: The path to the certificate key file for the connection with the source database.
           By default, it is not used.
        """
        return self._args.from_cert

    @property
    def to_cert(self) -> str:
        """
        :return: The path to the certificate key file for the connection with the target database.
           By default, it is not used.
        """
        return self._args.to_cert

    @property
    def from_ca(self) -> str:
        """
        :return: The path to the CA file for the connection with the source database. By default, it is not used.
        """
        return self._args.from_ca

    @property
    def to_ca(self) -> str:
        """
        :return: The path to the CA file for the connection with the target database. By default, it is not used.
        """
        return self._args.to_ca

    @property
    def from_session_token(self) -> str:
        """
        :return: The session token to use for the connection with the source database. By default, it is not used.
        """
        return self._args.from_session

    @property
    def to_session_token(self) -> str:
        """
        :return: The session token to use for the connection with the source database. By default, it is not used.
        """
        return self._args.to_session

    @property
    def ignore(self) -> bool:
        """
        :return: If activate, ignore copy errors.
        """
        return self._args.ignore

    def __init__(self):
        """ Constructor. """
        parser = ArgumentParser(description='Copy a collection from a MongoDB database to another.')
        self.set_arguments(parser)
        self._args = parser.parse_args()

    @staticmethod
    def set_arguments(parser: ArgumentParser) -> None:
        """ Set the arguments for this argument parser.

        :param parser: The Argument parser.
        """
        parser.add_argument('-fh', '--from_host', type=str, metavar='HOST', default='localhost',
                            help='The source database host. By default, localhost.')
        parser.add_argument('-th', '--to_host', type=str, metavar='HOST', default='localhost',
                            help='The target database host. By default, localhost.')
        parser.add_argument('-fp', '--from_port', type=int, metavar='PORT', default=27017,
                            help='The source database port. By default, 27017.')
        parser.add_argument('-tp', '--to_port', type=int, metavar='PORT', default=27017,
                            help='The target database port. By default, 27017.')
        parser.add_argument('-fr', '--from_replicaset', type=str, metavar='REPLICASET', help='The source replicaset.')
        parser.add_argument('-tr', '--to_replicaset', type=str, metavar='REPLICASET', help='The target replicaset.')
        parser.add_argument('-fu', '--from_user', type=str, metavar='USER',
                            help='The username for the source database. By default, it is not used.')
        parser.add_argument('-tu', '--to_user', type=str, metavar='USER',
                            help='The username for the target database. By default, it is not used.')
        parser.add_argument('-fw', '--from_password', type=str, metavar='PASSWORD',
                            help='The password for the source database. By default, it is not used.')
        parser.add_argument('-fd', '--from_database', type=str, metavar='NAME', required=True,
                            help='The source database name.')
        parser.add_argument('-td', '--to_database', type=str, metavar='NAME', required=True,
                            help='The target database name.')
        parser.add_argument('-fc', '--from_collection', type=str, metavar='NAME', required=True,
                            help='The source database collection.')
        parser.add_argument('-tw', '--to_password', type=str, metavar='PASSWORD',
                            help='The password for the target database. By default, it is not used.')
        parser.add_argument('-tc', '--to_collection', type=str, metavar='NAME', required=True,
                            help='The target database collection.')
        parser.add_argument('-fm', '--from_mode', type=str.upper, metavar='MODE', default='AUTO', choices=MODES,
                            help='The authentication model for the source MongoDB database. By default, try all. '
                                 f'Available modes: {",".join(MODES)}')
        parser.add_argument('-tm', '--to_mode', type=str.upper, metavar='MODE', default='AUTO', choices=MODES,
                            help='The authentication model for the target MongoDB database. By default, it try all. '
                                 f'Available modes: {", ".join(MODES)}')
        parser.add_argument('from_cert', type=str, metavar='FILE', default=None,
                            help='The path to the certificate key file for the connection with the source database. '
                                 'By default, it is not used.')
        parser.add_argument('to_cert', type=str, metavar='FILE', default=None,
                            help='The path to the certificate key file for the connection with the target database. '
                                 'By default, it is not used.')
        parser.add_argument('from_ca', type=str, metavar='FILE', default=None,
                            help='The path to the CA file for the connection with the source database. '
                                 'By default, it is not used.')
        parser.add_argument('to_ca', type=str, metavar='FILE', default=None,
                            help='The path to the CA file for the connection with the target database. '
                                 'By default, it is not used.')
        parser.add_argument('-fs', '--from_session', type=str, metavar='TOKEN', default=None,
                            help='The session token to use for the connection with the source database. '
                                 'By default, it is not used.')
        parser.add_argument('-ts', '--to_session', type=str, metavar='TOKEN', default=None,
                            help='The session token to use for the connection with the target database. '
                                 'By default, it is not used.')
        parser.add_argument('-i', '--ignore', action='store_true', default=False,
                            help='If activate, ignore copy errors.')
