from typing import List

from .helper import convert_to_unicode
from bert2tf.executors import BaseExecutor


class BaseTokenizer(BaseExecutor):
    """Base Tokenizer"""

    def __init__(self, vocab_file_path, unk='[UNK]'):
        super(BaseTokenizer, self).__init__()

        self.vocab_file_path = vocab_file_path
        self.vocabs = load_vocab(self.vocab_file_path)
        self.inv_vocabs = {v: k for k, v in self.vocabs.items()}

        self.unk = unk
        self.unk_id = self.vocabs[unk]

    def tokenize(self, text):
        """tokenize text to pieces of word"""
        raise NotImplementedError

    def encode(self, *args, **kwargs):
        """encode tokens to ids by using vocab"""

    def convert_tokens_to_ids(self, tokens: List[str]) -> List[int]:
        return [self.vocabs[token] if token in self.vocabs else self.unk_id for token in tokens]

    def convert_ids_to_tokens(self, ids: List[int]) -> List[str]:
        return [self.inv_vocabs[idx] if idx in self.inv_vocabs else self.unk for idx in ids]


def load_vocab(vocab_file_path):
    import collections
    vocabs = collections.OrderedDict()
    index = 0
    with open(vocab_file_path, 'r', encoding='utf-8') as reader:
        while True:
            token = convert_to_unicode(reader.readline())
            if not token:
                break
            token = token.strip()
            vocabs[token] = index
            index += 1
    return vocabs
