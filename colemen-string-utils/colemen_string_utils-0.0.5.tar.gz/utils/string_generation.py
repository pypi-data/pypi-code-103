import json
import hashlib
import string
import random
import utils.objectUtils as objUtils


def hash(value):
    '''
        Generates a sha256 hash from the string provided.

        ----------
        Arguments
        -----------------
        `value` {str}
            The string to calculate the hash on.

        Return
        ----------
        `return` {str}
            The sha256 hash
    '''
    jsonStr = json.dumps(value).encode('utf-8')
    hex_dig = hashlib.sha256(jsonStr).hexdigest()
    return hex_dig


def rand(length=12, **kwargs):
    '''
        Generates a cryptographically secure random string.


        ----------
        Arguments
        -----------------
        `length`=12 {int}
            The number of characters that the string should contain.

        Keyword Arguments
        -----------------
        `upper_case`=True {bool}
            If True, uppercase letters are included.
            ABCDEFGHIJKLMNOPQRSTUVWXYZ

        `lower_case`=True {bool}
            If True, lowercase letters are included.
            abcdefghijklmnopqrstuvwxyz

        `digits`=True {bool}
            If True, digits are included.
            0123456789

        `symbols`=False {bool}
            If True, symbols are included.
            !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~

        `exclude`=[] {string|list}
            Characters to exclude from the random string.

        Return
        ----------
        `return` {str}
            A random string of N length.
    '''

    uppercase = objUtils.get_kwarg(['upper case', 'upper'], True, bool, **kwargs)
    lowercase = objUtils.get_kwarg(['lower case', 'lower'], True, bool, **kwargs)
    digits = objUtils.get_kwarg(['digits', 'numbers', 'numeric', 'number'], True, bool, **kwargs)
    symbols = objUtils.get_kwarg(['symbols', 'punctuation'], False, bool, **kwargs)
    exclude = objUtils.get_kwarg(['exclude'], [], (list, string), **kwargs)

    choices = ''
    if uppercase is True:
        choices += string.ascii_uppercase
    if lowercase is True:
        choices += string.ascii_lowercase
    if digits is True:
        choices += string.digits
    if symbols is True:
        choices += string.punctuation

    if len(exclude) > 0:
        if isinstance(exclude, str):
            exclude = list(exclude)
        for e in exclude:
            choices = choices.replace(e, '')

    return ''.join(random.SystemRandom().choice(choices) for _ in range(length))


def variations(string):
    '''
        Generates simple variations of the string provided.

        ----------
        Arguments
        -----------------
        `string` {str}
            The string to generate variations of

        Keyword Arguments
        -----------------
        `upper_case`=True {bool}
            If True, uppercase letters are included.
            ABCDEFGHIJKLMNOPQRSTUVWXYZ

        Return
        ----------
        `return` {str}
            A list of variations.

        Example
        ----------
        BeepBoop => ['BEEPBOOPBLEEPBLORP','beepboopbleepblorp','beep_boop','BEEP_BOOP']
    '''
    string = str(string)
    varis = []
    lower = string.lower()
    upper = string.upper()
    snake_case = lower.replace(" ", "_")
    screaming_snake_case = upper.replace(" ", "_")
    varis.append(lower)
    varis.append(upper)
    varis.append(snake_case)
    varis.append(screaming_snake_case)
    return varis
