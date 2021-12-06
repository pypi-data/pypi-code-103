import unittest

from bert2tf import Flow
from tests import Bert2TFTestCase


class MyTestCase(Bert2TFTestCase):

    def test_create_flow(self):
        Flow()

        Flow().add(use='BaseExecutor', name='a1', replicas=1, timeout_ready=600000)

    def test_build_flow_with_customize(self):
        flow = (Flow()
                .add(use='BaseExecutor',
                     name='a1',
                     replicas=10,
                     runtime_backend='thread',
                     timeout_ready=600000))

        with flow:
            pass

    def test_flow_with_rest_gateway(self):
        flow = (Flow(rest_api=True)
                .add(use='BaseExecutor',
                     name='a1',
                     replicas=1,
                     runtime_backend='thread',
                     timeout_ready=600000))

        with flow:
            pass

    @unittest.skip('just run on local machine')
    def test_build_flow_from_yaml(self):
        with Flow.load_config('yaml/flow.yml'):
            pass

    @unittest.skip('just run on local machine')
    def test_grpc_request_with_tokenizer(self):
        flow = Flow().add(use='BertTokenizer',
                          use_with={'vocab_file_path': '../resources/pre_models/roberta_wwm_ext/vocab.txt'},
                          name='tokenizer')

        with flow:
            result = flow.predict(['aaaa', '第二十八次集体学习'])
            self.assertEqual(isinstance(result, list), True)
            self.assertEqual(isinstance(result[0], list), True)
            self.assertEqual(len(result[0][0]), 4)

            result = flow.predict([['aaaa'], ['第二十八次集体学习']])
            self.assertEqual(isinstance(result, list), True)
            self.assertEqual(isinstance(result[0], list), True)
            self.assertEqual(len(result[0][0]), 4)

    @unittest.skip('just run on local machine')
    def test_grpc_request_with_model(self):
        flow = (Flow()
                .add(use='Bert',
                     use_with={'config': '../resources/pre_models/roberta_wwm_ext/bert_config.json',
                               'pretrained_weights_path': '../resources/pre_models/roberta_wwm_ext/bert_model.ckpt'},
                     name='bert',
                     on_gpu=True,
                     timeout_ready=1000000))
        with flow:
            input_ids = [[101, 5018, 753, 1282, 1061, 3613, 7415, 860, 2110, 739, 102],
                         [101, 5018, 753, 1282, 1061, 3613, 7415, 860, 2110, 739, 102]]
            attention_masks = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

            result = flow.predict([input_ids, attention_masks])
            self.assertEqual(isinstance(result, list), True)
            self.assertEqual(len(result), 2)
            self.assertEqual(isinstance(result[0], list), True)
            self.assertEqual(len(result[0][0]), 1)
            self.assertEqual(len(result[0][0][0]), 11)
            self.assertEqual(len(result[0][0][0][0]), 768)

    @unittest.skip('just run on local machine')
    def test_grpc_request_with_full_flow(self):
        flow = (Flow()
                .add(use='BertTokenizer',
                     use_with={'vocab_file_path': '../resources/pre_models/roberta_wwm_ext/vocab.txt'},
                     name='tokenizer')
                .add(use='Bert',
                     use_with={'config': '../resources/pre_models/roberta_wwm_ext/bert_config.json',
                               'pretrained_weights_path': '../resources/pre_models/roberta_wwm_ext/bert_model.ckpt'},
                     name='bert',
                     replicas=1,
                     on_gpu=True,
                     device_map=[0, 2, 3],
                     timeout_ready=1000000)
                )

        with flow:
            result = flow.predict(['aaaa', '第二十八次集体学习'])
            self.assertEqual(isinstance(result, list), True)
            self.assertEqual(len(result), 2)
            self.assertEqual(isinstance(result[0], list), True)
            self.assertEqual(len(result[0][0]), 1)
            self.assertEqual(len(result[0][0][0]), 4)
            self.assertEqual(len(result[0][0][0][0]), 768)
            self.assertEqual(len(result[1][0]), 1)
            self.assertEqual(len(result[1][0][0]), 11)
            self.assertEqual(len(result[1][0][0][0]), 768)

    @unittest.skip('just run on local machine')
    def test_flow_rest_request_predict(self):
        flow = (Flow(rest_api=True)
                .add(use='BertTokenizer',
                     use_with={'vocab_file_path': '../resources/pre_models/roberta_wwm_ext/vocab.txt'},
                     name='tokenizer',
                     runtime_backend='thread',
                     timeout_ready=1000000)
                .add(use='Bert',
                     use_with={'config': '../resources/pre_models/roberta_wwm_ext/bert_config.json',
                               'pretrained_weights_path': '../resources/pre_models/roberta_wwm_ext/bert_model.ckpt'},
                     name='bert',
                     replicas=1,
                     on_gpu=True,
                     device_map=[0, 2, 3],
                     timeout_ready=1000000)
                )

        with flow:
            import requests
            result = \
                requests.post('http://0.0.0.0:5000/webapi', json={'inputs': [['第二十八次集体学习'], ['第二十八次集体学习']]}).json()[
                    'outputs']
            self.assertEqual(isinstance(result, list), True)
            self.assertEqual(len(result), 2)
            self.assertEqual(isinstance(result[0], list), True)
            self.assertEqual(len(result[0][0]), 1)
            self.assertEqual(len(result[0][0][0]), 4)
            self.assertEqual(len(result[0][0][0][0]), 768)
            self.assertEqual(len(result[1][0]), 1)
            self.assertEqual(len(result[1][0][0]), 11)
            self.assertEqual(len(result[1][0][0][0]), 768)

    def test_close_flow(self):
        flow = (Flow().add(use='BaseExecutor',
                           name='a1',
                           runtime_backend='thread',
                           replicas=10,
                           timeout_ready=600000))

        flow.build()
        flow.close()

        flow = Flow(rest_api=True).add(use='BaseExecutor',
                                       name='a1',
                                       runtime_backend='thread',
                                       replicas=10,
                                       timeout_ready=600000)
        flow.build()
        flow.close()

    def test_build_complex_flow(self):
        flow = (Flow()
                .add(use='BaseExecutor',
                     name='a1',
                     runtime_backend='thread',
                     replicas=5)
                .add(use='BaseExecutor',
                     name='a2',
                     replicas=5,
                     runtime_backend='thread',
                     needs='gateway')
                .add(use='BaseExecutor',
                     name='a3',
                     replicas=5,
                     runtime_backend='thread',
                     needs=['a1', 'a2'])
                .add(use='BaseExecutor',
                     name='a4',
                     runtime_backend='thread',
                     replicas=5)
                .add(use='BaseExecutor',
                     name='a5',
                     runtime_backend='thread',
                     replicas=5)
                )

        with flow:
            pass
