import unittest

import numpy as np

from bert2tf import Executor, ElectraDiscriminator, BertTokenizer
from tests import Bert2TFTestCase


class MyTestCase(Bert2TFTestCase):
    @unittest.skip('just run on local machine')
    def test_create_electra_model(self):
        model = Executor.load_config('ElectraDiscriminator', use_with={
            'pretrained_weights_path': '../../resources/pre_models/electra-chinese-small/electra_small',
            'config': '../../resources/pre_models/electra-chinese-small/electra_small_config.json'})
        self.assertEqual(isinstance(model, ElectraDiscriminator), True)

        model = Executor.load_config('yaml/electra.yml')
        self.assertEqual(isinstance(model, ElectraDiscriminator), True)

        model = ElectraDiscriminator(
            config='../../resources/pre_models/electra-chinese-small/electra_small_config.json',
            pretrained_weights_path='../../resources/pre_models/electra-chinese-small/electra_small')
        self.assertEqual(isinstance(model, ElectraDiscriminator), True)

    @unittest.skip('just run on local machine')
    def test_electra_encode(self):
        model = ElectraDiscriminator(
            config='../../resources/pre_models/electra-chinese-small/electra_small_config.json',
            pretrained_weights_path='../../resources/pre_models/electra-chinese-small/electra_small')
        self.assertEqual(isinstance(model, ElectraDiscriminator), True)

        tokenizer = BertTokenizer('../../resources/pre_models/electra-chinese-small/vocab.txt')
        input_ids, input_mask, segment_ids = tokenizer.encode('今天天气不好')
        result = model([np.array([input_ids]), np.array([input_mask]), np.array([segment_ids])]).numpy()
        self.assertEqual(result.size, 2048)
