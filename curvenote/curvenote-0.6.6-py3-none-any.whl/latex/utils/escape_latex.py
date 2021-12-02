import re

escapes = [
    (r"\\ ", "BACKSLASHSPACE"),
    (r"\\", "BACKSLASH"),
    ("~", "TILDE"),
    ("&", "\\&"),
    ("%", "\\%"),
    ("\\$", "\\$"),
    ("#", "\\#"),
    ("_", "\\_"),
    ("\\{", "\\{"),
    ("\\}", "\\}"),
    ("\\^", "\\^"),
    ("BACKSLASHSPACE", r"{\\textbackslash}~"),
    ("BACKSLASH", r"{\\textbackslash}"),
    ("TILDE", r"{\\textasciitilde}"),
]


def escape_latex(content: str):
    if not content:
        return content
    for old, new in escapes:
        content = re.sub(old, new, content)
    return content
