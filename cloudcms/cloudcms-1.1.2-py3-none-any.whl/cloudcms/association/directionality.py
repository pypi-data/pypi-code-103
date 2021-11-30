from enum import Enum

class Directionality(Enum):
    DIRECTED='DIRECTED',
    UNDIRECTED='UNDIRECTED'

    def __str__(self):
        return str(self.name)