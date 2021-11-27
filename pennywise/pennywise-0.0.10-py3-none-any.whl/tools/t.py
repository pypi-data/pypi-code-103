from it.core.base import BaseTool


class Trimmomatic(BaseTool):
    image = "staphb/trimmomatic:latest"
    prefix_cmd = "trimmomatic"
