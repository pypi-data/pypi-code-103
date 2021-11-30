#!/usr/bin/env python3


from libervia.server.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)


name = "merge-requests_new"
access = C.PAGES_ACCESS_PUBLIC
template = "merge-request/create.html"
