import re
from typing import List, Optional, Union
from collections import Counter

from ._var import AlleleType
from ._var import NA_CHARS


def isNA(allele: str) -> bool:
    if re.search(r"[\.-]+", allele) or allele.lower() in NA_CHARS:
        return True
    return False


def isSignal(value: str) -> bool:
    if re.match(r"^[ATGC]{2,}$|[ATGC01]+/[ATGC01]+", value):
        return True
    return False


def naAlleleTransform(allele: str) -> str:
    if isNA(allele):
        return AlleleType.NA
    else:
        return allele


def uniAllele(alleles: List[str], keep_na: bool) -> Optional[str]:
    if alleles[0] == AlleleType.NA and (not keep_na):
        return None
    else:
        return alleles[0]


def twiAllele(
    alleles_count: Counter, max_na: float, keep_na: bool = False
) -> Optional[str]:
    if AlleleType.NA in alleles_count:
        na_portion = alleles_count[AlleleType.NA] / sum(alleles_count.values())
        if na_portion < max_na:
            alleles = list(alleles_count.keys())[:]
            alleles.remove(AlleleType.NA)
            return alleles[0]
        elif keep_na:
            return AlleleType.NA
    return None


def isHybrid(allele: str) -> bool:
    return allele != AlleleType.NA and len(set(list(allele.replace("/", "")))) > 1


def equalNA(value):
    return value == AlleleType.NA


def replaceHybrid(allele: Optional[str]) -> Optional[str]:
    if allele and not isHybrid(allele):
        return allele
    else:
        return None


def isATGCorNA(value: Union[str, float, int]) -> bool:
    if isNA(str(value)) or isSignal(str(value)):
        return True
    return False