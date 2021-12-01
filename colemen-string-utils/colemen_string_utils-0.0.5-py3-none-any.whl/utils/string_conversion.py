import json
import hashlib
import string

import re
import utils.objectUtils as objUtils


def to_snake_case(subject):
    '''
        Convert a subject to snake case.

        ----------
        Arguments
        -----------------
        `subject` {str}
            The subject to convert

        Return
        ----------
        `return` {str}
            The subject converted to snake case

        Example
        ----------            
        BeepBoop Bleep blorp => beep_boop_bleep_blorp
    '''
    subject = str(subject)
    subject = re.sub(r'([a-z])([A-Z])', r'\1_\2', subject)
    subject = subject.replace(' ', '_')
    return subject.lower()


def to_screaming_snake(subject):
    '''
        Convert a subject to screaming snake case.

        ----------
        Arguments
        -----------------
        `subject` {str}
            The subject to convert

        Return
        ----------
        `return` {str}
            The subject converted to screaming snake case

        Example
        ----------            
        BeepBoop Bleep blorp => BEEP_BOOP_BLEEP_BLORP
    '''
    return to_snake_case(subject).upper()
