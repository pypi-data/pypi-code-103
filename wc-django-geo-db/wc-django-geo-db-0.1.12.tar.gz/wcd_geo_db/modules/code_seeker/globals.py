from .registry import CodeSeekerRegistry
from .builtins import ISO3166_SEEKER


__all__ = 'registry',

registry = CodeSeekerRegistry((
    ISO3166_SEEKER,
))
