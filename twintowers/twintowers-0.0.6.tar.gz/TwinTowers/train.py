import time

import pandas as pd
import torch.cuda
import random
import argparse
import numpy as np
import os
import torch.distributed as dist
import torch.multiprocessing as mp
from contextlib import nullcontext
from math import ceil
from torch.nn.parallel import DistributedDataParallel as DDP
from LoadingData.data_construction import load_scope_data, sample_seqs, data_split
from torch.utils.checkpoint import checkpoint
from model import MSARetrieveModel
from LoadingData.dataset import RetrieveDataset
from torch.utils.data import DataLoader
from utils import setup_seed, progress_bar, TimeCounter
from vector_construction import mp_get_vec
from torch.cuda import amp
from dynamic_sampling import dynamic_sampling

parser = argparse.ArgumentParser()
parser.add_argument("--world_size", default=4, type=int)
parser.add_argument("--local_size", default=4, type=int)
parser.add_argument("--node_rank", default=0, type=int)
parser.add_argument("--start_loc", default=0, type=int)
parser.add_argument("--total_rank", default=1, type=int)
parser.add_argument("--master_addr", default="127.0.0.1", type=str)
parser.add_argument("--master_port", default="10086", type=str)
args = parser.parse_args()


# 额外添加的loss，用于确定分类阈值并据此来训练模型
class RetrieveLoss:
    def __init__(self, pos_t, neg_t, margin):
        self.pos_t = pos_t
        self.neg_t = neg_t
        self.margin = margin

    # 考虑欧式距离的损失函数
    def __call__(self, ori, pos, neg):
        zero = torch.tensor(0, dtype=torch.double).to(ori)
        pos_dist = (ori - pos).norm(2, dim=1)
        neg_dist = (ori - neg).norm(2, dim=1)

        # 计算triplet loss
        triplet_dist = pos_dist - neg_dist + self.margin

        triplet_loss = torch.where(triplet_dist < 0, zero, triplet_dist).sum()
        # triplet_loss = triplet_loss / (triplet_dist > 0).sum().item() if triplet_loss > 0 else triplet_loss
        triplet_loss /= triplet_dist.size(0)

        # 计算distance loss
        pos_dist = pos_dist - self.pos_t
        neg_dist = self.neg_t - neg_dist

        pos_loss = torch.where(pos_dist < 0, zero, pos_dist).sum()
        neg_loss = torch.where(neg_dist < 0, zero, neg_dist).sum()

        # pos_loss = pos_loss / (pos_dist > 0).sum().item() if pos_loss > 0 else pos_loss
        # neg_loss = neg_loss / (neg_dist > 0).sum().item() if neg_loss > 0 else neg_loss
        pos_loss /= pos_dist.size(0)
        neg_loss /= neg_dist.size(0)
        dist_loss = pos_loss + neg_loss

        loss = dist_loss + triplet_loss
        return loss
    # 考虑余弦相似度的损失函数
    # def __call__(self, ori, pos, neg, t=0.5):
    #     zero = torch.tensor(0, dtype=torch.double).to(ori)
    #     value_t = t
    #     pos_dist = (ori * pos).sum(dim=1)
    #     neg_dist = (ori * neg).sum(dim=1)
    #
    #     # 计算triplet loss
    #     triplet_dist = neg_dist - pos_dist + value_t
    #
    #     triplet_loss = torch.where(triplet_dist < 0, zero, triplet_dist).sum()
    #     triplet_loss = triplet_loss / (triplet_dist > 0).sum().item() if triplet_loss > 0 else triplet_loss
    #
    #     # 计算distance loss
    #     pos_dist = value_t - pos_dist
    #     neg_dist = neg_dist - value_t
    #
    #     pos_loss = torch.where(pos_dist < 0, zero, pos_dist).sum()
    #     neg_loss = torch.where(neg_dist < 0, zero, neg_dist).sum()
    #
    #     pos_loss = pos_loss / (pos_dist > 0).sum().item() if pos_loss > 0 else pos_loss
    #     neg_loss = neg_loss / (neg_dist > 0).sum().item() if neg_loss > 0 else neg_loss
    #     dist_loss = pos_loss + neg_loss
    #
    #     loss = triplet_loss + dist_loss
    #     return loss


def train(local_rank, world_size, local_size, node_rank, model, dataset, times):
    rank = local_rank + local_size * node_rank
    # backend初始化
    dist.init_process_group("nccl",
                            init_method="tcp://{}:{}".format(args.master_addr, args.master_port),
                            rank=rank,
                            world_size=world_size)
    
    # 训练参数设置
    EPOCH = 1
    BATCH_SIZE = 1
    GRADIENT_ACCUMULATION = 32
    loss_func = RetrieveLoss(1, 1, 1)

    model.train()
    model.to(local_rank)
    model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model)

    # 使用torch混合精度训练
    scaler = amp.GradScaler()
    
    # 多机多卡调用
    model = DDP(model, device_ids=[local_rank], output_device=local_rank)
    optimizer = torch.optim.Adam(model.parameters(), lr=2e-5)

    # 加载DataLoader
    sampler = torch.utils.data.distributed.DistributedSampler(dataset)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, collate_fn=dataset.collate_fn, sampler=sampler)
    # 开始训练
    for epoch in range(EPOCH):
        cnt = 0
        ave_loss = 0
        n_iter = ceil(len(dataloader) / GRADIENT_ACCUMULATION)
        sampler.set_epoch(epoch)
        for i, data in enumerate(dataloader):
            # 在梯度累加时取消all reduce操作，加快训练速度
            context = model.no_sync if (i + 1) % GRADIENT_ACCUMULATION != 0 else nullcontext
            with context():
                with amp.autocast():
                    ori_ids = data['ori_ids'].to(local_rank)
                    pos_ids = data['pos_ids'].to(local_rank)
                    neg_ids = data['neg_ids'].to(local_rank)
    
                    ori = model(ori_ids, use_checkpoint=False)['repr']
                    pos = model(pos_ids, use_checkpoint=False)['repr']
                    neg = model(neg_ids, use_checkpoint=False)['repr']
    
                    loss = loss_func(ori, pos, neg) / GRADIENT_ACCUMULATION

                scaler.scale(loss).backward()
                ave_loss += loss.item()

                if (i + 1) % GRADIENT_ACCUMULATION == 0 or i + 1 == len(dataloader):
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad()
                    cnt += 1
                    if dist.get_rank() == 0:
                        desc = f"epoch:{epoch}  loss:{ave_loss}"
                        progress_bar(cnt, n_iter, desc)
                        ave_loss = 0

                        if cnt % 100 == 0 or cnt == n_iter:
                            batch = world_size * BATCH_SIZE * GRADIENT_ACCUMULATION
                            torch.save(model.module.state_dict(),
                                       f"PretrainedModels/RetrieveModel_scope2.08_d1_m1_t{times}_I{cnt}_B{batch}_phase3.pt")
                            

if __name__ == '__main__':
    seed = 2021
    setup_seed(seed)
    # 读取数据集
    # with TimeCounter("Loading the dataset..."):
    #     path = 'Data/train_scope2.08.tsv'
    #     dataset = RetrieveDataset(path)

    # 初始化模型
    with TimeCounter("Initializing the model..."):
        model = MSARetrieveModel()
        path = 'PretrainedModels/RetrieveModel_scope2.08_d1_m1_t12_I663_B256.pt'
        model.load_state_dict(torch.load(path, map_location='cpu'))

    with TimeCounter("Loading sample pool..."):
        # 读取文件
        path = 'Data/scope2.08.faa'
        sf_dict = load_scope_data(path)
        # 加载训练样本池
        train_sf, _, _ = data_split(sf_dict)
    
    times = 1
    while True:
        if args.node_rank == 0:
            if os.path.exists("validation.temp"):
                os.remove("validation.temp")
        
        temp_path = "temp_dataset"
        n_per_sf = 100
        neg_num = 100000
        neg_per_sample = 200
        
        # dynamically sampling training set
        with TimeCounter("Sampling training set..."):
            dynamic_sampling(args, train_sf, model, temp_path, n_per_sf, neg_num, neg_per_sample)
            
        with TimeCounter("Loading the dataset..."):
            dataset = RetrieveDataset(f"{temp_path}.tsv")
        
        # start training
        mp.spawn(train,
                 args=(args.world_size, args.local_size, args.node_rank, model, dataset, times),
                 nprocs=args.local_size,
                 join=True)

        if args.node_rank == 0:
            os.remove(f"{temp_path}.tsv")
            with open("validation.temp", 'w') as f:
                pass
        
        else:
            while True:
                if os.path.exists("validation.temp"):
                    break
                    
        times += 1
    