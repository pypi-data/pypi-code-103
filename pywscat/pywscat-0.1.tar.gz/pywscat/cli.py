#!/usr/bin/env python3

import argparse
from . import wsclient, wsserver

def main():
    # Create an ArgumentParser object
    # args:
    #   -l --listen: boolean should we listen
    #   uri: string URI to connect or listen to

    parser = argparse.ArgumentParser(description='Socket Server Example')
    #parser.add_argument('--listen', '-l', action='store_true', help='should we listen on this uri')
    parser.add_argument('uri', help='URI to connect or listen to')
    args = parser.parse_args()

    """
    if args.listen:
        wsserver.main()
    else:
        wsclient.main()
    """
    wsclient.main()


if __name__ == "__main__":
    main()