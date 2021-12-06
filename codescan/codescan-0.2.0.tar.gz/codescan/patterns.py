import re


def check_security_pattern(check_string):
    pattern = r"(['\"]*[a-zA-Z0-9_-]*[pP][aA][sS]+[wW][oO][rR][dD][sS'\"]*|" \
                "['\"]*[a-zA-Z0-9_-]*[sS][eE][cC][rR][eE][tT][a-zA-Z0-9_-]*['\"]*)" \
                "[\s]*(=>|:|=)[\s]*((?:'|\").*(?:'|\")|\d*)"

    results = re.findall(pattern, check_string)
    if len(results) > 0:
        return results

    return None


def check_leaks_in_comments(check_string):

    pattern = r"[/#*%}]+[\s'\"]*([a-zA-z0-9]*[pP]+[aA]+[sS]+[wW]+[oO]+[rR]+[dD]+[a-zA-Z0-9]*|" \
              "[a-zA-z0-9_-]*[sS]+[eE]+[cC]+[rR]+[eE]+[tT]+[a-zA-Z0-9_-]*)[\s'\"]*(=>|:|=)[\s'\"]*" \
              "([a-zA-Z0-9~!@#$%\^&*()_+=-]+)[\s{%'\"]*"

    results = re.findall(pattern, check_string)
    if len(results) > 0:
        return results

    return None

