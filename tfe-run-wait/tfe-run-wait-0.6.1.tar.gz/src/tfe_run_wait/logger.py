import os
import logging

logging.basicConfig(format="%(levelname)s: %(message)s")
log = logging.getLogger("tfe-run-wait")
log.setLevel(os.getenv("LOG_LEVEL", "INFO"))
