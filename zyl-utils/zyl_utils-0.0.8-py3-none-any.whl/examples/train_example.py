# encoding: utf-8
'''
@author: zyl
@file: train_example.py
@time: 2021/11/11 16:14
@desc:
'''

import os

import pandas as pd

from zyl_utils.model_utils.models.my_model import MyModel


class Test(MyModel):
    def __init__(self):
        super(Test, self).__init__()
        self.start_time = '...'
        self.end_time = '...'

        self.wandb_proj = 'ttt'
        self.model_version = 'v0.0.0.0'  # to save model or best model

        self.use_model = 't5'  # t5/ mt5 /classification
        self.model_type = 't5'
        self.pretrained_model = '/large_files/pretrained_pytorch/t5-base/'  # 预训练模型位置

        self.use_cuda = True
        self.cuda_device = 0

        self.args = MyModel.set_model_parameter(model_version=self.model_version,
                                                args=self._set_args(),
                                                save_dir="/home/zyl/disk/test/")

    def run(self):
        self.train_test()

    def train_test(self):
        self.pretrained_model = '/home/zyl/disk/best_model/v4.2.0.4/'
        self.model_version = 'vtest'
        self.args = MyModel.set_model_parameter(model_version=self.model_version,
                                                args=self._set_args(), save_dir="/home/zyl/disk/test/")

        os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
        self.cuda_device = 0
        self.args.n_gpu = 2

        self.args.num_train_epochs = 1
        self.args.learning_rate = 5e-5
        self.args.train_batch_size = 16  # 512
        self.args.eval_batch_size = 32  # 256
        self.args.max_seq_length = 128
        self.args.gradient_accumulation_steps = 2  # 256

        train_df = pd.read_excel('./data/v1/train_1110.xlsx', 'train_mt5')[0:500]

        train_df.rename(columns={"therapy_labels_num": "target_text"}, inplace=True)
        train_df['prefix'] = 'classification'

        eval_df = pd.read_excel('./data/v1/train_1110.xlsx', 'eval_mt5')[0:200]

        eval_df.rename(columns={"therapy_labels_num": "target_text"}, inplace=True)
        eval_df['prefix'] = 'classification'

        self.train(train_df, eval_df)


if __name__ == '__main__':
    Test().run()
