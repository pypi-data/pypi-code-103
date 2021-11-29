import os

def env(a: str) -> str:
    ret = os.getenv(a)
    if ret is None:
        raise Exception("Failed to get env %s, Please setup it or add it to your .env file" % a)
    return ret
