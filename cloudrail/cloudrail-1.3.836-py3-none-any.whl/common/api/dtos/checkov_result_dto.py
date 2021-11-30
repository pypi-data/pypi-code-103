from dataclasses import dataclass


@dataclass
class CheckovResultDTO:
    check_id: str
    file_path: str
    resource: str
    start_line: int
    end_line: int

    @staticmethod
    def from_dict(dic: dict):
        return CheckovResultDTO(dic['check_id'], dic['file_path'], dic['resource'], dic['start_line'], dic['end_line'])
