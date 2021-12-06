import unittest

import numpy as np

from bert2tf import Executor, SoftMaskedBert, BertTokenizer
from tests import Bert2TFTestCase


class MyTestCase(Bert2TFTestCase):
    @unittest.skip('just run on local machine')
    def test_create_soft_masked_bert_model(self):
        model = Executor.load_config('SoftMaskedBert', use_with={
            'pretrained_weights_path': '../../resources/pre_models/roberta_wwm_ext/bert_model.ckpt',
            'config': '../../resources/soft_masked_bert/soft_masked_bert_config.json'})
        self.assertEqual(isinstance(model, SoftMaskedBert), True)

        model = Executor.load_config('yaml/soft_masked_bert.yml')
        self.assertEqual(isinstance(model, SoftMaskedBert), True)

        model = SoftMaskedBert(config='../../resources/soft_masked_bert/soft_masked_bert_config.json',
                               pretrained_weights_path='../../resources/pre_models/roberta_wwm_ext/bert_model.ckpt')
        self.assertEqual(isinstance(model, SoftMaskedBert), True)

    @unittest.skip('just run on local machine')
    def test_bert_encode(self):
        model = Executor.load_config('yaml/soft_masked_bert.yml')

        tokenizer = BertTokenizer('../../resources/pre_models/roberta_wwm_ext/vocab.txt')
        input_ids, input_mask, segment_ids = tokenizer.encode('今天天气不好')
        result = model([np.array([input_ids]), np.array([input_mask]), np.array([segment_ids])])
        self.assertEqual(isinstance(result, tuple), True)
        self.assertEqual(result[0].numpy().shape[0], 1)
        self.assertEqual(result[0].numpy().shape[1], 8)
        self.assertEqual(result[0].numpy().shape[2], 2)
        self.assertEqual(result[1].numpy().shape[0], 1)
        self.assertEqual(result[1].numpy().shape[1], 8)
        self.assertEqual(result[1].numpy().shape[2], 21128)
