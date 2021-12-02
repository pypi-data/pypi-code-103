"""Updates configured AWS credentials with MFA."""

__version__ = "0.1.2"

import argparse
import configparser
import functools
import logging
import pathlib
import sys

import boto3

DEFAULT_DURATION_SECONDS = 900
DEFAULT_ROLE_SESSION_NAME = "local"
DEFAULT_CONFIG_PATH = "~/.aws/config"
DEFAULT_CREDENTIALS_PATH = "~/.aws/credentials"
DEFAULT_CREDENTIALS_ENCODING = "utf-8"

AWS_ACCESS_KEY_ID_KEY = "aws_access_key_id"
AWS_SECRET_ACCESS_KEY_KEY = "aws_secret_access_key"
AWS_SESSION_TOKEN_KEY = "aws_session_token"

ROLE_ARN_KEY = "role_arn"
SOURCE_PROFILE_KEY = "source_profile"


def set_logger(level: int = None) -> None:
    """Set named logger.

    :param level: Log level.
    """
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter("%(asctime)s %(levelname)8s %(message)s")
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    if level is not None:
        logger.setLevel(level)
        stream.setLevel(level)
    logger.addHandler(stream)


def file_type(file_path: str) -> pathlib.Path:
    """Resolve a file path to a file.

    :param file_path: Path to file.
    :return: Path object.
    """
    file = pathlib.Path(file_path).expanduser().resolve()
    if not file.is_file():
        raise argparse.ArgumentTypeError("{} is not a file.".format(file.as_uri()))
    return file


def uri(path: str) -> str:
    """Convert a path to a URI.

    :param path: Raw path.
    :return: Path URI.
    """
    return pathlib.Path(path).expanduser().resolve().as_uri()


def parse_args() -> argparse.Namespace:
    """Parse arguments.

    :return: Argument Parser Namespace.
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("--version", action="version", version=f"{__version__}")

    parser.add_argument(
        "role_profile",
        help="The complete role profile section name, including the profile prefix, "
        "from the AWS configuration file to authenticate with MFA, e.g. "
        f'"profile my-role". This section must have the "{ROLE_ARN_KEY}" '
        f'and "{SOURCE_PROFILE_KEY}" keys.',
    )
    parser.add_argument(
        "mfa_arn", help='MFA ARN, e.g. "arn:aws:iam::123456789012:mfa/john.doe"'
    )

    parser.add_argument(
        "--mfa-token-code",
        default=None,
        help="MFA token code from the authenticator. "
        "Defaults to user input if not provided.",
        dest="mfa_token_code",
    )
    parser.add_argument(
        "--duration-seconds",
        default=DEFAULT_DURATION_SECONDS,
        help="Duration in seconds before the new credentials expire. "
        f"Defaults to {DEFAULT_DURATION_SECONDS} seconds.",
        type=int,
        dest="duration_seconds",
    )
    parser.add_argument(
        "--role-session-name",
        default=DEFAULT_ROLE_SESSION_NAME,
        help="Role session name as required by your organization. "
        f'Defaults to "{DEFAULT_ROLE_SESSION_NAME}".',
        dest="role_session_name",
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Only show the access key ID, secret access key, "
        "and the session token of the assumed role without "
        "saving it to the AWS credentials file.",
        dest="no_write",
    )
    parser.add_argument(
        "--config-path",
        default=DEFAULT_CONFIG_PATH,
        help="Path to the AWS configuration file. Defaults to "
        f"{uri(DEFAULT_CONFIG_PATH)}.",
        type=functools.partial(file_type),
        dest="config_path",
    )
    parser.add_argument(
        "--credentials-path",
        default=DEFAULT_CREDENTIALS_PATH,
        help="Path to the AWS credentials file. Defaults to "
        f"{uri(DEFAULT_CREDENTIALS_PATH)}.",
        type=functools.partial(file_type),
        dest="credentials_path",
    )
    parser.add_argument(
        "--credentials-encoding",
        default=DEFAULT_CREDENTIALS_ENCODING,
        help="Encoding of the AWS credentials file. Defaults to {}.".format(
            DEFAULT_CREDENTIALS_ENCODING.upper()
        ),
        dest="credentials_encoding",
    )
    return parser.parse_args()


def section_has_keys(section: configparser.SectionProxy, *keys: str) -> bool:
    """Verify that an INI section has the keys.

    :param section: INI section.
    :param keys: Expected keys from the INI section.
    :return: Whether the INI section has the expected keys.
    """
    return len(set(keys).intersection(set(section.keys()))) == len(keys)


def is_role_profile(section: configparser.SectionProxy):
    """Verify that an INI section has the keys expected from an AWS role profile.

    :param section: INI section.
    :return: Whether the INI section has the expected role profile keys.
    """
    return section_has_keys(section, ROLE_ARN_KEY, SOURCE_PROFILE_KEY)


def assume_role(
    role_arn: str,
    role_session_name: str,
    duration_seconds: int,
    serial_number: str,
    token_code: str,
) -> dict:
    """Assume a role using STS.

    :param role_arn: Role ARN of the profile.
    :param role_session_name: Role session name.
    :param duration_seconds: Duration in seconds.
    :param serial_number: MFA ARN.
    :param token_code: MFA token code value.
    :return: STS Assume Role response.
    """
    client = boto3.client("sts")
    return client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name,
        DurationSeconds=duration_seconds,
        SerialNumber=serial_number,
        TokenCode=token_code,
    )


def is_source_profile(section: configparser.SectionProxy) -> bool:
    """Verify that an INI section has the keys expected from an AWS source profile.

    :param section: INI section.
    :return: Whether the INI section has the expected source profile keys.
    """
    return section_has_keys(
        section, AWS_ACCESS_KEY_ID_KEY, AWS_SECRET_ACCESS_KEY_KEY, AWS_SESSION_TOKEN_KEY
    )


def update_credentials(
    source_profile_section: configparser.SectionProxy, sts_response
) -> None:
    """Mutate the source profile values.

    :param source_profile_section: Source profile section.
    :param sts_response: STS Assume Role response.
    """
    credentials = sts_response["Credentials"]
    source_profile_section[AWS_ACCESS_KEY_ID_KEY] = credentials["AccessKeyId"]
    source_profile_section[AWS_SECRET_ACCESS_KEY_KEY] = credentials["SecretAccessKey"]
    source_profile_section[AWS_SESSION_TOKEN_KEY] = credentials["SessionToken"]

    logger = logging.getLogger(__name__)
    logger.info("Credentials will expire on %s.", credentials["Expiration"])


def save_credentials(path: pathlib.Path, encoding: str, credentials) -> None:
    """Update the credential file to reflect the new secrets.

    :param path: Path of the credentials file.
    :param encoding: Encoding of the credentials file.
    :param credentials: The entire parsed content from the credentials file.
    """
    with open(path.as_posix(), "w", encoding=encoding) as file:
        credentials.write(file)


def log_secrets(response: dict) -> None:
    """Log secrets to user.

    :param response: STS Assume Role response.
    """
    logger = logging.getLogger(__name__)

    credentials = response["Credentials"]
    logger.info("%s: %s", AWS_ACCESS_KEY_ID_KEY.upper(), credentials["AccessKeyId"])
    logger.info(
        "%s: %s", AWS_SECRET_ACCESS_KEY_KEY.upper(), credentials["SecretAccessKey"]
    )
    logger.info("%s: %s", AWS_SESSION_TOKEN_KEY.upper(), credentials["SessionToken"])


def main() -> None:
    """Run this script."""
    set_logger(logging.INFO)
    logger = logging.getLogger(__name__)

    args = parse_args()

    if args.mfa_token_code is None:
        mfa_token_code = input("Input MFA Token: ")
    else:
        mfa_token_code = args.mfa_token_code

    logger.info("Role Profile: %s", args.role_profile)
    logger.info("MFA ARN: %s", args.mfa_arn)
    logger.info("MFA Token: %s", mfa_token_code)
    logger.info("Duration (Seconds): %s", args.duration_seconds)
    logger.info("Role Session Name: %s", args.role_session_name)
    logger.info("Print Only (No Write): %s", args.no_write)
    logger.info("AWS Configuration Path URI: %s", args.config_path.as_uri())
    logger.info("AWS Credentials Path URI: %s", args.credentials_path.as_uri())
    logger.info("AWS Credentials Encoding: %s", args.credentials_encoding)

    config = configparser.ConfigParser()
    config.read(args.config_path.as_posix())

    if args.role_profile not in config.sections():
        logger.error("Failed to find profile.")
        sys.exit(1)

    role_profile = config[args.role_profile]
    if is_role_profile(role_profile) is False:
        logger.error("Role profile does not have the expected keys.")
        sys.exit(1)

    response = assume_role(
        role_profile[ROLE_ARN_KEY],
        args.role_session_name,
        args.duration_seconds,
        args.mfa_arn,
        mfa_token_code,
    )
    if args.no_write is True:
        log_secrets(response)
        sys.exit(1)

    credentials = configparser.ConfigParser()
    credentials.read(args.credentials_path.as_posix())

    if role_profile[SOURCE_PROFILE_KEY] not in credentials.sections():
        logger.error("Failed to find source profile.")
        sys.exit(1)

    source_profile = credentials[role_profile[SOURCE_PROFILE_KEY]]
    if is_source_profile(source_profile) is False:
        logger.error("Source profile does not have the expected keys.")
        sys.exit(1)

    update_credentials(source_profile, response)
    save_credentials(args.credentials_path, args.credentials_encoding, credentials)

    logger.info("Updated %s.", args.credentials_path.as_uri())
