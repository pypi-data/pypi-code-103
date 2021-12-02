import datetime
from typing import TypeVar, Any

from boltons.iterutils import remap

Data = TypeVar('Data')


def _convert(term: Any) -> Any:  # type: ignore
    """Convert $statement to @statement."""
    if isinstance(term, str) and term.startswith('$'):
        return '@' + term[1:]  # noqa: WPS336

    # pyld cannot expand() a document which contains data which cannot be
    # trivially serialized to JSON.
    # FIXME we may want to replace this with an xsd:date declaration, but let's
    #   revisit that later.
    if isinstance(term, (datetime.date, datetime.datetime)):
        return str(term)

    return term


def convert_dollar_signs(
    meta_data: Data,
) -> Data:
    """
    Convert $ character to @ in keys.

    We use $ by convention to avoid writing quotes.
    """
    if not meta_data:
        return {}

    return remap(
        meta_data,
        lambda path, key, value: (  # noqa: WPS110
            _convert(key),
            _convert(value),
        ),
    )
