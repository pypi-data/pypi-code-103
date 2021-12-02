import faiss
import re
import pandas as pd
import torch
import esm
import numpy as np
from Bio import SeqIO
from math import ceil
from model import MSARetrieveModel
from vector_construction import fasta2vec
from utils import TimeCounter


# 构建Faiss索引
def contruct_faiss_index(vectors, path, dim, measure, param):
	index = faiss.index_factory(dim, param, measure)
		
	if not index.is_trained:
		index.train(vectors)
	index.add(vectors)
	
	faiss.write_index(index, path)


if __name__ == '__main__':
	
	# model_name = "esm1b_t33_650M_UR50S"
	model_name = "RetrieveModel_scope2.08_d1_m1_t62_I663_B256_phase3"
	params = {"device_ids": [0, 1, 2, 3],
	          "model_path": f"../PretrainedModels/{model_name}.pt",
	          "fasta_path": f"/sujin/dataset/uniclust30/UniRef30_2020_06_100_200",
	          "save_path": f"/sujin/dataset/uniclust30/UniRef30_2020_06_100_200",
	          "batch_size": 64,
	          "log_name": None,
	          "cover": True}
	# fasta2vec(**params)
	# file_names = ['400_500']
	# for name in file_names:
	# 	params['fasta_path'] = f"/sujin/dataset/uniclust30/UniRef30_2020_06_{name}"
	# 	params['save_path'] = f"/sujin/dataset/uniclust30/UniRef30_2020_06_{name}"
	# 	fasta2vec(**params)

	
	name = '600_700'
	path = "/sujin/dataset/uniclust30/UniRef30_2020_06"

	vectors = np.load(f"{path}_{name}.npy")
	print(vectors.shape[0])

	n = ceil(vectors.shape[0] / 256)
	dim, measure = 1280, faiss.METRIC_L2
	param = f'IVF{n}, Flat'
	save_path = f"{path}_{name}_1.index"
	with TimeCounter("Constructing index..."):
		contruct_faiss_index(vectors, save_path, dim, measure, param)