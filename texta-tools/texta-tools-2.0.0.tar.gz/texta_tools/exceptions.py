class MLPNotAvailableError(Exception):
    """Raised when MLP is not available."""
    pass

class MLPFailedError(Exception):
    """Raised when MLP processing fails."""
    pass

class InvalidInputError(Exception):
    """Raised when something incorrect given to trainers."""
    pass

class OutOfVocabError(Exception):
    """Raised when word not present in the vocabulary of embedding."""
    pass

class InvalidSplitMethodError(Exception):
    """Raised when TextSplitter is initiated with invalid splitting option."""
    pass
