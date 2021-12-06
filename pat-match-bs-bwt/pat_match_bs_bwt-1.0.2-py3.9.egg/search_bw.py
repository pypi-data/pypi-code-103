import argparse
import ast
import ntpath
import sys
import threading

from scripts import suffix_array
from scripts import utils

sys.setrecursionlimit(10 ** 7)  # max depth of recursion
threading.stack_size(2 ** 27)  # new thread will get stack of such size


def BWTSearch(bwt_sa, pattern, offset, fm_index):
    first = 0
    last = len(bwt_sa) - 1
    while first <= last:
        if pattern:
            char = pattern[-1]
            pattern = pattern[:-1]
            first = offset[char] + fm_index[char][first]
            last = offset[char] + fm_index[char][last + 1] - 1
        else:
            return last, first
    return None, None


def readSAFile(count, fasta_file):
    base_filename = ntpath.basename(fasta_file)
    input_filename = base_filename.split('.')[0] + "_processed.txt"
    f = open(input_filename, "r")
    lcount = 0
    sa = []
    bwt_sa = []
    first_occur = {}
    fm_index = {}
    for line in enumerate(f):
        if lcount < count:
            lcount += 1
            continue
        num = line[1]
        if lcount < count + 1:
            data = num.split('\f')
            sa = (data[1].split(' '))
            sa = sa[:-1]
            sa = list(map(int, sa))
            bwt_sa = list(data[2])
            # print(bwt_sa)
            first_occur = ast.literal_eval(data[3])
            fm_index = ast.literal_eval(data[4])
            lcount += 1
            continue
    count = lcount
    return sa, count, bwt_sa, first_occur, fm_index


def runSearchBW(fasta_file, fastq_file, out_file_name):
    fasta_seqs = utils.get_seq_from_file(fasta_file, "fasta")
    fastq_seqs = utils.get_seq_from_file(fastq_file, "fastq")
    f = open(out_file_name, 'w')
    count = 0
    for fasta_seq in fasta_seqs:
        sa = []
        sa, count, bwt_sa, first_occur, fm_index = readSAFile(count, fasta_file)
        # n = len(fasta_seq.seq)
        # print('n', n)

        for fastq_seq in fastq_seqs:
            matched_indices = []
            # m = len(fastq_seq.seq)
            # print('m', m)
            # time_start = timeit.default_timer()
            first, last = BWTSearch(bwt_sa, fastq_seq.seq, first_occur, fm_index)
            if first is not None and last != None:
                # print(first, last)
                for idx in range(last, first + 1):
                    matched_indices.append(sa[idx] + 1)
            # time_end = timeit.default_timer()
            # print(((time_end - time_start) * (10 ** 3)))
            utils.output_sam(matched_indices, fasta_seq, fastq_seq, f)


def main():
    parser = argparse.ArgumentParser(description="Matches a pattern using the BWT FM index Implementation")
    parser.add_argument(dest="fasta_file", help="fasta file")
    parser.add_argument(dest="fastq_file", help="fastq file", nargs="?")
    parser.add_argument("-p", dest="preprocess",
                        action="store_true", help="preprocess genome")
    parser.add_argument("-o", dest="out_file_name", help="output filename")
    args = parser.parse_args()

    if args.preprocess:
        suffix_array.run_sa_build(args.fasta_file, 'bw')
        return

    runSearchBW(args.fasta_file, args.fastq_file, args.out_file_name)


if __name__ == "__main__":
    main()
