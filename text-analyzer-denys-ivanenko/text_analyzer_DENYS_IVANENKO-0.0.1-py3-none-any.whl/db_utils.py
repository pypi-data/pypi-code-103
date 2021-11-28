from os import path

from model import FileReports
from text_analyzer.db import session
from text_analyzer.file_utils import clean_file_lead
from text_analyzer.reports import WordsReport, SentencesReport, CharactersReport, PalindromeReport


def save_reports_to_db(words_report: WordsReport, sentences_report: SentencesReport,
                       characters_report: CharactersReport,
                       palindrome_report: PalindromeReport, filename: str):
    reports = [words_report, sentences_report, characters_report, palindrome_report]
    cleaned_filename, _ = clean_file_lead(filename)
    cleaned_filename = path.basename(cleaned_filename)
    file_reports = FileReports(name=cleaned_filename, reports=reports)
    session.add(file_reports)
    session.commit()


def get_reports_from_db(filename: str):
    matched_reports = session.query(FileReports).filter(FileReports.name == filename)
    return matched_reports
