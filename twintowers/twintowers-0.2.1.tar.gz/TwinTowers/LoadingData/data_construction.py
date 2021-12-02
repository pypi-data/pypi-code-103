import re
import random
import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from tqdm import tqdm
from ..utils import TimeCounter


# 过滤长度过长的序列
def data_filter(path, out_path, threshold=512):
	with open(out_path, 'w') as f:
		for seq_record in tqdm(SeqIO.parse(path, "fasta")):
			if len(seq_record.seq) > threshold:
				continue
			else:
				f.write(f">{seq_record.description}\n")
				f.write(f"{str(seq_record.seq)}\n")


# SCOP2
def load_data(path):
	sf = {}
	pattern = r'SF=([\d]+)'

	# 提取文件里的所有序列，按照超家族分类
	for seq_record in SeqIO.parse(path, "fasta"):
		sf_id = re.search(pattern, seq_record.description).group(1)

		if sf_id not in sf.keys():
			sf[sf_id] = [seq_record]
		else:
			sf[sf_id].append(seq_record)

	# 去掉所有同源序列数量为1的超家族
	del_ids = []
	for sf_id, seqs in sf.items():
		if len(seqs) == 1:
			del_ids.append(sf_id)
	[sf.pop(key) for key in del_ids]

	return sf


#SCOPe v2.08
def load_scope_data(path):
	pattern = r' (.*?\d+.\d+)'
	records = SeqIO.parse(path, 'fasta')
	sf_dict = {}

	for seq in records:
		fd_id = re.search(pattern, str(seq.description)).group(1)
		seq.seq = Seq(str(seq.seq).upper())
		if fd_id not in sf_dict.keys():
			sf_dict[fd_id] = [seq]
		else:
			sf_dict[fd_id].append(seq)

	sf_dict = {k: v for k, v in sf_dict.items() if len(v) > 1}

	return sf_dict


# uniclust30_2018_08_seed
def sample_seqs(fasta_path, pointer, n, threshold):
	# total number of sequences
	total = pointer.shape[0]
	
	# sample n negative samples
	indices = [random.randint(0, total-1) for _ in range(n)]
	
	samples = []
	with open(fasta_path, 'r') as f:
		for index in indices:
			loc = pointer[index][0]
			
			# ensure length of sequence less than threshold
			while True:
				f.seek(loc)
				f.readline()
				seq = f.readline()[:-1]
				if len(seq) <= threshold:
					samples.append(seq)
					break
					
				else:
					new_index = random.randint(0, total-1)
					loc = pointer[new_index][0]
	
	return samples
			

# 对fasta文件构建指针索引
def construct_pointer(fasta_path, save_path):
	with TimeCounter("Constructing index file..."):
		with open(save_path, 'w') as w:
			w.write("location\n")
			with open(fasta_path, 'r') as r:
				loc = r.tell()
				line = r.readline()
				while line:
					if line[0] == '>':
						w.write(f'{loc}\n')

					loc = r.tell()
					line = r.readline()


# 将数据划分为训练集和测试集
def data_split(data):
	sorted_sf_dict = sorted(data.items(), key=lambda kv: (len(kv[1]), kv[0]), reverse=True)

	test_seqs = []
	test_db = []
	# 系统抽样
	for i in range(10, len(data), 10):
		key = sorted_sf_dict[i][0]
		seqs = data.pop(key)
		test_seqs.append(seqs[0])
		test_db += seqs

	return data, test_seqs, test_db


def training_construction(data):
	n_per_sf = 2000
	
	fasta_path = "/sujin/dataset/uniclust30/uniclust30_2018_08_seed.fasta"
	pointer_path = "/sujin/dataset/uniclust30/uniclust30_2018_08_seed.tsv"
	pointer = pd.read_csv(pointer_path, sep='\t').values

	with open("../Data/train_scope2.08.tsv", 'w') as f:
		f.write("ori\tpos\tneg\n")

		for records in tqdm(data.values()):
			neg_seqs = sample_seqs(fasta_path, pointer, n_per_sf, 512)
			for i in range(n_per_sf):
				ori, pos = random.sample(records, 2)
				ori_seq = str(ori.seq)
				pos_seq = str(pos.seq)
				neg_seq = neg_seqs[i]
		
				f.write(f'{ori_seq}\t{pos_seq}\t{neg_seq}\n')


def threshold_data_construction(sf):
	with open("../Data/thresold_data_scope2.07.tsv", 'w') as f:
		f.write("seq\thomo_num\n")
		for k, v in sf.items():
			for seq in v:
				f.write(f"{str(seq.seq)}\t{len(v)-1}\n")


def create_tsv(data, path):
	pattern = r' (.*?\d+.\d+)'
	seqs = []
	# 将向量的顺序与id对应起来输出为索引文件
	with open(path, 'w') as f:
		f.write("SF_ID\tSCOP_ID\n")
		for i, record in enumerate(data):
			scop_id = record.id
			sf_id = re.search(pattern, record.description).group(1)
			seqs.append(str(record.seq))

			f.write(f"{sf_id}\t{scop_id}\n")


if __name__ == '__main__':
	# 文件的位置
	path = "../Data/scope2.08_<=512.faa"
	# out_path = "../Data/scope2.08_<=512.faa"
	# data_filter(path, out_path, threshold=512)
	# 读取文件
	sf_dict = load_scope_data(path)
	# 划分训练集测试集
	train_sf, test_seqs, test_db = data_split(sf_dict)
	# 将测试集输出为fasta文件
	SeqIO.write(test_seqs, "../Data/test_scope2.08.faa", "fasta")
	SeqIO.write(test_db, "../Data/test_db_scope2.08.faa", "fasta")
	# 构建测试tsv文件
	create_tsv(test_seqs, "../Data/test_scope2.08.tsv")
	create_tsv(test_db, "../Data/test_db_scope2.08.tsv")
	# 构建训练集
	training_construction(train_sf)
	
	# fasta_path = "/sujin/dataset/uniclust30/uniclust30_2018_08_seed.fasta"
	# pointer_path = "/sujin/dataset/uniclust30/uniclust30_2018_08_seed_pointer.tsv"
	# construct_pointer(fasta_path, pointer_path)
	# negs = sample_seqs(fasta_path, pointer_path, 100)
	# print(negs)