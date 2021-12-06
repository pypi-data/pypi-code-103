import unittest

import numpy as np

from bert2tf import Executor, HuaweiGPT, HuaweiGPTTokenizer
from tests import Bert2TFTestCase


class MyTestCase(Bert2TFTestCase):
    @unittest.skip('just run on local machine')
    def test_create_huawei_gpt_model(self):
        model = Executor.load_config('HuaweiGPT', use_with={
            'pretrained_weights_path': '../../resources/pre_models/huawei-gpt/cn_gpt',
            'config': '../../resources/pre_models/huawei-gpt/cn_gpt.json'})
        self.assertEqual(isinstance(model, HuaweiGPT), True)

        model = Executor.load_config('yaml/huawei_gpt.yml')
        self.assertEqual(isinstance(model, HuaweiGPT), True)

        model = HuaweiGPT(config='../../resources/pre_models/huawei-gpt/cn_gpt.json',
                          pretrained_weights_path='../../resources/pre_models/huawei-gpt/cn_gpt')
        self.assertEqual(isinstance(model, HuaweiGPT), True)

    @unittest.skip('just run on local machine')
    def test_huawei_gpt_encode(self):
        tokenizer = HuaweiGPTTokenizer('../../resources/pre_models/huawei-gpt/vocab.txt')
        model = HuaweiGPT(config='../../resources/pre_models/huawei-gpt/cn_gpt.json',
                          pretrained_weights_path='../../resources/pre_models/huawei-gpt/cn_gpt')

        input_ids = tokenizer.encode('今天天气不错')[0][:-1]
        result = model(np.array([input_ids]))[-1].numpy()
        self.assertEqual(result.size, 5376)

    @unittest.skip('just run on local machine')
    def test_gpt_huawei_generate_from_beam_search(self):
        model = Executor.load_config('yaml/huawei_gpt_auto_regressive.yml')

        tokenizer = HuaweiGPTTokenizer('../../resources/pre_models/huawei-gpt/vocab.txt')
        input_ids = tokenizer.encode('本拉登')[0][:-1]
        all_ids = model.beam_search([np.array([input_ids])])
        text = ''.join(tokenizer.convert_ids_to_tokens(list(all_ids)))
        print(text)
