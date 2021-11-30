from gensim.models.phrases import Phraser as GSPhraser
from gensim.models.phrases import Phrases
import logging

logging.basicConfig(
    format='%(levelname)s %(asctime)s: %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S',
    level=logging.ERROR
)

class Phraser:
    """
    Wrapper of Gensim Phraser.
    """
    def __init__(self):
        self._phraser = None

    def train(self, sentences):
        """
        Trains phraser model using input sentences.
        """
        phrase_model = Phrases(sentences)
        phraser = GSPhraser(phrase_model)
        self._phraser = phraser

    def _phrase(self, text):
        try:
            return self._phraser[text]
        except AttributeError as e:
            # when older model is used, AttributeError is caught
            # skip phrasing in that case and log error
            logging.error(f"Phrasing failed. Skipping. Error Message: {e}")
            return text

    def phrase(self, text):
        """
        Phrases input text.
        """
        if self._phraser:
            if isinstance(text, str):
                text = text.split(' ')
                return ' '.join(self._phrase(text))
            else:
                return self._phrase(text)
        else:
            return text
