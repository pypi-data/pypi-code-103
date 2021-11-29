import argparse

from aos_starter.actions import do_oem_user


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Startup Aos User",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-oem", "--oem", action='store_true', help="OEM USER")

    parser.add_argument("-d", "--domain", dest="register_domain", default='aoscloud.io',
                        help="Aos Cloud domain to register user keys")

    parser.add_argument(
        "-t", "--token", dest="token",
        help="Authorization token. If token is given you will not be prompted for user name and password")

    return parser.parse_args()


def main():
    args = _parse_args()
    print(args)
    if args.oem:
        do_oem_user(args.register_domain, args.token)


if __name__ == '__main__':
    main()
