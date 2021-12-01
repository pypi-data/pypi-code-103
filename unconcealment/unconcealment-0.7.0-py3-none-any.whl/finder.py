from typing import Final, Optional

from unconcealment.secret_pattern import SecretPattern

MAX_TESTED_LENGTH: Final = 5000


def extract_secret(tested: str, secret_pattern: SecretPattern) -> Optional[str]:
    """ Check if a string contains a secret using regexp"""
    if len(tested) == 0:
        return None
    result = None
    for i in range(0, len(tested), MAX_TESTED_LENGTH):
        value = tested[i:i + MAX_TESTED_LENGTH]
        for inclusion in secret_pattern.value.inclusions:
            if inclusion.match(value) is None:
                return None
            search = inclusion.search(value)
            result = (search.group(1) if search is not None and len(search.groups()) >= 1 else tested).strip()
    for exclusion in secret_pattern.value.exclusions:
        search = exclusion.search(tested)
        if search:
            return extract_secret(exclusion.sub('', tested), secret_pattern)
    return result
