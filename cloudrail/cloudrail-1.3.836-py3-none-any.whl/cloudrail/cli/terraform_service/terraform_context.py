from dataclasses import dataclass


@dataclass
class TerraformRawData:
    file_name: str
    start_line: int
    end_line: int
