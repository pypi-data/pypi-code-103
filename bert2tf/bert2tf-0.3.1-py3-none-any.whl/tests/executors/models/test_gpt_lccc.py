import unittest

import numpy as np

from bert2tf import Executor, OpenAIGPT, GPTTokenizer
from tests import Bert2TFTestCase


class MyTestCase(Bert2TFTestCase):
    @unittest.skip('just run on local machine')
    def test_create_gpt_lccc_model(self):
        model = Executor.load_config('OpenAIGPT', use_with={
            'pretrained_weights_path': '../../resources/pre_models/GPT_LCCC-base-tf/gpt_model.ckpt',
            'config': '../../resources/pre_models/GPT_LCCC-base-tf/gpt_config.json'})
        self.assertEqual(isinstance(model, OpenAIGPT), True)

        model = Executor.load_config('yaml/gpt_lccc.yml')
        self.assertEqual(isinstance(model, OpenAIGPT), True)

        model = OpenAIGPT(config='../../resources/pre_models/GPT_LCCC-base-tf/gpt_config.json',
                          pretrained_weights_path='../../resources/pre_models/GPT_LCCC-base-tf/gpt_model.ckpt')
        self.assertEqual(isinstance(model, OpenAIGPT), True)

    @unittest.skip('just run on local machine')
    def test_openai_gpt_lccc_generate_from_random_sample(self):
        tokenizer = GPTTokenizer('../../resources/pre_models/GPT_LCCC-base-tf/vocab.txt')
        model = Executor.load_config('yaml/gpt_lccc_auto_regressive.yml')

        speakers = [
            tokenizer.vocabs['[speaker1]'],
            tokenizer.vocabs['[speaker2]']
        ]

        token_ids = [tokenizer.cls_token_id, speakers[0]]
        segment_ids = [tokenizer.cls_token_id, speakers[0]]

        texts = [u'这边是直接删除答疑']

        for idx, text in enumerate(texts):
            ids = tokenizer.encode(text)[0][1:-1] + [speakers[(idx + 1) % 2]]
            token_ids.extend(ids)
            segment_ids.extend([speakers[idx % 2]] * len(ids))
            segment_ids[-1] = speakers[(idx + 1) % 2]

        results = model.random_sample([np.array([token_ids]), np.array([segment_ids])])
        for ids in results:
            print(''.join(tokenizer.convert_ids_to_tokens(list(ids))))

    @unittest.skip('just run on local machine')
    def test_openai_gpt_lccc_generate_from_beam_search(self):
        tokenizer = GPTTokenizer('../../resources/pre_models/GPT_LCCC-base-tf/vocab.txt')
        model = Executor.load_config('yaml/gpt_lccc_auto_regressive.yml')

        speakers = [
            tokenizer.vocabs['[speaker1]'],
            tokenizer.vocabs['[speaker2]']
        ]

        token_ids = [tokenizer.cls_token_id, speakers[0]]
        segment_ids = [tokenizer.cls_token_id, speakers[0]]

        texts = [u'别爱我没结果', u'你这样会失去我的', u'失去了又能怎样']

        for idx, text in enumerate(texts):
            ids = tokenizer.encode(text)[0][1:-1] + [speakers[(idx + 1) % 2]]
            token_ids.extend(ids)
            segment_ids.extend([speakers[idx % 2]] * len(ids))
            segment_ids[-1] = speakers[(idx + 1) % 2]

        results = model.beam_search([np.array([token_ids]), np.array([segment_ids])])
        text = ''.join(tokenizer.convert_ids_to_tokens(list(results)))
        print(text)
