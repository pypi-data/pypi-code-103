"""
Meaningless
An Epytomil module
Created by: Zhean 'Z1aaan' Ganituen

Meaningless is a dummy text generator for Epytoml and it's modules.
"""

from lorem.text import TextLorem
import string
import random


def loremIpsum(wordCount, printOut=None):
    """Generate lorem ipsum dummy text.

    Args:
        wordCount (int): The number of words the function will generate
        printOut (bool, optional): Print out the generated dummy text. Defaults to False.

    Returns:
        The lorem ipsum dummy text.
    """

    lorem = TextLorem(wsep=" ", srange=(wordCount, wordCount))

    meaningless_text = lorem.sentence()

    # check if printOut is not none
    if printOut is not None:
        # print out is not none and is true so print out the generated text.
        if printOut == True:
            print(meaningless_text)
        # print out is not none and is false so only return the generated text.

    return meaningless_text


def deadText(wordCount, wordLength, letterCase=None, printOut=None):
    """Generate random dummy text.

    Args:
        wordCount (int): The number of words the function will generate.
        wordLength (int): The length of each randomly generated word.
        letterCase (int, optional): Specify the letter case (1 Lower, 2 Upper, 3 Both). Defaults to 3.
        printOut (bool, optional): Print out the generated dummy text. Defaults to False.

    Returns:
        The randomly generated dummy text.
    """

    # final output
    meaningless_text = ""

    # check if letter case is none
    if letterCase is None:
        # if letter case is none, set it to default (lower and upper case)
        caseMin = 0
        caseMax = 51
    else:
        # if letter case is not none, then use the given
        if letterCase == 1:
            # if letter case is lower, make the caseMin and caseMax to 1 and 25
            caseMin = 0
            caseMax = 25
        elif letterCase == 2:
            # if letter is upper, make the caseMin and caseMax to 26 and 51
            caseMin = 26
            caseMax = 51
        else:
            # if letter case is not found, set it to default or lower case and upper case
            caseMin = 0
            caseMax = 51

    # generate a N number of string of random characters based on the wordCount
    for i in range(wordCount):
        # Generate random characters to be added to the meaningless_text string
        # then stop generating then add a space when the wordLength is reached
        for i in range(wordLength):
            letter = random.randint(caseMin, caseMax)
            meaningless_text += string.ascii_letters[letter]
        # add a space after every randomly generated word
        meaningless_text += " "

    # check if printOut is not none
    if printOut is not None:
        # print out is not none and is true so print out the generated text.
        if printOut == True:
            print(meaningless_text)
        # print out is not none and is false so only return the generated text.

    return meaningless_text


def horiLine(lineLength, lineWidth=None, lineCharacter=None, printOut=None):
    """Generate a horizontal line.

    Args:
        lineLength (int): The length of the line or how many characters the line will have.
        lineWidth (int, optional): The width of the line or how many lines of text the line will take space. Defaults to 1.
        lineCharacter (str, optional): The string, character, or number the line will use as a single character. Defaults to '-'.
        printOut (bool, optional): Print out the generated dummy text. Defaults to False.

    Returns:
        The horizontal line created.
    """
    meaningless_text = ""
    lineGenerated = ""

    # check if lineWidth is none
    if lineWidth is None:
        # if lineWidth is none, set it to default of 1
        width = 1
    else:
        # if line wdith is not none, set it to the given value
        width = lineWidth

    # check if lineCharacter is none
    if lineCharacter is None:
        # if lineCharacter is none, set it to default "-"
        character = "-"
    else:
        # if line character is not none, then use the user specified character
        character = lineCharacter

    for i in range(width):
        # generate a line
        for char in range(lineLength):
            lineGenerated += character
        if width > 1:
            # if line width is greater than 1, append a new line character
            lineGenerated += "\n"

    meaningless_text += lineGenerated

    # check if printOut is not none
    if printOut is not None:
        # print out is not none and is true so print out the generated text.
        if printOut == True:
            print(meaningless_text)
        # print out is not none and is false so only return the generated text.

    return meaningless_text
