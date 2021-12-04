from enum import Enum

class Datatype(Enum):
    INT = "INT"
    TINYINT = "TINYINT"
    FLOAT = "FLOAT"
    CHAR = "CHAR"

    def VARCHAR(length):
        return f"VARCHAR({length})"
