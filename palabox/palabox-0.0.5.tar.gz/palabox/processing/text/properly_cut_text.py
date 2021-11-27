"""Cut properly some text."""

import re

END_OF_SENTENCE_CHARACTERS = {".", ";", "!", "?"}


def properly_cut_text(
    text: str, start_idx: int, end_idx: int, nbr_before: int = 30, nbr_after: int = 30
) -> str:
    """Properly cut a text around some interval."""
    str_length = len(text)
    start_idx = max(0, start_idx - nbr_before)
    end_idx = end_idx + nbr_after

    # Change the end depending on the value
    match = re.search(r"\.[^\d]|\?|\!", text[end_idx:], flags=re.IGNORECASE)
    if match:
        end_idx = match.end() + end_idx
    else:
        end_idx = str_length

    # Change the beginning depending on the value
    match = re.search(r"(\.|\?|\!)(?!.*\1)", text[: start_idx - 1], flags=re.IGNORECASE)
    if match:
        start_idx = match.end() + 1
    else:
        start_idx = 0

    return text[start_idx:end_idx].strip()
