# filters.py
# additional jinja2 filters used by the songbook rendering engine


def safe_name(chord):
    """
    Makes chordnames 'safe' (no shell special chars)
    Might need expanding for Windows/Mac)

    Args:
        chord(str): a chordname to manipulate

    Returns:
        str: chordname with awkward characters replaced
    """
    # rules:
    # replace '#' with _sharp if at end,
    #                   _sharp_ if not
    # replace '/' with _on_
    return chord.translate({ord("#"): "_sharp_", ord("/"): "_on_"})


custom_filters = {
    "safe_name": safe_name,
}
