import os
import random
import multiprocessing as mp
import pandas as pd
from Bio import SeqIO
from tqdm import tqdm
from utils import setup_seed, progress_bar
from math import ceil


def building(file_list, path):
	print("building training set...")
	with open(path, 'w') as f:
		f.write("ori\tpos\tneg\n")

		for i, file in enumerate(file_list):
			sample_n = 100

			records = list(SeqIO.parse(file, 'fasta'))
			ori = str(records[0].seq)

			# 对正样本进行采样
			pos_list = records if len(records) == 1 else records[1:]
			pos_seqs = []
			for _ in range(sample_n):
				pos_seqs.append(str(random.choice(pos_list).seq).replace('-', '').upper())

			# 对负样本进行采样
			while True:
				neg_files = random.sample(file_list, sample_n)
				if file not in neg_files:
					break

			neg_seqs = []
			for file in neg_files:
				neg_records = list(SeqIO.parse(file, 'fasta'))
				sample = random.choice(neg_records)
				neg_seqs.append(str(sample.seq).replace('-', '').upper())

			for pos, neg in tuple(zip(*[pos_seqs, neg_seqs])):
				f.write(f"{ori}\t{pos}\t{neg}\n")

			progress_bar(i+1, len(file_list), path)


def mp_setup(path, n):
	print("loading data...")
	print(path)
	dirs = os.listdir(path)
	file_list = []
	for dir in tqdm(dirs):
		sub_dir = path + "/" + dir
		for file in os.listdir(sub_dir):
			file_path = sub_dir + '/' + file
			file_list.append(file_path)
	print("finished")

	# 将数据分割为多份
	num = ceil(len(file_list) / n)
	p_list = []
	for i in range(n):
		st = num * i
		ed = st + num
		path = f"../Data/PkU_training_set_{st}_{ed}.tsv"

		p = mp.Process(target=building, args=(file_list[st: ed], path))
		p.start()
		p_list.append(p)

	# 等待所有进程执行完毕
	for p in p_list:
		p.join()

	# 合并数据
	count = 0
	with open("../Data/PkU_training_set.tsv", 'w') as f:
		f.write("ori\tpos\tneg\n")

		for i in range(n):
			st = num * i
			ed = st + num
			path = f"../Data/PkU_training_set_{st}_{ed}.tsv"
			with open(path, 'r') as rf:
				for line in rf.readlines()[1:]:
					f.write(line)

			os.remove(path)


if __name__ == '__main__':
	setup_seed(2021)
	path = "../Data/PkU_training_set.tsv"
	# mp_setup(path, 100)

	data = pd.read_csv(path, sep='\t')
	tiny_data = data.sample(4000)
	print(tiny_data)
	tiny_data.to_csv("../Data/PkU_tiny_training_set.tsv", index=False, sep='\t')