# encoding: utf-8
"""
@author: zyl
@file: t5.py
@time: 2021/11/29 14:46
@desc:
"""
import time

import pandas as pd
import wandb
from loguru import logger
from simpletransformers.t5 import T5Model

class NerT5:
    """
    ner model for train and eval---t5--simple-trainsformers
    """
    def __init__(self):
        self.start_time = '...'
        self.end_time = '...'
        self.describe = " use simple-transformers--t5-model"

        self.wandb_proj = 'mt5'
        self.save_dir = './'
        self.model_version = 'v0.0.0.0'  # to save model or best model
        # like a,b,c,d : a 原始数据批次，b模型方法批次，比如mt5和分类，
        # c进行模型的处理的数据批次，比如同一输入，输出是文本还是序号，d：迭代调参批次

        self.model_type = 't5'
        self.pretrained_model = 't5-base'  # 预训练模型位置 model_name

        self.use_cuda = True
        self.cuda_device = 0

        self.model_args = self.my_config()

    def my_config(self):
        return {
            'train_batch_size': 8,

            # multiprocess
            'use_multiprocessing': False,
            'use_multiprocessing_for_evaluation': False,

            # base config
            'reprocess_input_data': True,
            'use_cached_eval_features': False,
            'fp16': False,
            'manual_seed': 234,
            'gradient_accumulation_steps': 1,  # ::increase batch size,Use time for memory,

            # save
            'no_save': False,
            'save_eval_checkpoints': False,
            'save_model_every_epoch': False,
            'save_optimizer_and_scheduler': True,
            'save_steps': -1,

            # eval
            'evaluate_during_training': True,
            'evaluate_during_training_verbose': True,

            # normal
            'no_cache': False,
            'use_early_stopping': False,
            'encoding': None,
            'do_lower_case': False,
            'dynamic_quantize': False,
            'quantized_model': False,
            'silent': False,

            # save
            'overwrite_output_dir': True,
            'output_dir': self.save_dir + 'outputs/' + self.model_version + '/',
            'cache_dir': self.save_dir + 'cache/' + self.model_version + '/',
            'best_model_dir': self.save_dir + 'best_model/' + self.model_version + '/',
            'tensorboard_dir': self.save_dir + 'runs/' + self.model_version + '/' + time.strftime("%Y%m%d_%H%M%S",
                                                                                                  time.localtime()) + '/',

            # t5 args
            'use_multiprocessed_decoding': False,
            'num_beams': 1,
            'length_penalty': 2.0,
            'max_length': 20,
            'num_return_sequences': 1,
            'preprocess_inputs': True,
            'repetition_penalty': 1.0,
            'special_tokens_list': [],
            'top_k': None,
            'top_p': None,
        }

    @staticmethod
    def deal_with_df(df):
        df = df[['prefix', 'input_text', 'target_text']]
        df = df.astype('str')
        return df

    def train(self, train_data: pd.DataFrame, eval_data: pd.DataFrame):
        # deal with dt
        train_data = NerT5.deal_with_df(train_data)
        eval_data = NerT5.deal_with_df(eval_data)
        train_size = train_data.shape[0]
        eval_size = eval_data.shape[0]

        all_steps = train_size / self.model_args.get('train_batch_size')
        self.model_args.update(
            {
                'train_size': train_size,
                'eval_size': eval_size,
                'logging_steps': int(max(all_steps / 10 / self.model_args.get('gradient_accumulation_steps'), 1)),
                'evaluate_during_training_steps': int(
                    max(all_steps / 10 / self.model_args.get('gradient_accumulation_steps'), 1)),
                'wandb_project': self.wandb_proj,
                'wandb_kwargs': {
                    'name': self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                    'tags': [self.model_version, 'train']
                }
            }
        )

        model = T5Model(model_type=self.model_type, model_name=self.pretrained_model,
                        use_cuda=self.use_cuda, cuda_device=self.cuda_device, args=self.model_args)

        # train
        try:
            start_time = time.time()
            logger.info(f'start training: model_version---{self.model_version},train_size---{train_size}')
            model.train_model(train_data=train_data, eval_data=eval_data)
            logger.info('training finished!!!')
            end_time = time.time()
            logger.info(f'train time: {round(end_time - start_time, 4)} s')
        except Exception as error:
            logger.error(f'train failed!!! ERROR:{error}')
        finally:
            wandb.finish()
            # ModelUtils.remove_some_model_files(model.args)


    # def eval(self, eval_df: pd.DataFrame, use_t5_matric=False):
    #     eval_data = NerT5.deal_with_df(eval_df)
    #     eval_size = len(set(eval_df['sentence_id'].tolist()))
    #
    #     self.model_args.update(
    #         {
    #             'eval_size': eval_size,
    #             'wandb_project': self.wandb_proj,
    #             'wandb_kwargs': {
    #                 'name': self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
    #                 'tags': [self.model_version, 'eval']
    #             }
    #         }
    #     )
    #
    #     model = NERModel(model_type=self.model_type, model_name=self.model_args.get('best_model_dir'),
    #                      args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device)
    #
    #     result, model_outputs, preds_list = model.eval_model(eval_data)
    #
    #     if use_t5_matric:
    #         labels = eval_data.groupby(by=['sentence_id'], sort=False)
    #         labels = labels.apply(lambda x: x['labels'].tolist())
    #
    #         preds_list = [set(NerModel.get_entity(p)) for p in preds_list]
    #         labels = [set(NerModel.get_entity(l)) for l in labels]
    #         from zyl_utils.model_utils.ner_utils import NERUtils
    #         NERUtils.entity_recognition_v2(labels, preds_list)
    #
    #     print('1')
    #     # # wandb updata
    #     # wandb.init(
    #     #     project=self.wandb_proj,
    #     #     config = self.model_args,
    #     #     name=self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
    #     #     tags=[self.model_version, 'eval']
    #     # )
    #     # wandb.log({"f1_score": result.get('f1_score')})
    #
    # def eval_sample(self):
    #     eval_file = './test.xlsx'
    #     eval_data = pd.read_excel(eval_file)
    #
    #     self.save_dir = '../'
    #     self.model_version = 'erv4.2.0.2'
    #     self.model_type = 'bert'
    #     self.use_cuda = True
    #     self.cuda_device = 1
    #
    #     self.model_args = self.my_config()
    #     self.model_args.update(
    #         {
    #             'eval_file': eval_file,
    #             'eval_batch_size': 16,
    #             'max_seq_length': 512,
    #         }
    #     )
    #     self.eval(eval_data)

if __name__ == '__main__':
    def train_example(self):
        train_file = './test.xlsx'
        eval_file = './test.xlsx'
        train_data = pd.read_excel(train_file)
        eval_data = pd.read_excel(eval_file)

        self.wandb_proj = 't5'
        self.save_dir = './'

        self.model_version = 'erv4.2.0.2'
        self.model_type = 'mt5'
        self.pretrained_model = 'google/mt5-base'  # 预训练模型位置 model_name
        self.use_cuda = True
        self.cuda_device = 0

        self.model_args = self.my_config()
        self.model_args.update(
            {
                'train_file': train_file,
                'eval_file': eval_file,
                'num_train_epochs': 3,
                'learning_rate': 1e-3,
                'train_batch_size': 24,  # 28
                'gradient_accumulation_steps': 16,
                'eval_batch_size': 16,
                'max_seq_length': 512,
            }
        )
        self.train(train_data, eval_data)