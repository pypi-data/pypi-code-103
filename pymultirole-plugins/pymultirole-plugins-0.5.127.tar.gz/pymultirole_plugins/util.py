from typing import List


def comma_separated_to_list(commasep: str, sep: str = ',') -> List[str]:
    commasep_aslist: List[str] = []
    if commasep:
        commasep_aslist = [x.strip() for x in commasep.split(sep)]
    return commasep_aslist
