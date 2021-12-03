from typing import Any, Dict, Optional, Sequence, Tuple, TypeVar
from wcd_geo_db.modules.code_seeker import CodeSeekerRegistry, query


QT = TypeVar('QT', bound=query.CodeSeekerQuerySet)


class CodeSeekingClientMixin:
    code_seeker_registry: CodeSeekerRegistry

    def __init__(
        self, *_, **kw
    ):
        code_seeker_registry = kw.get('code_seeker_registry')

        assert code_seeker_registry is not None, (
            'Code seeking registry must not be empty.'
        )

        super().__init__(**kw)

        self.code_seeker_registry = code_seeker_registry

    def _get_codes_filter(
        self, codes:  Optional[query.CodeSeekSeq] = None
    ) -> query.CodesFilter:
        return {
            'registry': self.code_seeker_registry,
            'codes': codes,
            'warning_context': f'{self.__class__} client\'s registry'
        }
