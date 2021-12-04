#!/usr/bin/env python
# coding: utf-8
# 2292879219@qq.com
"""
Created on Mon Mar 17 17:35:12 2020

@author: xczcx
"""
import pandas as pd
import numpy as np
import time
import torch
from importlib import import_module
from sen2vec.util.utils import build_dataset_test, build_iterator
import os

"""
This module provides functions to transform sentences to vectors.
There are two ways to employ sen2vec:
1.Use the default models we provide:
    from sen2vec import sen2vec_fi, sen2vec_download
    sen2vec_download() 
    new_df = sen2vec_fi(old_df, df_title)
2.Use the self-defined models:
    from sen2vec import sen2vec
    model_config = (model_name, vec_dim, num_class, model_path)  # (set your model config)
    s = sen2vec(model_config)  # (set your model config)
    new_df = s.sen2vec_fi(old_df, df_title)
"""


class CONFIG(object):
    def __init__(self):
        self.dataset = os.path.dirname(os.path.abspath(__file__)) + "/sampled"
        self.bert_config_path = self.dataset + "/bertwwm_pretrain/model_config.txt"
        self.mcl = [x.strip().split(':') for x in open(self.bert_config_path).readlines()]
        self.mcd = {idx: tag for idx, tag in self.mcl}
        self.model_config = (self.mcd['model_name'], int(self.mcd['vec_dim']), int(self.mcd['num_class']))
        self.model_path = self.dataset + '/bertwwm_pretrain/' + self.mcd['model_name'] + '.ckpt'


class sen2vec(CONFIG):
    """
    Use the self-defined models:
        from sen2vec import sen2vec
        model_config = (model_name, vec_dim, num_class, model_path)  # (set your model config)
        s = sen2vec(model_config)  # (set your model config)
        new_df = s.sen2vec_fi(old_df, df_title)
    """

    def __init__(self, model_config=None, if_class=False):
        CONFIG.__init__(self)
        self.if_class = if_class
        if model_config is not None:
            self.model_config = model_config
            self.model_path = self.model_config[3]
        self.model_name = self.model_config[0]
        self.vec_dim = self.model_config[1]
        self.num_class = self.model_config[2]

    def sen2vec_fi(self, data, title):
        dataset = self.dataset
        model_name, vec_dim, num_class, model_path = self.model_name, self.vec_dim, self.num_class, self.model_path
        data_feature, data, len_data = data_process_(data, title)
        x = import_module('sen2vec.models.bert')
        config = x.Config(dataset, model_name, vec_dim, num_class)
        config.test_path = data_feature
        try:
            model = x.Model(config).to(config.device)
            model.load_state_dict(torch.load(model_path, 'cuda' if torch.cuda.is_available() else 'cpu'))
            exf_2, exf_3, exf_4 = sen2vec_process_(model, config, len_data)
            all_2 = pd.concat([data, exf_2], axis=1) if any(nd in model_name for nd in config.ver_list) else data.copy()
            all_2 = pd.concat([all_2, exf_3], axis=1) if self.if_class or 'cls' in model_name else all_2
            all_2 = pd.concat([all_2, exf_4], axis=1) if 'ner' in model_name else all_2
            return all_2
        except:
            return None


def sen2vec_fi(data=None, title=None, model_name=None, vec_dim=None, num_class=None, model_path=None, if_class=False):
    """
    Use the default models we provide:
        from sen2vec import sen2vec_fi
        new_df = sen2vec_fi(old_df, df_title)
    """
    dataset = os.path.dirname(os.path.abspath(__file__)) + "/sampled"
    data_feature, data, len_data = data_process_(data, title)
    x = import_module('sen2vec.models.bert')
    config = x.Config(dataset, model_name, vec_dim, num_class)
    config.test_path = data_feature
    model_path = config.save_path if model_path is None else model_path
    try:
        model = x.Model(config).to(config.device)
        model.load_state_dict(torch.load(model_path, 'cuda' if torch.cuda.is_available() else 'cpu'))
        exf_2, exf_3, exf_4 = sen2vec_process_(model, config, len_data)
        all_2 = pd.concat([data, exf_2], axis=1) if any(nd in model_name for nd in config.ver_list) else data.copy()
        all_2 = pd.concat([all_2, exf_3], axis=1) if if_class or 'cls' in model_name else all_2
        all_2 = pd.concat([all_2, exf_4], axis=1) if 'ner' in model_name else all_2
        return all_2
    except:
        return None


def sen2vec_download(model_name=None, url_path=None, save_path=None):
    """
    Download the default models we provide:
        from sen2vec import sen2vec_download
        sen2vec_download()
    """
    from sen2vec.sampled.downloader import Download_P
    dp = Download_P()
    if url_path is None and model_name is None:
        dp.download_file(dp.default_bin_name, dp.default_url, dp.default_save_dir)
        dp.download_file(dp.default_ckpt_name, dp.default_url, dp.default_save_dir)
    elif url_path is not None or model_name is not None:
        url_path = dp.default_url if url_path is None else url_path
        model_name = dp.default_ckpt_name if model_name is None else model_name
        save_path = dp.default_save_dir if save_path is None else save_path
        dp.download_file(model_name, url_path, save_path)


def data_clean_(data, title):
    data = data.dropna(subset=[title], axis=0).reset_index(drop=True)
    data[title] = data[title].apply(lambda x: x.replace('\t', ''))
    data[title] = data[title].apply(lambda x: x.strip().strip('；'))
    data[title] = data[title].apply(lambda x: None if len(x) == 0 else x)
    data = data.dropna(subset=[title], axis=0).reset_index(drop=True)
    return data


def data_process_(data, title):
    data = data_clean_(data, title)
    data_feature = []
    for i, line in enumerate(data[title]):
        for ll in line.split("；"):
            data_feature.append(ll + "\t" + str(i)) if ll != '' else None
    len_data = len(data)
    return data_feature, data, len_data


def sen2vec_process_(model, config, len_data):
    model.eval()
    test_data = build_dataset_test(config)
    test_iter = build_iterator(test_data, config)
    time_start = time.time()
    n = 0
    for text, j in test_iter:
        outputs, outputs_classes, outputs_ner = model(text)
        if j == 0 and n == 0:
            vec_dim = len(outputs[0])
            len_vecs = len(outputs_classes)
            len_vec_dims = 0
            for i in range(len_vecs):
                len_vec_dims += len(outputs_classes[i][0])
            feature_2 = [np.zeros(vec_dim) for _ in range(len_data)]
            feature_3 = [np.zeros(len_vec_dims) for _ in range(len_data)]
            feature_4 = ['' for _ in range(len_data)]
        j_index = j.cpu().data.numpy()[0]
        for i in range(len_vecs):
            if i == 0:
                outputs_1 = outputs_classes[i].cpu().data.numpy()[0]
            else:
                outputs_t = outputs_classes[i].cpu().data.numpy()[0]
                outputs_1 = np.concatenate((outputs_1, outputs_t), axis=0)
        feature_2[j_index] += outputs.cpu().data.numpy()[0]
        feature_3[j_index] += outputs_1
        feature_4[j_index] = str(outputs_ner) if feature_4[j_index] == '' else feature_4[j_index] + '；' + str(
            outputs_ner)
        n += 1
        if j_index % 100 == 0:
            print("Cycle: ", j_index, 'totally cost', time.time() - time_start)
    out2 = pd.DataFrame(feature_2)
    out3 = pd.DataFrame(feature_3)
    out4 = pd.DataFrame(feature_4, columns=['NER'])
    for i in range(len_vec_dims):
        out3.rename(columns={i: "out" + str(i)}, inplace=True)
    return out2, out3, out4
