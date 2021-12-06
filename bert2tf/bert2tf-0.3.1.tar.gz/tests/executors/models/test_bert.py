import unittest

import numpy as np

from bert2tf import Executor, Bert, BertTokenizer
from tests import Bert2TFTestCase


class MyTestCase(Bert2TFTestCase):
    @unittest.skip('just run on local machine')
    def test_create_bert_model(self):
        model = Executor.load_config('Bert', use_with={
            'pretrained_weights_path': '../../resources/pre_models/roberta_wwm_ext/bert_model.ckpt',
            'config': '../../resources/pre_models/roberta_wwm_ext/bert_config.json'})
        self.assertEqual(isinstance(model, Bert), True)

        model = Executor.load_config('yaml/bert.yml')
        self.assertEqual(isinstance(model, Bert), True)

        model = Bert(config='../../resources/pre_models/roberta_wwm_ext/bert_config.json',
                     pretrained_weights_path='../../resources/pre_models/roberta_wwm_ext/bert_model.ckpt')
        self.assertEqual(isinstance(model, Bert), True)

    @unittest.skip('just run on local machine')
    def test_bert_encode(self):
        model = Executor.load_config('yaml/bert.yml')

        tokenizer = BertTokenizer('../../resources/pre_models/roberta_wwm_ext/vocab.txt')
        input_ids, input_mask, segment_ids = tokenizer.encode('今天天气不好')
        result = model([np.array([input_ids]), np.array([input_mask]), np.array([segment_ids])])[-1].numpy()
        self.assertEqual(result.size, 768)
