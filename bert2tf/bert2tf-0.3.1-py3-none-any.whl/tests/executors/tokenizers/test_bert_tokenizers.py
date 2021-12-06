import unittest

from tests import Bert2TFTestCase
from bert2tf import Executor, BertTokenizer


class MyTestCase(Bert2TFTestCase):
    @unittest.skip('just run on local machine')
    def test_create_bert_tokenizer(self):
        tokenizer = BertTokenizer('../../resources/pre_models/roberta_wwm_ext/vocab.txt', max_length=5)
        self.assertEqual(isinstance(tokenizer, BertTokenizer), True)

        tokenizer = Executor.load_config('yaml/bert_tokenizer.yml')
        self.assertEqual(isinstance(tokenizer, BertTokenizer), True)

    @unittest.skip('just run on local machine')
    def test_one_sents_encode(self):
        tokenizer = BertTokenizer('../../resources/pre_models/roberta_wwm_ext/vocab.txt', max_length=5)
        input_ids, input_mask, segment_ids = tokenizer.encode('就fasdfasfsfa发发发')
        self.assertEqual(len(input_ids), 5)
        self.assertEqual(len(input_mask), 5)
        self.assertEqual(len(segment_ids), 5)

        input_ids, input_mask, segment_ids = tokenizer.encode('就fasdfasfsfa发发发', '发')
        self.assertEqual(len(input_ids), 5)
        self.assertEqual(len(input_mask), 5)
        self.assertEqual(len(segment_ids), 5)
