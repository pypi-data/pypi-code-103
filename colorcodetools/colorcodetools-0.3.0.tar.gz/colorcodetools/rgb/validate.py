def is_rgb(rgb: str, a: float = 1.0) -> bool:
    try:
        rgb_split = rgb.replace("(", "")
        rgb_split = rgb_split.replace(")", "")
        rgb_split = rgb_split.split(",")
    except:
        return False
    if len(rgb_split) != 3:
        return False
    for e in rgb_split:
        try:
            if int(e) > 255 or int(e) < 0:
                return False
        except:
            return False
    if a > 1.0 or a < 0.0:
        return False
    return True


def is_single_rgb(rgb: int) -> bool:
    if 255 >= rgb >= 0:
        return True
    else:
        return False
