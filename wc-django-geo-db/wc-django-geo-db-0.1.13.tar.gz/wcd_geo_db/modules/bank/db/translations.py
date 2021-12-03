from pxd_lingua import create_translated_model

from .divisions import Division


__all__ = 'DivisionTranslation',


DivisionTranslation = create_translated_model(
    Division, fields=('name', 'synonyms')
)
