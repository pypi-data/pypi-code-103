def is_cmyk(cmyk: str) -> bool:
    try:
        cmyk_split = cmyk.split("/")
    except:
        return False
    for e in cmyk_split:
        try:
            int(e)
        except:
            return False
        if len(e) > 3:
            return False
        if int(e) > 100 or int(e) < 0:
            return False
    return True


def is_single_cmyk(cmyk: int) -> bool:
    if 100 >= cmyk >= 0:
        return True
    else:
        return False
