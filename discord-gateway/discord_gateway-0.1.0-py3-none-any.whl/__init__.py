"""Sans-I/O implementation of the Discord gateway.

Sans-I/O means that this implements no I/O (network) and operates purely on the
bytes given using `wsproto`.

It means that this implementation can be reused for libraries implemented in a
threading fashion or asyncio/trio/curio.
"""

from .conn import *
from .errors import *
from .opcode import *
