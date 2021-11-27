from it.core.base import BaseTool


class FastANI(BaseTool):
    image = "staphb/fastani:latest"
    prefix_cmd = "fastANI"
