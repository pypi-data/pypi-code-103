from pprint import pprint
from text_analyzer.reports import WordsReport, SentencesReport, PalindromeReport, CharactersReport


def print_reports(words_report: WordsReport, sentences_report: SentencesReport, characters_report: CharactersReport,
                  palindrome_report: PalindromeReport, filename: str):
    print(f"Text Analyzer report for {filename} :")
    print(f"Number of characters in processed text is {characters_report.characters_number}.")
    print(f"Number of words in processed text is {words_report.words_number}.")
    print(f"Number of sentences in processed text is {sentences_report.sentences_number}.")

    print(f"Frequency of characters in processed text is: ")
    pprint(characters_report.characters_freq)

    print(f"Distribution of characters as a percentage of total in processed text is: ")
    pprint(characters_report.characters_distribution)

    print(f"Average word length in processed text is {words_report.average_word_length} characters.")
    print(
        f"The average number of words in a sentence in processed text is {sentences_report.average_word_number}.")

    print(f"Top 10 most used words in processed text are:")
    pprint(words_report.top_10_most_used_words)

    print(f"Top 10 longest words in processed text are:")
    pprint(words_report.top_10_longest_words)

    print(f"Top 10 shortest words in processed text are:")
    pprint(words_report.top_10_shortest_words)

    print(f"Top 10 longest sentences in processed text are ")
    pprint(sentences_report.top_10_longest_sentences)

    print(f"Top 10 shortest sentences in processed text are ")
    pprint(sentences_report.top_10_shortest_sentences)

    print(f"Number of palindrome words in processed text is {words_report.number_of_palindromes}.")
    print(f"Top 10 longest palindrome words in processed text is: ")
    pprint(words_report.top_10_longest_palindromes)
    is_pal_text = "Yes" if palindrome_report.is_whole_text_palindrome else "No"
    print(f"Is the whole text a palindrome? (Without whitespaces and punctuation marks.): {is_pal_text}")

    print(f"The reversed text is: ")
    pprint(characters_report.reversed_text)

    print(f"The reversed text but the character order in words kept intact is: ")
    pprint(words_report.reversed_text_order_kept)



def print_process_time(process_time, filename: str):
    print(f"Time took to process {filename} text in ms:{process_time}")
