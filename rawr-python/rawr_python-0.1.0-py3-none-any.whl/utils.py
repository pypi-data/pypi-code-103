from boltons.iterutils import remap


def renamestyle_keys(json_dict) -> dict:
    return remap(
        json_dict,
        visit=lambda p, k, v: (camel_to_snake(k.replace("CC", "Cc")), v)
        if isinstance(k, str)
        else (k, v),
    )


def camel_to_snake(s: str) -> str:
    return "".join(["_" + c.lower() if c.isupper() else c for c in s]).lstrip("_")
