import json
import hashlib
import string

import re
import utils.objectUtils as objUtils


def to_snake_case(string):
    '''
        Convert a string to snake case.

        ----------
        Arguments
        -----------------
        `string` {str}
            The string to convert

        Return
        ----------
        `return` {str}
            The string converted to snake case

        Example
        ----------            
        BeepBoop Bleep blorp => beep_boop_bleep_blorp
    '''
    string = str(string)
    string = re.sub(r'([a-z])([A-Z])', r'\1_\2', string)
    string = string.replace(' ', '_')
    return string.lower()


def to_screaming_snake(string):
    '''
        Convert a string to screaming snake case.

        ----------
        Arguments
        -----------------
        `string` {str}
            The string to convert

        Return
        ----------
        `return` {str}
            The string converted to screaming snake case

        Example
        ----------            
        BeepBoop Bleep blorp => BEEP_BOOP_BLEEP_BLORP
    '''
    return to_snake_case(string).upper()
