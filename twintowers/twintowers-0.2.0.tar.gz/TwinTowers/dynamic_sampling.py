import pandas as pd
import random
import numpy as np
import os
import time
from math import ceil
from .utils import TimeCounter
from .LoadingData.data_construction import load_scope_data, sample_seqs, data_split
from .vector_construction import mp_get_vec


def remove_temp_files(args, temp_path):
    os.remove(f"{temp_path}_ori.seq")
    os.remove(f"{temp_path}_pos.seq")
    os.remove(f"{temp_path}_neg.seq")
    os.remove(f"{temp_path}_ori.seq.npy")
    os.remove(f"{temp_path}_pos.seq.npy")
    os.remove(f"{temp_path}_neg.seq.npy")
    os.remove(f"generation_done")
    
    for i in range(args.total_rank):
        ori_path = f"{temp_path}_ori.seq_{i}.npy"
        pos_path = f"{temp_path}_pos.seq_{i}.npy"
        neg_path = f"{temp_path}_neg.seq_{i}.npy"
        os.remove(ori_path)
        os.remove(pos_path)
        os.remove(neg_path)


def write_sequences(seqs, save_path):
    with open(save_path, 'w') as f:
        for seq in seqs:
            f.write(f"{seq}\n")


def load_sequences(path):
    with open(path, 'r') as f:
        return [seq[:-1] for seq in f.readlines()]


def generate_training_set(data, path, neg_num, n_per_sf):
    fasta_path = "/sujin/dataset/uniclust30/uniclust30_2018_08_seed.fasta"
    pointer_path = "/sujin/dataset/uniclust30/uniclust30_2018_08_seed_pointer.tsv"
    pointer = pd.read_csv(pointer_path, sep='\t').values
    
    # sampling negative samples
    neg_samples = sample_seqs(fasta_path, pointer, neg_num, 512)
    
    # sampling original and positive samples
    ori_seqs, pos_seqs = [], []
    for records in data.values():
        for i in range(n_per_sf):
            ori, pos = random.sample(records, 2)
            ori_seqs.append(str(ori.seq))
            pos_seqs.append(str(pos.seq))
    
    write_sequences(neg_samples, f"{path}_neg.seq")
    write_sequences(ori_seqs, f"{path}_ori.seq")
    write_sequences(pos_seqs, f"{path}_pos.seq")

    with open(f"generation_done", 'w') as f:
        pass


def calculate_vectors(args, model, temp_path):
    device_ids = list(range(args.local_size))
    seqs = load_sequences(temp_path)
 
    len_per_part = ceil(len(seqs)/args.world_size)
    data_start = len_per_part * args.start_loc
    data_end = data_start + len_per_part * args.local_size
    sub_seqs = seqs[data_start:data_end]
    
    # calculating vectors of negative samples
    save_path = f"{temp_path}_{args.node_rank}.npy"
    mp_get_vec(device_ids, model, sub_seqs, save_path=save_path, batch_size=64)
    
    # wait until all vectors calculated
    while True:
        flag = True
        for i in range(args.total_rank):
            path = f"{temp_path}_{i}.npy"
            if not os.path.exists(path):
                flag = False
                break
        
        if flag:
            break
    
    # master host merges several vectors and others wait
    if args.node_rank == 0:
        vectors = np.empty((len(seqs), model.dim), dtype=np.float32)
        pointer = 0
        for i in range(args.total_rank):
            path = f"{temp_path}_{i}.npy"
            v = np.load(path)
            vectors[pointer: pointer + v.shape[0]] = v
            pointer += v.shape[0]
    
        np.save(f"{temp_path}.npy", vectors)
    
    else:
        while True:
            if os.path.exists(f"{temp_path}.npy"):
                break


def build_training_file(args, temp_path, n_per_sf, neg_per_sample):
    if args.node_rank == 0:
        ori_seqs = load_sequences(f"{temp_path}_ori.seq")
        pos_seqs = load_sequences(f"{temp_path}_pos.seq")
        neg_seqs = load_sequences(f"{temp_path}_neg.seq")
        
        ori_vecs = np.load(f"{temp_path}_ori.seq.npy")
        pos_vecs = np.load(f"{temp_path}_pos.seq.npy")
        neg_vecs = np.load(f"{temp_path}_neg.seq.npy")
        
        # choose the negative sample with nearest distance to the original sample
        # and write results into a tsv format file
        with open(f"{temp_path}.tsv", 'w') as f:
            f.write("ori\tpos\tneg\n")
        
            for i, ori_vec in enumerate(ori_vecs):
                st = int(i / n_per_sf) * n_per_sf
                sub_pos_vecs = pos_vecs[st: st+n_per_sf]
                pos_dist = np.linalg.norm(sub_pos_vecs - ori_vec, ord=2, axis=1)
                max_loc = np.argmax(pos_dist)
                pos_seq = pos_seqs[st+max_loc]

                indices = [random.randint(0, len(neg_seqs) - 1) for _ in range(neg_per_sample)]
                sub_neg_vecs = neg_vecs[indices]
                
                dist = np.linalg.norm(sub_neg_vecs - ori_vec, ord=2, axis=1)
                min_loc = np.argmin(dist)
                if dist[min_loc] != np.inf and pos_dist[max_loc] != np.inf:
                    f.write(f"{ori_seqs[i]}\t{pos_seq}\t{neg_seqs[indices[min_loc]]}\n")
        
        # master host sends a sign indicating the work done
        with open(f"{temp_path}_0_validation", 'w') as f:
            pass
    
    else:
        while True:
            if os.path.exists(f"{temp_path}_0_validation"):
                break


def dynamic_sampling(args, data, model, temp_path, n_per_sf, neg_num, neg_per_sample):
    if not os.path.exists(f"{temp_path}.tsv"):
        # master computer generates training set
        if args.node_rank == 0:
            generate_training_set(data, temp_path, neg_num, n_per_sf)
        
        # others wait until the training set built
        else:
            while True:
                if os.path.exists(f"generation_done"):
                    break
    
        # divide training set into pieces for each host to calculate vectors
        # ori seqs
        calculate_vectors(args, model, f"{temp_path}_ori.seq")
        # pos seqs
        calculate_vectors(args, model, f"{temp_path}_pos.seq")
        # neg_seqs
        calculate_vectors(args, model, f"{temp_path}_neg.seq")
        
        # master host builds training file
        build_training_file(args, temp_path, n_per_sf, neg_per_sample)
        
        if args.node_rank == 0:
            # check if every host breaks the loop
            while True:
                flag = True
                for i in range(1, args.total_rank):
                    path = f"{temp_path}_{i}_validation"
                    if not os.path.exists(path):
                        flag = False
                        break
    
                if flag:
                    break
                
            remove_temp_files(args, temp_path)
            for i in range(args.total_rank):
                os.remove(f"{temp_path}_{i}_validation")
                
        else:
            with open(f"{temp_path}_{args.node_rank}_validation", 'w') as f:
                pass
    