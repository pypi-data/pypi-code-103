import re


class SentencesReport:
    SENTENCES_MARKS = r".|\?|\!|"
    SPACE = " "

    def __init__(self, text: str):
        self.sentences = re.split(r"[.?!]", text)
        self.sentences = list(filter(lambda sentence: len(sentence) != 0, self.sentences))
        self.sentences = list(map(lambda sentence: sentence.strip(), self.sentences))
        self._generate_report()

    def get_average_number_of_words_in_sentence(self):
        number_of_words_in_sentences = list(map(lambda sentence: len(sentence.split(self.SPACE)), self.sentences))
        average_number_of_words_in_sentence = sum(number_of_words_in_sentences) / len(number_of_words_in_sentences)
        return average_number_of_words_in_sentence

    def get_top_10_longest_sentences(self):
        sorted_sentences = sorted(self.sentences, key=lambda sentence: len(sentence), reverse=True)
        return sorted_sentences[:10]

    def get_top_10_shortest_sentences(self):
        sorted_sentences = sorted(self.sentences, key=lambda sentence: len(sentence))
        return sorted_sentences[:10]

    def _generate_report(self):
        self.sentences_number = len(self.sentences)
        self.average_word_number = self.get_average_number_of_words_in_sentence()
        self.top_10_longest_sentences = self.get_top_10_longest_sentences()
        self.top_10_shortest_sentences = self.get_top_10_shortest_sentences()
