import pandas as pd
import os
import numpy as np
import platform
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from ..utils import TimeCounter

abs_path = os.path.dirname(os.path.dirname(__file__))
# use different commands for windows and linux respectively
system = platform.system().lower()
if system == 'linux':
    rm = 'rm {}'
    mv = 'mv {} {}'
    align_tool = f"{abs_path}/software/linux_famsa"
    command = align_tool + " {} {} >/dev/null 2>&1"

elif system == 'windows':
    rm = 'del {}'
    mv = 'move {} >nul 2>nul'
    align_tool = f"{abs_path}\\software\\windows_famsa.exe"
    command = align_tool + " {} {} >nul 2>nul"


def fasta2a3m(id, path):
    records = SeqIO.parse(path, "fasta")
    gap_id = ord('-')
    letter_gap = ord('A') - ord('a')
    
    for record in SeqIO.parse(path, "fasta"):
        if record.id == id:
            query_record = record
            seq = bytes(query_record.seq)
            seq_ids = np.array([id for id in seq])
            info = query_record.description
            # 查询序列中有'-'的位置
            ori_gaps = seq_ids == gap_id
            seq = ''.join(chr(id) for id in seq_ids[~ori_gaps])
    
    with open(f'{path}.a3m', 'w') as f:
        f.write(f'>{info}\n{seq}\n')
        for record in records:
            if record.id == query_record.id:
                continue
            
            seq = bytes(record.seq)
            info = record.description
            seq_ids = np.array([id for id in seq])
            
            # 同源序列中有'-'的位置
            seq_gaps = seq_ids == gap_id
            
            seq_ids[ori_gaps] = seq_ids[ori_gaps] - letter_gap
            
            mask = seq_gaps & ori_gaps
            seq = ''.join(chr(id) for id in seq_ids[~mask])
            
            f.write(f'>{info}\n{seq}\n')
    
    os.system(mv.format(f"{path}.a3m", path))


def build_msa(fasta_path, out_path, id, fmt='a3m'):
    os.system(command.format(fasta_path, out_path))
    if fmt == 'a3m':
        fasta2a3m(id, out_path)


def tsv_to_msa(tsv_path, output, align=True, fmt='a3m'):
    data = pd.read_csv(tsv_path, sep='\t')
    
    with TimeCounter('Generating files...'):
        for i, item in enumerate(data.groupby("query_id").indices.items()):
            query_id, indices = item
            info = data.iloc[indices].values
            
            out_name = f"{output}/query_{i}.faa" if output else f"query_{i}.faa"
            with open(out_name, 'w') as f:
                query_description, query_seq = info[0][1], info[0][4]
                f.write(f">{query_description}\n{query_seq}\n")
                
                for target in info:
                    f.write(f">{target[3]}\n{target[5]}\n")
            
            if align:
                build_msa(f"{out_name}", f"{out_name}_aligned", query_id, fmt=fmt)
                
                if fmt == 'a3m':
                    os.system(mv.format(f"{out_name}_aligned", f"{out_name[:-4]}.a3m"))
                    os.system(rm.format(out_name))
                elif fmt == 'fasta':
                    os.system(mv.format(f"{out_name}_aligned", out_name[:-4]))


def parse_tsv(tsv_path):
    data = pd.read_csv(tsv_path, sep='\t')
    
    for i, item in enumerate(data.groupby("query_id").indices.items()):
        query_id, indices = item
        info = data.iloc[indices].values
        
        query_description, query_seq = info[0][1], info[0][4]
        
        print(f"no.{i + 1}\nquery id: {query_id}")
        print(f"description: {query_description}")
        print(f"sequence length: {len(query_seq)}\n")
        
        print("detected sequences:")
        print(f"number:{len(info)}")
        print(f"{'target id':<40}{'length':<10}{'distance':<10}{'description':^50}")
        for target in info:
            hit_len = len(target[-2])
            hit_id = target[2]
            hit_description = target[3]
            distance = target[-1]
            print(f"{hit_id:<40}{hit_len:<10}{distance:.4f}\t{hit_description:<50}")
        
        print("*" * 100 + '\n\n')


def write_to_tsv(q_info_path, db_pointer_path, db_path, out_path, homo_list, dist_list):
    pointer = pd.read_csv(db_pointer_path, sep='\t')
    homo_dict = {}
    with open(db_path, 'r') as r:
        for homo in homo_list:
            for index in homo:
                if index not in homo_dict.keys():
                    loc = pointer.iloc[index][0]
                    r.seek(loc)
                    desc = r.readline()[1:-1]
                    id = desc.split(' ', maxsplit=1)[0]
                    seq = r.readline()[:-1]
                    homo_dict[index] = (id, desc, seq)
    
    # 输出查询结果
    with open(out_path, 'w') as f:
        f.write(f"query_id\tquery_description\ttarget_id\ttarget_description\tquery_seq\ttarget_seq\tdistance\n")
        q_info = pd.read_csv(q_info_path, sep='\t')
        for i, record in enumerate(q_info.values):
            query_id, query_description, query_seq = record
            
            if len(homo_list[i]) == 0:
                continue
            
            for j, index in enumerate(homo_list[i]):
                target_id, target_description, target_seq = homo_dict[index]
                if j != 0:
                    query_seq = ""
                f.write(f"{query_id}\t{query_description}\t{target_id}\t"
                        f"{target_description}\t{query_seq}\t{target_seq}\t{dist_list[i][j]}\n")


if __name__ == '__main__':
    path = 'UniRef30_2020_06_900_1000_index.tsv'
    parse_tsv(path)