class InvalidInputError(Exception):
    """Raised when something incorrect given to trainers."""
    pass

class OutOfVocabError(Exception):
    """Raised when word not present in the vocabulary of embedding."""
    pass