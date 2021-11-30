from edition.exceptions.edition_error import EditionError


class NoPressError(EditionError):
    """Raised when a requested press does not exist."""

    def __init__(self, key: str) -> None:
        super().__init__(f'No press for "{key}"')
