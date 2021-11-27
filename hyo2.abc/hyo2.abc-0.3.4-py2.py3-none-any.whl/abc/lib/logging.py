import logging
from typing import Optional

# logger = logging.getLogger(__name__)


def set_logging(ns_list: Optional[list] = None,
                default_logging: int = logging.WARNING,
                hyo2_logging: int = logging.INFO,
                lib_logging: int = logging.DEBUG):

    logging.basicConfig(
        level=default_logging,
        format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s"
    )
    logging.getLogger("hyo2").setLevel(hyo2_logging)

    main_ns = "__main__"
    if ns_list is None:
        ns_list = [main_ns, ]
    if main_ns not in ns_list:
        ns_list.append(main_ns)

    for ns in ns_list:
        # logger.info(ns)
        logging.getLogger(ns).setLevel(lib_logging)
