import torch
import pandas as pd
import numpy as np
from .tokenizer import Tokenizer
from torch.utils.data import Dataset


class RetrieveDataset(Dataset):
    def __init__(self, path):
        data = pd.read_csv(path, sep='\t')
        self.ori = data['ori'].values
        self.pos = data['pos'].values
        self.neg = data['neg'].values
        
        self.tokenizer = Tokenizer()

    def __len__(self):
        return len(self.ori)

    def __getitem__(self, index):
        return self.ori[index], self.pos[index], self.neg[index]

    def collate_fn(self, batch):
        ori, pos, neg = tuple(zip(*batch))
        # pad_id = self.tokenizer.convert_token_to_id('<pad>')

        ori_ids, ori_lengths = self.tokenizer.batch_encode(ori, padding=True).values()
        pos_ids, pos_lengths = self.tokenizer.batch_encode(pos, padding=True).values()
        neg_ids, neg_lengths = self.tokenizer.batch_encode(neg, padding=True).values()

        return {'ori_ids': ori_ids,
                'pos_ids': pos_ids,
                'neg_ids': neg_ids,
                'ori_lengths': ori_lengths,
                'pos_lengths': pos_lengths,
                'neg_lengths': neg_lengths}


class ThresholdModel(Dataset):
    def __init__(self, path):
        self.data = pd.read_csv(path, sep='\t')
        self.seqs, self.homo_num = tuple(zip(*self.data.values))
        self.tokenizer = Tokenizer()

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, index):
        seq, homo_num = self.seqs[index], self.homo_num[index]
        seq_id = self.tokenizer.single_encode(seq)
        return seq_id, homo_num

    def collate_fn(self, batch):
        seq_ids, homo_nums = tuple(zip(*batch))
        pad_id = self.tokenizer.convert_token_to_id('<pad>')

        seq_ids = torch.from_numpy(self.tokenizer.pad_sequences(seq_ids, pad_id))
        homo_nums = torch.tensor(homo_nums)

        return {'seq_ids': seq_ids,
                'homo_nums': homo_nums}

