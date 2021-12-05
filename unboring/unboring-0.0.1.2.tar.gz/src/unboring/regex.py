import re

#Counts how many occurances there of a substring in a string
def countUp(txt, findstr):
    found = re.findall(findstr, txt)
    return len(found)

#Splits At the string
def splitAt(txt, splitstr):
    splitTxt = re.split(splitstr, txt)
    return splitTxt

#Replaces substrings with different values
def substitute(txt, substr, replace):
    newTxt = re.sub(substr, replace, txt)
    return newTxt 
