
from decimal import Decimal
from enum import Enum

class Variable(Enum):
    UNDEFINED = '<undefined>'
    MISSING = '<missing>'
    
    def __str__(self):
        return self.value
    
    def __repr__(self):
        return self.value


def is_defined(value):
    return False if value == Variable.UNDEFINED else True

def is_missing(value):
    return True if value == Variable.MISSING else False

def exist(value):
    return False if value in ['', None, Variable.MISSING, Variable.UNDEFINED] else True

def is_private(string: str) -> bool:
    return True if string.startswith("_") and not string.endswith("_") else False

def unprivate(string: str) -> str:
    return string[ 1: ] if is_private(string) else string

def json_encode(value):
    if value == None:
        return ''
    elif isinstance(value, (str, int, float)):
        return value
    elif isinstance(value, bool):
        return 'true' if value == True else 'false'
    elif isinstance(value, Decimal):
        return str(value)
    elif isinstance(value, list):
        return [json_encode(i) for i in value ]
    elif isinstance(value, dict):
        return {unprivate(k): json_encode(v) for k, v in value.items()}
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, tuple):
        try:
            return {k: json_encode(v) for (k,v) in value._asdict().items()}
        except:
            return [json_encode(v) for v in value]
    else:
        try:
            return str(value)
        except BaseException as e:
            print(e)
        finally:
            return value
            
