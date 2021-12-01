# import json
# import hashlib
# import string
# import utils.objectUtils as objUtils


def leftPad(subject, max_len=2, pad_char='0'):
    '''
        Convert a subject to snake case.

        ----------
        Arguments
        -----------------
        `subject` {subject}
            The subject to convert
        `max_len` {int}
            The maximum length of the subject, if >= max_len the subject will not be padded.
        `pad_char` {subject}
            The character to pad the subject with
        Return
        ----------
        `return` {subject}
            The subject formatted with left padding

        Example
        ----------            
        leftPad("1",5,'0') // "00001"
    '''
    subject = str(subject)
    slen = len(subject)
    if slen <= max_len:
        subject = f"{pad_char * (max_len - slen)}{subject}"
    return subject
