import re

def check_alcoholic(text):
    pattern = r".*[^non-]alcohol.*"
    return bool(re.match(pattern, text))
