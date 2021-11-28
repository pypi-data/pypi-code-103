"""X24D."""
from .const import EXT_X24D, TYPE_IO
from .extension import Extension
from .ipx800 import IPX800


class X24D(Extension):
    def __init__(self, ipx: IPX800, ext_number: int, input_number: int):
        super().__init__(ipx, EXT_X24D, ext_number, input_number)
        self.io_state_id = self._config["ioInput_id"][input_number - 1]

    @property
    async def status(self) -> bool:
        """Return the current X24D digital input status."""
        return await self._ipx.get_io(self.io_state_id)
