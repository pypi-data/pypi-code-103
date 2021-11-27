from asking.protocols import StateProtocol
from asking.types import StageKey, StageType


class Stage:
    def __init__(self, stage: StageType, state: StateProtocol) -> None:
        self._stage = stage
        self._state = state

    def perform(self) -> StageKey:
        next = self._state.perform_actions(self._stage)
        self._state.logger.debug("next stage: %s", next)
        return next
