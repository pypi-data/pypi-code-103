from logging import getLogger
from typing import Optional

from asking.prompts.prompt import PromptBuilder


class RecallPromptBuilder(PromptBuilder):
    """
    Creates a prompt like "(previous value)" if a key exists and recall is
    enabled.
    """

    @property
    def prompt(self) -> Optional[str]:
        logger = getLogger("asking")

        if not self._ask.recall:
            logger.debug("Won't recall value: recall is disabled")
            return None

        if not self._ask.key:
            logger.debug("Won't recall value: no key")
            return None

        value = self._ask.state.get_response(self._ask.key) or ""
        logger.debug("Recall value: %s", value)
        return "" if not value else f"default: {value}"
