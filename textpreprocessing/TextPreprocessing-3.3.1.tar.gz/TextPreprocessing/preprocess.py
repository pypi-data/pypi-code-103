import re
from TextPreprocessing.utility import process_text

class preprocess:
    
    def __init__(self):
        self.__version__ = "3.3.1"
        self.obj = process_text()
        self.start = 1
    
    def load_language_model(self, modal_name):
        self.obj.set_language_modal(modal_name)
    
    def set_entity_ignore_list(self, ignore_list):
        self.obj.set_entity_exclusion_list(ignore_list)

    def clean_entities(self, text):
        return self.obj.clear_generic_entity(text)
    
    def clear_email_address(self, text):
        return self.obj.clear_email_id(text)
    
    def clear_urls(self, text):
        return self.obj.clear_web_url(text)
    
    def clear_html_tag(self, text):
        return self.obj.clear_html_tags(text)
    
    def expand_abbreviations(self, text):
        return self.obj.convert_abbreviations(text)
    
    def clear_special_char(self, text):
        return self.obj.clear_special_chars(text)
    
    def clear_accented_char(self, text):
        return self.obj.clear_accented_chars(text)
    
    def clear_all_stop_words(self, text):
        return self.obj.clear_stop_words(text)
    
    def lematize_text(self, text):
        return self.obj.lemetize(text)
    
    def spell_correct(self, text):
        return self.obj.correct_spelling(text)