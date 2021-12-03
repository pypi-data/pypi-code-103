import logging
from .secrets import Secrets

logger = logging.getLogger('microgue_secrets')
logger.setLevel(logging.CRITICAL)


class SecretsWithoutLogging(Secrets):
    pass
