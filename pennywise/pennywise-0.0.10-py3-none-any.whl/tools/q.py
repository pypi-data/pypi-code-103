from it.core.base import BaseTool


class Quast(BaseTool):
    image = "staphb/quast:latest"
    prefix_cmd = "quast.py"
