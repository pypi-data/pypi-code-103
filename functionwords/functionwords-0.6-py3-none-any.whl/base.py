"""
@author: Haining Wang
Created on March 17, 2021.
Modified on Nov. 19, 2021.
"""

import re
import os
import json

NAMES = ["chinese_classical_comprehensive", "chinese_classical_naive", "chinese_simplified_modern", "english"]


class FunctionWords(object):
    """
    The main class does the heavy lifting.

    Attr:
        name: Which function word list is called. Either 'chinese_classical_comprehensive', 'chinese_classical_naive',
         'chinese_simplified_modern', or 'english'.
        function_words: The corresponding function word list.
        description: The description of the function word list.
    """

    def __init__(self, name):
        self.__path__ = os.path.dirname(__file__)
        if name.lower() in NAMES:
            self.name = name.lower()
        else:
            raise ValueError(f"""Pass in desired function word list in {NAMES}.""")
        self.function_words = json.load(
            open(os.path.join(self.__path__, "resources", self.name + ".json"), "r")
        )
        self.description = json.load(
            open(os.path.join(self.__path__, "resources", "description.json"), "r")
        )[self.name]

    def get_feature_names(self):
        """
        Returns a list of desired function words.
        """

        return self.function_words

    def transform(self, raw):
        """
        Counts function words in `raw`.
        param:
            raw: A string.
        return:
            A list of count of function words.
        """
        if not isinstance(raw, str):
            raise ValueError(
                f"""List of raw text documents expected, {type(raw)} object received."""
            )
        if self.name == 'english':
            counts = [len(re.findall(r"\b" + function_word + r"\b", raw.lower())) for function_word in self.function_words]
        else:
            counts = [len(re.findall(function_word, raw)) for function_word in self.function_words]

        return counts

    def fit_transform(self, raw):

        return self.transform(raw)

    def fit(self, raw):

        return self.transform(raw)
