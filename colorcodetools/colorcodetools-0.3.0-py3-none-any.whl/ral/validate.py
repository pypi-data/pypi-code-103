from colorcodetools.ral.config import valid_codes


def is_ral(ralcode: int) -> bool:
    codes = valid_codes()
    try:
        codes.index(ralcode)
    except:
        return False
    return True
