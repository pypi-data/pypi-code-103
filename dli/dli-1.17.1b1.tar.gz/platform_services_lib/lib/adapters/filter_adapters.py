from typing import List, Tuple, Dict


class DLCFilterAdapter(List[Tuple[str, str, str]]):
    def to_params(self) -> Dict[str, str]:
        result = {}

        for idx, param in enumerate(self):
            field, operator, value = param
            result.update({
                f'filter[{idx}][field]': field,
                f'filter[{idx}][operator]': operator,
                f'filter[{idx}][value]': value,
            })

        return result
