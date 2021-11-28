class CompareStrings:
    def __init__(self, lower_limit: int, upper_limit: int, case_insensitive=True):
        """
        lower_limit: Lower limit of the allowed UTF-8 character in compare_strings function
        upper_limit: Upper limit of the allowed UTF-8 character in compare_strings function
        For English words, lower_limit=97 and upper_limit=122;
        97 being UTF-8 code of character "a" and 122 of character "z"
        ch_count: Number of allowed characters
        For English words, ch_count=26
        """
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.ch_count = self.upper_limit - self.lower_limit + 1
        if case_insensitive:
            self.transform = lambda x: x.lower()
        else:
            self.transform = lambda x: x

    def _word_description(self, word: str):
        """
        returns a list representation of the word
        """
        word_desc_list = [0]*self.ch_count
        for ch in word:
            code = ord(self.transform(ch)) - self.lower_limit
            if 0 <= code < self.ch_count:
                word_desc_list[code] += 1
        return word_desc_list

    def compare_strings(self, word1: str, word2: str) -> float:
        """
        O(n+m) algorithm to calculate comparison score
        where n = length of word1, m = length of word1
        The function returns a real number between 0 and 1
        0 denoting no match at all
        1 denoting complete match
        """
        diff = 0.0
        wdl1 = self._word_description(word1)
        wdl2 = self._word_description(word2)
        for i in range(len(wdl1)):
            diff += abs(wdl1[i] - wdl2[i])
        return 1 - diff/(len(word1) + len(word2))


compare_english_words = CompareStrings(97, 122).compare_strings