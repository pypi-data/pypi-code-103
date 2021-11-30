"""
验证address
"""
import re

from dddd_utils.mail.mail_exception import InvalidEmailAddress

WSP = r'[ \t]'
CRLF = r'(?:\r\n)'
NO_WS_CTL = r'\x01-\x08\x0b\x0c\x0f-\x1f\x7f'
QUOTED_PAIR = r'(?:\\.)'
FWS = r'(?:(?:' + WSP + r'*' + CRLF + r')?' + WSP + r'+)'
CTEXT = r'[' + NO_WS_CTL + r'\x21-\x27\x2a-\x5b\x5d-\x7e]'
CCONTENT = r'(?:' + CTEXT + r'|' + QUOTED_PAIR + r')'
COMMENT = r'\((?:' + FWS + r'?' + CCONTENT + r')*' + FWS + r'?\)'
CFWS = r'(?:' + FWS + r'?' + COMMENT + ')*(?:' + FWS + '?' + COMMENT + '|' + FWS + ')'
ATEXT = r'[\w!#$%&\'\*\+\-/=\?\^`\{\|\}~]'
ATOM = CFWS + r'?' + ATEXT + r'+' + CFWS + r'?'
DOT_ATOM_TEXT = ATEXT + r'+(?:\.' + ATEXT + r'+)*'
DOT_ATOM = CFWS + r'?' + DOT_ATOM_TEXT + CFWS + r'?'
QTEXT = r'[' + NO_WS_CTL + r'\x21\x23-\x5b\x5d-\x7e]'
QCONTENT = r'(?:' + QTEXT + r'|' + QUOTED_PAIR + r')'
QUOTED_STRING = CFWS + r'?' + r'"(?:' + FWS + r'?' + QCONTENT + r')*' + FWS + r'?' + r'"' + CFWS + r'?'
LOCAL_PART = r'(?:' + DOT_ATOM + r'|' + QUOTED_STRING + r')'
DTEXT = r'[' + NO_WS_CTL + r'\x21-\x5a\x5e-\x7e]'
DCONTENT = r'(?:' + DTEXT + r'|' + QUOTED_PAIR + r')'
DOMAIN_LITERAL = CFWS + r'?' + r'\[' + r'(?:' + FWS + r'?' + DCONTENT + r')*' + FWS + r'?\]' + CFWS + r'?'
DOMAIN = r'(?:' + DOT_ATOM + r'|' + DOMAIN_LITERAL + r')'
ADDR_SPEC = LOCAL_PART + r'@' + DOMAIN

VALID_ADDRESS_REGEXP = '^' + ADDR_SPEC + '$'


def validate_email_with_regex(email_address):
    if not re.match(VALID_ADDRESS_REGEXP, email_address):
        emsg = 'Emailaddress "{}" is not valid according to RFC 2822 standards'.format(
            email_address)
        raise InvalidEmailAddress(emsg)
    if "." not in email_address and "localhost" not in email_address.lower():
        raise InvalidEmailAddress("Missing dot in emailaddress")
