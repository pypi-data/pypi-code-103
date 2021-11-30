# encoding: utf-8
"""
@author: zyl
@file: ner_model.py
@time: 2021/11/25 13:59
@desc:
"""
import time

import pandas as pd
import wandb
from loguru import logger
from simpletransformers.ner import NERModel


class NerBIO:
    """
    ner model for train and eval---bio--simple-trainsformers
    """

    def __init__(self):
        self.start_time = '...'
        self.end_time = '...'
        self.describe = " use simple-transformers--ner-model"

        self.wandb_proj = 'ner'
        self.save_dir = './'
        self.model_version = 'v0.0.0.0'  # to save model or best model
        # like a,b,c,d : a 原始数据批次，b模型方法批次，c进行模型的处理的数据批次，d：迭代调参批次

        self.model_type = 'roberta'
        self.pretrained_model = 'roberta-base'  # 预训练模型位置 model_name
        self.labels = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]

        self.use_cuda = True
        self.cuda_device = 0

        self.model_args = self.my_config()

    def my_config(self):
        return {
            'train_batch_size': 8,

            'use_multiprocessing': False,
            'use_multiprocessing_for_evaluation': False,
            # multiprocess

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

            'no_cache': False,
            'use_early_stopping': False,
            'encoding': None,
            'do_lower_case': False,
            'dynamic_quantize': False,
            'quantized_model': False,
            'silent': False,

            'overwrite_output_dir': True,
            'output_dir': self.save_dir + 'outputs/' + self.model_version + '/',
            'cache_dir': self.save_dir + 'cache/' + self.model_version + '/',
            'best_model_dir': self.save_dir + 'best_model/' + self.model_version + '/',
            'tensorboard_dir': self.save_dir + 'runs/' + self.model_version + '/' + time.strftime("%Y%m%d_%H%M%S",
                                                                                                  time.localtime()) + '/',
        }

    @staticmethod
    def deal_with_df(df: pd.DataFrame):
        df = df[["sentence_id", "words", "labels"]]
        df = df.astype({'sentence_id': 'int', 'words': 'str', 'labels': 'str'})
        return df

    def train(self, train_data: pd.DataFrame, eval_data: pd.DataFrame):
        # deal with dt
        train_data = NerBIO.deal_with_df(train_data)
        eval_data = NerBIO.deal_with_df(eval_data)
        train_size = len(set(train_data['sentence_id'].tolist()))
        eval_size = len(set(eval_data['sentence_id'].tolist()))

        # update args
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

        # get model
        model = NERModel(model_type=self.model_type, model_name=self.pretrained_model, labels=self.labels,
                         args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device)

        # train
        try:
            start_time = time.time()
            logger.info(f'start training: model_version---{self.model_version}')
            model.train_model(train_data=train_data, eval_data=eval_data)
            logger.info('training finished!!!')
            end_time = time.time()
            logger.info(f'train time: {round(end_time - start_time, 4)} s')
        except Exception as error:
            logger.error(f'train failed!!! ERROR:{error}')
        finally:
            wandb.finish()
            # ModelUtils.remove_some_model_files(model.args)

    @staticmethod
    def _get_id_entity(pred_list, label='DISEASE'):
        """
        从一个bio格式的序列中获得id实体，比如：['O', 'O', 'O', 'B-DISEASE', 'I-DISEASE', 'O', ]---->['-3-4']
        Args:
            pred_list: ['O', 'O', 'O', 'B-DISEASE', 'I-DISEASE', 'O', ]
            label: DISEASE

        Returns:
                ['-3-4']
        """
        if not label:
            label = ''
        entities = []
        e = ''
        is_entity = 0
        for index, p in enumerate(pred_list):
            if p == 'O':
                if is_entity == 1:
                    entities.append(e)
                is_entity = 0
            elif p.startswith('B-' + label):
                if is_entity == 1:
                    if e:
                        entities.append(e)
                e = '-' + str(index)
                is_entity = 1
            elif p.startswith('I-' + label):
                e = e + ('-' + str(index))
        if is_entity == 1:
            entities.append(e)
        return entities

    def eval(self, eval_df: pd.DataFrame, use_t5_metric=False):
        eval_data = NerBIO.deal_with_df(eval_df)
        eval_size = len(set(eval_df['sentence_id'].tolist()))

        self.model_args.update(
            {
                'eval_size': eval_size,
                'wandb_project': self.wandb_proj,
                'wandb_kwargs': {
                    'name': self.model_version + time.strftime("_%m%d_%H:%M:%S", time.localtime()),
                    'tags': [self.model_version, 'eval']
                }
            }
        )

        model = NERModel(model_type=self.model_type, model_name=self.model_args.get('best_model_dir'),
                         args=self.model_args, use_cuda=self.use_cuda, cuda_device=self.cuda_device)

        result, model_outputs, preds_list = model.eval_model(eval_data)

        if use_t5_metric:
            labels = eval_data.groupby(by=['sentence_id'], sort=False)
            labels = labels.apply(lambda x: x['labels'].tolist())

            preds_list = [set(NerBIO._get_id_entity(p)) for p in preds_list]
            labels = [set(NerBIO._get_id_entity(l)) for l in labels]
            from zyl_utils.model_utils.metrics.ner_metric import entity_recognition_v2
            res_df = entity_recognition_v2(labels, preds_list)
            wandb.log({"t5_res": res_df.iloc[2,-1]})

        wandb.log({"f1_score": result.get('f1_score')})

    @staticmethod
    def predict(model, to_predict):
        pass


if __name__ == '__main__':
    class Trainer(NerBIO):
        def __init__(self):
            super(Trainer, self).__init__()
            self.wandb_proj = 'panel_entity_recognition'

        def train_sample(self):
            train_file = './test.xlsx'
            eval_file = './test.xlsx'
            train_df = pd.read_excel(train_file)  # type:pd.DataFrame
            eval_df = pd.read_excel(eval_file)  # type:pd.DataFrame
            print(len(train_df))
            print(len(eval_df))
            self.save_dir = './'
            self.model_version = 'v0.0.0.0'
            self.model_type = 'bert'
            self.pretrained_model = 'bert-base-multilingual-cased'  # 预训练模型位置 model_name
            self.use_cuda = True
            self.cuda_device = 0

            self.model_args = self.my_config()
            self.model_args.update(
                {
                    'train_file': train_file,
                    'eval_file': eval_file,
                    'num_train_epochs': 3,
                    'learning_rate': 3e-4,
                    'train_batch_size': 24,  # 28
                    'gradient_accumulation_steps': 16,
                    'eval_batch_size': 16,
                    'max_seq_length': 512,
                }
            )
            self.labels = ["O", "B-DISEASE", "I-DISEASE"]
            self.train(train_df, eval_df)


    class Evaluator(NerBIO):
        def __init__(self):
            super(Evaluator, self).__init__()
            self.wandb_proj = 'panel_entity_recognition'

        def eval_sample(self):
            eval_file = './test.xlsx'
            eval_data = pd.read_excel(eval_file)

            self.save_dir = './'
            self.model_version = 'erv4.2.0.2'
            self.model_type = 'bert'
            self.use_cuda = True
            self.cuda_device = 1

            self.model_args = self.my_config()
            self.model_args.update(
                {
                    'eval_file': eval_file,
                    'eval_batch_size': 16,
                    'max_seq_length': 512,
                }
            )
            self.eval(eval_data)


    print(NerBIO._get_id_entity(['B-DISEASE', 'I-DISEASE','O','O','B-DISEASE',
                                 'B-DISEASE', 'I-DISEASE', 'B-DISEASE',]))