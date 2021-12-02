"""
The script contains the following text based validations:
1. HTML
2. XML
3. JSON
4. Text Characteristics - Length, Special Characters, Alphabets, Digits
"""

# Imports
from xml.etree import ElementTree

import re
import json


# HTML Validations
def validate_html(html: str) -> bool:
    regex = "<(\"[^\"]*\"|'[^']*'|[^'\">])*>"

    regex = re.compile(pattern=regex)

    if re.search(pattern=regex, string=html):
        return True

    return False


# XML Validations
def validate_xml(xml: str) -> bool:
    try:
        x = ElementTree.fromstring(xml)
        if x:
            return True
    except ElementTree.ParseError:
        return False


# JSON Validation
def validate_json(data: str) -> bool:
    try:
        val = json.loads(data)

        if val:
            return True
    except json.JSONDecodeError:
        return False


# Text Characteristic Validations
def validate_text(text: str, min_length: int = None, max_length: int = None,
                  special_characters: bool = True, allow_alpha: bool = True,
                  allow_digits: bool = True) -> bool:

    # Count Checks
    checks = 0

    # noinspection RegExpRedundantEscape
    sp_chars = re.compile("[@_!#$%^&*()<>?/\|}{~:]")
    alphas = re.compile("[a-zA-Z]")
    digits = re.compile("[0-9]")

    if min_length is not None and len(text) >= min_length:
        checks += 1

    if max_length is not None and len(text) <= max_length:
        checks += 1

    if special_characters and re.search(pattern=sp_chars, string=text) is None:
        checks += 1

    if allow_alpha and re.search(pattern=alphas, string=text) is None:
        checks += 1

    if allow_digits and re.search(pattern=digits, string=text) is None:
        checks += 1

    if min_length is not None and max_length is not None and special_characters \
            and allow_alpha and allow_digits and checks == 5:
        return True
    elif min_length is None and max_length is not None and special_characters \
            and allow_alpha and allow_digits and checks == 4:
        return True
    elif min_length is not None and max_length is None and special_characters \
            and allow_alpha and allow_digits and checks == 4:
        return True
    elif min_length is None and max_length is None and special_characters \
            and allow_alpha and allow_digits and checks == 3:
        return True
    elif min_length is None and max_length is None \
            and allow_alpha and allow_digits and checks == 2:
        return True
    elif min_length is None and max_length is None and special_characters \
            and allow_digits and checks == 2:
        return True
    elif min_length is None and max_length is None and special_characters \
            and allow_alpha and checks == 2:
        return True

    return False
