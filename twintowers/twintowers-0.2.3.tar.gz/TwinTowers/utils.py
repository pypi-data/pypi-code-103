# 自己平常写代码时为了方便实现某些功能而写的工具函数
import pandas as pd
import torch
import os
import numpy as np
import random
import time
from tqdm import tqdm
from Bio import SeqIO


# 统计时间的函数
class TimeCounter:
    def __init__(self, text, verbose=True):
        self.text = text
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        if self.verbose:
            print(self.text, flush=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time()
        t = end - self.start
        if self.verbose:
            print(f"Finished. The time is {t:.2f}s.\n", flush=True)


# 进度条
def progress_bar(now: int, total: int, desc: str = '', end='\n'):
    length = 50
    now = now if now <= total else total
    num = now * length // total
    progress_bar = '[' + '#' * num + '_' * (length - num) + ']'
    display = f'{desc:} {progress_bar} {int(now/total*100):02d}% {now}/{total}'

    print(f'\r\033[31m{display}\033[0m', end=end, flush=True)


# 设定种子
def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


# 随机种子
def random_seed():
    torch.seed()
    torch.cuda.seed()
    np.random.seed()
    random.seed()
    torch.backends.cudnn.deterministic = False


if __name__ == '__main__':
    # file_names = [f"{i}_{i+100}" for i in range(0, 1100, 100)]
    # files = []
    # path = "/sujin/dataset/uniclust30"
    # for name in file_names:
    #     files.append(open(f"{path}/UniRef30_2020_06_{name}", 'w'))
    #
    # fasta_path = "/sujin/dataset/uniclust30/UniRef30_2020_06.faa"
    # with open(fasta_path, 'r') as r:
    #     desc = r.readline()
    #     while desc:
    #         seq = r.readline()
    #         if len(seq) - 1 > 1022:
    #             desc = r.readline()
    #             continue
    #
    #         index = int((len(seq) - 1) / 100)
    #         files[index].write(desc)
    #         files[index].write(seq)
    #
    #         desc = r.readline()
    
    a = 1
    print(a)
    