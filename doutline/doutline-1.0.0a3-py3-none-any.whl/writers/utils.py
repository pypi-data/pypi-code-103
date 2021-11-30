def make_anchor(value: str) -> str:
    """
    Makes a GitHub-compatible anchor for `value`.

    Arguments:
        value: Heading to anchor.

    Returns:
        Anchor.
    """

    wip = ""
    for c in value:
        if str.isalnum(c):
            wip += c.lower()
        elif c in [" ", "-"]:
            wip += "-"
    return wip
