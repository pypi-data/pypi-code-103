from typing import AsyncGenerator

from datek_async_fsm.fsm import BaseFSM

from datek_jaipur.application.state_machine.scope import Scope


class FSM(BaseFSM):
    scope: Scope

    async def _input_generator(self) -> AsyncGenerator[dict, None]:
        while True:
            yield {"scope": self.scope}
