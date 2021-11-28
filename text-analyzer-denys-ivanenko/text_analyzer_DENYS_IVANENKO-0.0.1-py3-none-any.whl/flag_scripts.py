import datetime

from text_analyzer.constants import HELP_TEXT
from text_analyzer.db_utils import save_reports_to_db, get_reports_from_db
from text_analyzer.printers import print_reports, print_process_time
from text_analyzer.reports import WordsReport, SentencesReport, CharactersReport, PalindromeReport


def print_help():
    print(HELP_TEXT)


def text_analyzer(text, filename):
    start_time = datetime.datetime.now()

    words_report = WordsReport(text)
    sentences_report = SentencesReport(text)
    characters_report = CharactersReport(text)
    palindrome_report = PalindromeReport(text)

    print_reports(words_report, sentences_report, characters_report, palindrome_report, filename)
    save_reports_to_db(words_report, sentences_report, characters_report, palindrome_report, filename)

    finish_time = datetime.datetime.now()
    process_time = (finish_time - start_time).total_seconds() * 1000
    print_process_time(process_time, filename)


def view_file_reports(filename: str):
    matched_file_reports = get_reports_from_db(filename)
    for file_reports in matched_file_reports:
        print_reports(*file_reports.reports, file_reports.name)
