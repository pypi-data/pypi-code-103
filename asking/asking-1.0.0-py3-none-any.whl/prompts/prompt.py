from abc import ABC, abstractproperty
from logging import getLogger
from typing import List, Optional

from asking.protocols import AskActionProtocol


class PromptBuilder(ABC):
    """
    Base prompt builder.
    """

    def __init__(self, ask: AskActionProtocol) -> None:
        self._ask = ask

    @abstractproperty
    def prompt(self) -> Optional[str]:
        """
        Prompt to show to the user.
        """


class MultipleChoicePromptBuilder(PromptBuilder):
    """
    Creates a prompt like "(y/N)" if all the options are primitive strings.
    """

    @property
    def prompt(self) -> Optional[str]:
        logger = getLogger("asking")

        options: List[str] = []
        previous_valid: Optional[str] = None

        for branch in self._ask.branches:
            next_is_default = False
            for response in branch.response:
                if response == "":
                    if previous_valid is not None:
                        index = options.index(previous_valid)
                        options[index] = options[index].upper()
                    else:
                        next_is_default = True
                    continue

                if str.isupper(response) or branch.is_regex(response):
                    logger.debug(
                        "MultipleChoicePromptBuilder cannot build with: %s", response
                    )
                    return None

                if next_is_default:
                    next_is_default = False
                    options.append(response.upper())
                else:
                    previous_valid = response
                    options.append(response)

        logger.debug("options: %s", options)

        return "/".join(options)
