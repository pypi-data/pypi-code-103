"""
The script contains the following miscellaneous validations:
1. IP Address
2. MAC Address
3. Date
4. E-Mail Address
"""

# Imports
from datetime import datetime

import re


# IP Address Validations
def validate_ip(ip: str) -> bool:
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

    regex = re.compile(pattern=regex)

    if re.search(pattern=regex, string=ip):
        return True

    return False


# MAC Address Validations
def validate_mac(mac: str) -> bool:
    regex = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})|([0-9a-fA-F]{4}\\.[0-9a-fA-F]{4}\\.[0-9a-fA-F]{4})$"

    regex = re.compile(pattern=regex)

    if re.search(pattern=regex, string=mac):
        return True

    return False


# Date Validations
def validate_date(date: str, date_format: str) -> bool:
    if datetime.strptime(date_string=date, format=date_format):
        return True

    return False


# E-Mail Address Validations
def validate_email(email: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if re.fullmatch(pattern=regex, string=email):
        return True

    return False
