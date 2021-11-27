from it.core.base import BaseTool


class Prokka(BaseTool):
    image = "staphb/prokka:latest"
    prefix_cmd = "prokka"
