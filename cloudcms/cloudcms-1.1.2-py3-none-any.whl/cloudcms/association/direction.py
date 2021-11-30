from enum import Enum

class Direction(Enum):
    OUTGOING='OUTGOING',
    INCOMING='INCOMING',
    MUTUAL='MUTUAL',
    ANY='ANY'

    def __str__(self):
        return str(self.name)