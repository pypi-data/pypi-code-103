from gensim.models.phrases import Phraser as GSPhraser
from gensim.models import word2vec, fasttext, KeyedVectors
from gensim.models.phrases import Phrases
import joblib
import json

from texta_tools.text_processor import TextProcessor
from . import exceptions


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


class Embedding:
    """
    Embedding Abstraction to work with both Word2Vec & FastText.
    """
    def __init__(self, description="My Embedding", workers=1, min_freq=5, num_dimensions=100, window=5, num_epochs=5,
                 text_processor=TextProcessor(sentences=True, remove_stop_words=True, words_as_list=True)):
        self.model = None
        self.phraser = None
        self.description = description
        # params
        self.workers = workers
        self.min_freq = min_freq
        self.window = window
        self.num_epochs = num_epochs
        self.num_dimensions = num_dimensions
        self.text_processor = text_processor

    def _train(self, texts, selected_model, use_phraser):
        """
        Trains Embedding.
        This needs to be called out in train() method of the model implementation (e.g. W2V).
        :param: list texts: List of texts or an iterator (e.g. Elasticsearcher).
        """
        if not texts:
            raise exceptions.InvalidInputError("No training texts provided.")
        # add texts to text processor so we can use it as an iterator
        self.text_processor.input_texts = texts
        # build phraser if asked
        if use_phraser == True:
            phraser = Phraser()
            phraser.train(self.text_processor)
            # set phraser
            self.phraser = phraser
            # update phraser in text processor
            self.text_processor.phraser = phraser

        # word2vec model
        model = selected_model(
            self.text_processor,
            min_count=self.min_freq,
            vector_size=self.num_dimensions,
            epochs=int(self.num_epochs),
            window=self.window,
            workers=self.workers
        )
        self.model = model
        return True

    def save(self, file_path):
        """
        Saves embedding with phraser to disk.
        """
        to_dump = {"phraser": self.phraser, "embedding": self.model}
        joblib.dump(to_dump, file_path)
        return True

    def load(self, file_path):
        """
        Loads embedding with phraser from disk.
        """
        to_load = joblib.load(file_path)
        self.model = to_load["embedding"]
        self.phraser = to_load["phraser"]
        return True

    def load_django(self, embedding_object):
        """
        Loads embedding in Django.
        """
        file_path = embedding_object.embedding_model.path
        to_load = joblib.load(file_path)
        self.model = to_load["embedding"]
        self.phraser = to_load["phraser"]
        self.description = embedding_object.description
        return True

    def get_vector(self, word):
        """
        Returns vector for given embedding entry.
        """
        if word not in self.model.wv.index_to_key:
            raise exceptions.OutOfVocabError("Word or phrase not in vocabulary.")
        return self.model.wv.__getitem__(word)

    def get_vectors(self):
        """
        Returns Vectors as a Matrix.
        """
        return self.model.wv.vectors

    def get_vocabulary(self):
        """
        Returns embedding vocabulary (dict) from KeyedVectors.
        """
        return self.model.wv.key_to_index

    @staticmethod
    def _format_str(string):
        return str(string).replace(' ', '_')

    def get_similar(self, positives_used, negatives_used=list(), positives_unused=list(), negatives_unused=list(), n=20):
        """
        Find similar words & phraser for input list of strings.
        """
        # check if all inputs are strings
        for input_list in (positives_used, negatives_used, positives_unused, negatives_unused):
            if not isinstance(input_list, list):
                raise exceptions.InvalidInputError("Input must be list!")
        # reformat positives & negatives
        # get vocab:
        vocab = self.get_vocabulary()
        # filter out words not present in the embedding vocabulary
        positives = [self._format_str(positive) for positive in positives_used if self._format_str(positive) in vocab]
        negatives = [self._format_str(negative) for negative in negatives_used if self._format_str(negative) in vocab]
        # create set of the tokens we don't want to see in the output
        neg_pos_combined = negatives_used + positives_unused + negatives_unused
        not_suggestions = [self._format_str(not_suggestion) for not_suggestion in neg_pos_combined if self._format_str(not_suggestion) in self.model.wv.vocab]
        not_suggestions = set(not_suggestions)
        # return logic
        if positives:
            similar_items = self.model.wv.most_similar(positive=positives, negative=negatives, topn=n+len(not_suggestions))
            similar_items_topn = list()
            for i,s in enumerate(similar_items):
                if s[0] not in not_suggestions:
                    similar_items_topn += [{'phrase': s[0].replace('_', ' '), 'score': s[1], 'model': self.description}]
                if i == n:
                    break
            return similar_items_topn
        else:
            return []


    def get_similarity(self, s1: str, s2: str):
        """ Get similarity of the input words / phrases.
        """
        s1 =  self._format_str(s1)
        s2 =  self._format_str(s2)
        return self.model.wv.similarity(s1, s2)


class FastTextEmbedding(Embedding):
    """
    This is an actual embedding class you want to use!
    """
    def train(self, texts, use_phraser=True):
        """
        Trains FastText embedding.
        :param: list texts: List of texts or an iterator (e.g. Elasticsearcher).
        """
        return self._train(texts, fasttext.FastText, use_phraser=use_phraser)


class W2VEmbedding(Embedding):
    """
    This is an actual embedding class you want to use!
    """
    def train(self, texts, use_phraser=True):
        """
        Trains Word2Vec embedding.
        :param: list texts: List of texts or an iterator (e.g. Elasticsearcher).
        """
        return self._train(texts, word2vec.Word2Vec, use_phraser=use_phraser)
