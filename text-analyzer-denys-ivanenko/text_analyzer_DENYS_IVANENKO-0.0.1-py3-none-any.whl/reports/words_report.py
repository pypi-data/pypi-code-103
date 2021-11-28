from collections import Counter
from text_analyzer.reports import PalindromeReport


class WordsReport:
    def __init__(self, text: str):
        self.words = text.split(" ")
        self._generate_report()

    def _generate_report(self):
        self.words_number = len(self.words)
        self._get_average_word_length()
        self._get_top_10_most_used_words()
        self._get_top_10_shortest_words()
        self._get_top_10_longest_words()
        self._get_palindrome_report()
        self._get_reversed_text_order_kept()

    def _get_average_word_length(self):
        word_lengths = list(map(len, self.words))
        self.average_word_length = sum(word_lengths) / len(self.words)

    def _get_top_10_most_used_words(self):
        words_statistics = Counter(self.words)
        top_10_most_used_words = words_statistics.most_common(10)
        self.top_10_most_used_words = list(map(lambda word: word[0], top_10_most_used_words))

    def _get_top_10_shortest_words(self):
        words_sorted = sorted(self.words, key=lambda word: len(word))
        self.top_10_shortest_words = words_sorted[:10]

    def _get_top_10_longest_words(self):
        words_sorted = sorted(self.words, key=lambda word: len(word), reverse=True)
        self.top_10_longest_words = words_sorted[:10]

    def _get_reversed_text_order_kept(self):
        reversed_words = list(reversed(self.words))
        self.reversed_text_order_kept = " ".join(reversed_words)

    def _get_palindrome_report(self):
        palindromes = list(filter(lambda word: PalindromeReport.is_palindrome(word), self.words))
        self.number_of_palindromes = len(palindromes)
        self.top_10_longest_palindromes = self.get_top_10_longest_palindromes(palindromes)

    @staticmethod
    def get_top_10_longest_palindromes(palindromes: list[str]) -> list[str]:
        sorted_palindromes = sorted(palindromes, key=lambda word: len(word))
        return sorted_palindromes[:10]
