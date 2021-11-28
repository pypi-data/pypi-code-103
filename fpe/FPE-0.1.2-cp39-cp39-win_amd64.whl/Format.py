DIGITS = 0
CREDITCARD = 1
LETTERS = 2
STRING = 3
EMAIL = 4
CPR = 5

formats = [DIGITS, CREDITCARD, LETTERS, STRING, EMAIL, CPR]
def isFormat(format):
    if format not in formats:
        return False
    else:
        return True