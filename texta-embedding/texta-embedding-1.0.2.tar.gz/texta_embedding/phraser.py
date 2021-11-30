from gensim.models.phrases import Phraser as GSPhraser
from gensim.models.phrases import Phrases

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

    def phrase(self, text):
        """
        Phrases input text.
        """
        if self._phraser:
            if isinstance(text, str):
                text = text.split(' ')
                return ' '.join(self._phraser[text])
            else:
                return self._phraser[text]
        else:
            return text
