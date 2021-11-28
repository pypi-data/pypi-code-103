class PalindromeReport:
    PUNCTUATION = [" ", ",", ".", "!", "?", ":", ";"]

    def __init__(self, text):
        self.text = text
        self._check_text_for_palindrome()

    def _check_text_for_palindrome(self):
        text_without_punctuation = self.text
        for mark in self.PUNCTUATION:
            text_without_punctuation = text_without_punctuation.replace(mark, "")
        self.is_whole_text_palindrome = self.is_palindrome(text_without_punctuation)

    @staticmethod
    def is_palindrome(text: str) -> bool:
        return text == text[::-1]
