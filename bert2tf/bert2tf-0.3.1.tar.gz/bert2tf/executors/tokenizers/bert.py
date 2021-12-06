import collections
from typing import Tuple, List

from . import BaseTokenizer
from .helper import convert_to_unicode, whitespace_tokenize, is_punctuation, is_whitespace, is_control


class BasicTokenizer:
    """Runs basic tokenization (punctuation splitting, lower casing, etc.)."""

    def __init__(self, do_lower_case: bool = True):
        """Constructs a BasicTokenizer.

        Args:
          do_lower_case: Whether to lower case the input.
        """
        self.do_lower_case = do_lower_case

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes a piece of text."""
        text = convert_to_unicode(text)
        text = self._clean_text(text)

        # This was added on November 1st, 2018 for the multilingual and Chinese
        # models. This is also applied to the English models now, but it doesn't
        # matter since the English models were not trained on any Chinese data
        # and generally don't have any Chinese data in them (there are Chinese
        # characters in the vocabulary because Wikipedia does have some Chinese
        # words in the English Wikipedia.).
        text = self._tokenize_chinese_chars(text)

        orig_tokens = whitespace_tokenize(text)
        split_tokens = []
        for token in orig_tokens:
            if self.do_lower_case:
                token = token.lower()
                token = self._run_strip_accents(token)
            split_tokens.extend(self._run_split_on_punc(token))

        output_tokens = whitespace_tokenize(' '.join(split_tokens))
        return output_tokens

    def _run_strip_accents(self, text):
        import unicodedata
        """Strips accents from a piece of text."""
        text = unicodedata.normalize('NFD', text)
        output = []
        for char in text:
            cat = unicodedata.category(char)
            if cat == 'Mn':
                continue
            output.append(char)
        return ''.join(output)

    def _run_split_on_punc(self, text):
        """Splits punctuation on a piece of text."""
        chars = list(text)
        i = 0
        start_new_word = True
        output = []
        while i < len(chars):
            char = chars[i]
            if is_punctuation(char):
                output.append([char])
                start_new_word = True
            else:
                if start_new_word:
                    output.append([])
                start_new_word = False
                output[-1].append(char)
            i += 1

        return [''.join(x) for x in output]

    def _tokenize_chinese_chars(self, text):
        """Adds whitespace around any CJK character."""
        output = []
        for char in text:
            cp = ord(char)
            if self._is_chinese_char(cp):
                output.append(' ')
                output.append(char)
                output.append(' ')
            else:
                output.append(char)
        return ''.join(output)

    def _is_chinese_char(self, cp):
        """Checks whether CP is the codepoint of a CJK character."""
        # This defines a "chinese character" as anything in the CJK Unicode block:
        #   https://en.wikipedia.org/wiki/CJK_Unified_Ideographs_(Unicode_block)
        #
        # Note that the CJK Unicode block is NOT all Japanese and Korean characters,
        # despite its name. The modern Korean Hangul alphabet is a different block,
        # as is Japanese Hiragana and Katakana. Those alphabets are used to write
        # space-separated words, so they are not treated specially and handled
        # like the all of the other languages.
        if ((cp >= 0x4E00 and cp <= 0x9FFF) or  #
                (cp >= 0x3400 and cp <= 0x4DBF) or  #
                (cp >= 0x20000 and cp <= 0x2A6DF) or  #
                (cp >= 0x2A700 and cp <= 0x2B73F) or  #
                (cp >= 0x2B740 and cp <= 0x2B81F) or  #
                (cp >= 0x2B820 and cp <= 0x2CEAF) or
                (cp >= 0xF900 and cp <= 0xFAFF) or  #
                (cp >= 0x2F800 and cp <= 0x2FA1F)):  #
            return True

        return False

    def _clean_text(self, text):
        """Performs invalid character removal and whitespace cleanup on text."""
        output = []
        for char in text:
            cp = ord(char)
            if cp == 0 or cp == 0xfffd or is_control(char):
                continue
            if is_whitespace(char):
                output.append(' ')
            else:
                output.append(char)
        return ''.join(output)


class WordpieceTokenizer(BaseTokenizer):
    """Runs WordPiece tokenziation."""

    def __init__(self, vocab_file_path: str, unk_token: str = '[UNK]', max_input_chars_per_word: int = 200):
        super().__init__(vocab_file_path)
        self.unk_token = unk_token
        self.max_input_chars_per_word = max_input_chars_per_word

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes a piece of text into its word pieces.

        This uses a greedy longest-match-first algorithm to perform tokenization
        using the given vocabulary.

        For example:
          input = "unaffable"
          output = ["un", "##aff", "##able"]

        Args:
          text: A single token or whitespace separated tokens. This should have
            already been passed through `BasicTokenizer.

        Returns:
          A list of wordpiece tokens.
        """

        text = convert_to_unicode(text)

        output_tokens = []
        for token in whitespace_tokenize(text):
            chars = list(token)
            if len(chars) > self.max_input_chars_per_word:
                output_tokens.append(self.unk_token)
                continue

            is_bad = False
            start = 0
            sub_tokens = []
            while start < len(chars):
                end = len(chars)
                cur_substr = None
                while start < end:
                    substr = ''.join(chars[start:end])
                    if start > 0:
                        substr = '##' + substr
                    if substr in self.vocabs:
                        cur_substr = substr
                        break
                    end -= 1
                if cur_substr is None:
                    is_bad = True
                    break
                sub_tokens.append(cur_substr)
                start = end

            if is_bad:
                output_tokens.append(self.unk_token)
            else:
                output_tokens.extend(sub_tokens)
        return output_tokens


class BertTokenizer(WordpieceTokenizer):
    """Bert tokenizer"""

    def __init__(self, vocab_file_path: str, do_lower_case: bool = True, cls_token: str = '[CLS]',
                 sep_token: str = '[SEP]', pad_token: str = '[PAD]'):

        super(BertTokenizer, self).__init__(vocab_file_path=vocab_file_path)
        self.basic_tokenizer = BasicTokenizer(do_lower_case=do_lower_case)

        self.cls_token = cls_token
        self.sep_token = sep_token
        self.pad_token = pad_token

    def tokenize(self, text: str) -> List[str]:
        # 1. split words to word piece
        # 2. split word piece to bert style word piece
        # for example
        # input = "unaffable"
        # output = ["un", "##aff", "##able"]
        split_tokens = []
        for token in self.basic_tokenizer.tokenize(text):
            for sub_token in super().tokenize(token):
                split_tokens.append(sub_token)

        return split_tokens

    def encode(self, text1: str, text2: str = None, max_length: int = None, padding=False) -> Tuple[
        List[int], List[int], List[int]]:
        if text2:
            tokens, input_masks, segment_ids = self._encode_double(text1, text2, max_length)
        else:
            tokens, input_masks, segment_ids = self._encode_single(text1, max_length)

        while padding and max_length and len(tokens) < max_length:
            tokens.append(self.pad_token)
            input_masks.append(0)
            segment_ids.append(0)

        input_ids = self.convert_tokens_to_ids(tokens)

        return input_ids, input_masks, segment_ids

    def _encode_single(self, text, max_length=None):
        if max_length and max_length < 3:
            raise ValueError('if you want to set max length for encoding one sentence, '
                             'you must set max length greater than 2')
        tokens = self.tokenize(text)

        if max_length and len(tokens) > max_length - 2:
            tokens = tokens[:max_length - 2]

        tokens = [self.cls_token] + tokens + [self.sep_token]
        input_masks = [1] * len(tokens)
        segment_ids = [0] * len(tokens)

        return tokens, input_masks, segment_ids

    def _encode_double(self, text1, text2, max_length=None):
        if max_length and max_length < 5:
            raise ValueError('if you want to set max length for encoding two sentences, '
                             'you must set max length greater than 4')
        tokens1 = self.tokenize(text1)
        tokens2 = self.tokenize(text2)

        while max_length and len(tokens1) + len(tokens2) > max_length - 3:
            tokens1 = tokens1[:-1]
            if len(tokens1) + len(tokens2) > max_length - 3:
                tokens2 = tokens2[:-1]

        tokens = [self.cls_token] + tokens1 + [self.sep_token]
        segment_ids = [0] * (len(tokens))

        tokens = tokens + tokens2 + [self.sep_token]
        segment_ids = segment_ids + [1] * (len(tokens) - len(segment_ids))

        input_masks = [1] * len(tokens)
        return tokens, input_masks, segment_ids

    @property
    def cls_token_id(self):
        return self.vocabs[self.cls_token]

    @property
    def pad_token_id(self):
        return self.vocabs[self.pad_token]

    @property
    def seq_token_id(self):
        return self.vocabs[self.sep_token]


# todo need perfect
class BertMRCTokenizer(BertTokenizer):
    def encode(self, question, content, answer_span, training=False, doc_stride=64, maxlen=None):
        if maxlen is not None:
            if maxlen < 5:
                raise ValueError('if you want to set max length for encoding machine comprehension token, '
                                 'you must set max length greater than 4')
            elif maxlen < 3 + len(answer_span):
                self.logger.warning('please set big max length, your max length is small than answer span length. '
                                    'now it will uses first word of answer span as answer span')
                question_tokens = self.tokenize(question)[:1]

            else:
                question_tokens = self.tokenize(question)

            max_content_len = maxlen - len(question_tokens) - 3
        else:
            max_content_len = None
            question_tokens = self.tokenize(question)

        _Input = collections.namedtuple('Input',
                                        ['input_ids', 'segment_ids', 'input_masks', 'start_position', 'end_position',
                                         'token_to_orig_map', 'token_is_max_context'])
        tok_to_orig_index = []
        orig_to_tok_index = []
        all_doc_tokens = []
        for (i, token) in enumerate(content):
            orig_to_tok_index.append(len(all_doc_tokens))
            sub_tokens = self.tokenize(token)
            for sub_token in sub_tokens:
                tok_to_orig_index.append(i)
                all_doc_tokens.append(sub_token)

        if training and answer_span:
            start = content.index(answer_span)
            end = start + len(answer_span) - 1
            tok_start_position = orig_to_tok_index[start]
            if end < len(content) - 1:
                tok_end_position = orig_to_tok_index[end + 1] - 1
            else:
                tok_end_position = len(all_doc_tokens) - 1
            tok_start_position, tok_end_position = self._improve_answer_span(
                all_doc_tokens, tok_start_position, tok_end_position, answer_span)

        else:
            tok_start_position = -1
            tok_end_position = -1

        _DocSpan = collections.namedtuple('DocSpan', ['start', 'length'])

        doc_spans = []
        start_offset = 0

        while start_offset < len(all_doc_tokens):  # slice
            length = len(all_doc_tokens) - start_offset
            if max_content_len is not None and length > max_content_len:
                length = max_content_len
            doc_spans.append(_DocSpan(start=start_offset, length=length))
            if start_offset + length == len(all_doc_tokens):
                break
            start_offset += min(length, doc_stride)

        inputs = []
        for doc_span_index, doc_span in enumerate(doc_spans):
            tokens = []
            token_to_orig_map = {}
            token_is_max_context = {}
            segment_ids = []
            tokens.append(self.cls_token)
            segment_ids.append(0)
            for token in question_tokens:
                tokens.append(token)
                segment_ids.append(0)
            tokens.append(self.sep_token)
            segment_ids.append(0)

            for i in range(doc_span.length):
                split_token_index = doc_span.start + i
                token_to_orig_map[len(tokens)] = tok_to_orig_index[split_token_index]

                is_max_context = _check_is_max_context(doc_spans, doc_span_index,
                                                       split_token_index)
                token_is_max_context[len(tokens)] = is_max_context
                tokens.append(all_doc_tokens[split_token_index])
                segment_ids.append(1)

            tokens.append(self.sep_token)
            segment_ids.append(1)

            input_ids = self.convert_tokens_to_ids(tokens)
            input_masks = [1] * len(input_ids)
            while maxlen is not None and len(input_ids) < maxlen:
                input_ids.append(0)
                input_masks.append(0)
                segment_ids.append(0)

            if training and answer_span:
                # For training, if our document chunk does not contain an annotation
                # we throw it out, since there is nothing to predict.
                doc_start = doc_span.start
                doc_end = doc_span.start + doc_span.length - 1
                if not (tok_start_position >= doc_start and tok_end_position <= doc_end):
                    start_position = 0
                    end_position = 0
                else:
                    doc_offset = len(question_tokens) + 2
                    start_position = tok_start_position - doc_start + doc_offset  # [CLS] question [SEP]
                    end_position = tok_end_position - doc_start + doc_offset

            else:
                start_position = 0
                end_position = 0

            inputs.append(_Input(input_ids=input_ids, segment_ids=segment_ids,
                                 input_masks=input_masks, start_position=start_position,
                                 end_position=end_position, token_to_orig_map=token_to_orig_map,
                                 token_is_max_context=token_is_max_context))

        return inputs

    def _improve_answer_span(self, all_doc_tokens, start, end, answer_span):
        """Returns tokenized answer spans that better match the annotated answer."""

        # The SQuAD annotations are character based. We first project them to
        # whitespace-tokenized words. But then after WordPiece tokenization, we can
        # often find a "better match". For example:
        #
        #   Question: What year was John Smith born?
        #   Context: The leader was John Smith (1895-1943).
        #   Answer: 1895
        #
        # The original whitespace-tokenized answer will be "(1895-1943).". However
        # after tokenization, our tokens will be "( 1895 - 1943 ) .". So we can match
        # the exact answer, 1895.
        #
        # However, this is not always possible. Consider the following:
        #
        #   Question: What country is the top exporter of electornics?
        #   Context: The Japanese electronics industry is the lagest in the world.
        #   Answer: Japan
        #
        # In this case, the annotator chose "Japan" as a character sub-span of
        # the word "Japanese". Since our WordPiece tokenizer does not split
        # "Japanese", we just use "Japanese" as the annotation. This is fairly rare
        # in SQuAD, but does happen.
        tok_answer_text = ' '.join(self.tokenize(answer_span))

        for new_start in range(start, end + 1):
            for new_end in range(end, new_start - 1, -1):
                text_span = ' '.join(all_doc_tokens[new_start:(new_end + 1)])
                if text_span == tok_answer_text:
                    return new_start, new_end

        return start, end


def _check_is_max_context(doc_spans, cur_span_index, position):
    """Check if this is the 'max context' doc span for the token."""

    # Because of the sliding window approach taken to scoring documents, a single
    # token can appear in multiple documents. E.g.
    #  Doc: the man went to the store and bought a gallon of milk
    #  Span A: the man went to the
    #  Span B: to the store and bought
    #  Span C: and bought a gallon of
    #  ...
    #
    # Now the word 'bought' will have two scores from spans B and C. We only
    # want to consider the score with "maximum context", which we define as
    # the *minimum* of its left and right context (the *sum* of left and
    # right context will always be the same, of course).
    #
    # In the example the maximum context for 'bought' would be span C since
    # it has 1 left context and 3 right context, while span B has 4 left context
    # and 0 right context.
    best_score = None
    best_span_index = None
    for (span_index, doc_span) in enumerate(doc_spans):
        end = doc_span.start + doc_span.length - 1
        if position < doc_span.start:
            continue
        if position > end:
            continue
        num_left_context = position - doc_span.start
        num_right_context = end - position
        score = min(num_left_context, num_right_context) + 0.01 * doc_span.length
        if best_score is None or score > best_score:
            best_score = score
            best_span_index = span_index

    return cur_span_index == best_span_index
