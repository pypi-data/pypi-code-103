import re
import os
import sys
import json
import unicodedata
import spacy
from spacy.lang.en.stop_words import STOP_WORDS as stopwords
from bs4 import BeautifulSoup
from textblob import TextBlob


class process_text:

    def __init__(self):
        self.__version__ = "1.0.1"
        self.nlp = spacy.load("en_core_web_sm")
        self.path = r".\\TextPreprocessing"
        self.abbreviations_path = os.path.join(self.path, 'data','abbreviations_wordlist.json')
    
    
    
    def convert_abbreviations(self, text):
        self.abbreviations = json.load(open(self.abbreviations_path))
        if type(text) == str:
            for key in self.abbreviations:
                value = self.abbreviations[key]
                raw_text = r'\b' + key + r'\b'
                text = re.sub(raw_text, value, text)
            return text
        else:
            return text
    
    def clear_duplicate_chars(self, text):
        return re.sub("(.)\\1{2,}", "\\1", text)
    
    def clear_email_id(self, text):
        return re.sub(r'([a-z0-9+._-]+@[a-z0-9+._-]+\.[a-z0-9+_-]+)',"", text)
    
    def clear_web_url(self, text):
        return re.sub(r'(http|https|ftp|ssh)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', '' , text)
    
    def clear_html_tags(self, text):
        return BeautifulSoup(text, 'lxml').get_text().strip()
    
    def clear_accented_chars(self, text):
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    
    def clear_special_chars(self, text):
        text = re.sub(r"[^\w]+", " ", text)
        text = " ".join([w for w in text.split()])
        return text
    
    def clear_binary_char(self, text):
        return re.sub(r"\brt\b", "", text).strip()

    def clear_stop_words(self, text):
        return " ".join([txt for txt in text.split() if txt not in stopwords])
    
    def correct_spelling(self, text):
        return TextBlob(text).correct()
    
    def lemetize(self, text):
        text = str(text)
        texts = []
        document = self.nlp(text)
        for token in document:
            lemma = token.lemma_
            if lemma == "-PRON-" or lemma == "be":
                lemma = token.text
            texts.append(lemma)
        return " ".join(texts)