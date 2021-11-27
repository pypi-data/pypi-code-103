"""
ShortcutMiner
An Epytoml module
Created by: Zhean 'Z1aaan' Ganituen

ShortcutMiner is a module that mines the possible shortcuts of a given text.
"""

from collections import Counter
import re


def mineText(content, shortcutCount, address):
    """Creats a shortcut dictionary from the given text for Notaker to use.

    Args:
        content (str): The text to mine shortcuts from.
        shortcutCount (int): How many shortcuts to mine.
        address (str): The shortcut address the mined shortcuts will be saved to.

    Returns:
        The dictionary of the mined shorcuts.
    """
    Shortcuts = {}
    initialMined_Shortcuts = {}

    # remove the non-alphabet characters in the content
    alphabet = re.compile("[^a-zA-Z]")
    filteredContent = re.sub(alphabet, " ", content)

    # convert the filteredContent into a list of words
    word_list = list(filteredContent.split())

    # count the number of times each word appears in the word_list
    Shortcuts = Counter(word_list)

    # sort the Shortcuts by the number of times each word appears
    Shortcuts = Shortcuts.most_common(shortcutCount)

    # only accept words that appear more than once
    for key in range(shortcutCount):
        # check if their occurence count is greater than 1
        if Shortcuts[key][1] > 1:
            initialMined_Shortcuts[key] = ["", Shortcuts[key][0]]

    mined_Shortcuts = {}

    # add 1 to the keys of the dictionary because it starts at 0
    for key in range(len(initialMined_Shortcuts)):
        mined_Shortcuts[key + 1] = initialMined_Shortcuts[key]
        del initialMined_Shortcuts[key]

    # assign the address to the mined shortcuts
    for key in range(1, len(mined_Shortcuts) + 1):
        finalAddress = address + str(key)
        mined_Shortcuts[key][0] = finalAddress

    return mined_Shortcuts
