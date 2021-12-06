import argparse
import ntpath
import sys
import threading

from scripts import suffix_array
from scripts import utils

sys.setrecursionlimit(10 ** 7)  # max depth of recursion
threading.stack_size(2 ** 27)  # new thread will get stack of such size


def findFirst(pattern, text, sa):
    low, high = 0, len(text)
    while low < high:
        mid = int((low + high) / 2)
        # print(mid)
        if text[sa[mid]:] < pattern:
            low = mid + 1
        else:
            high = mid
    return low


def findLastImpBs(pattern, text, sa, low):
    low, high = low, len(text)
    while low < high:
        mid = int((low + high) / 2)
        if text[sa[mid]:sa[mid] + len(pattern)] <= pattern:
            low = mid + 1
        else:
            high = mid
    return low


def readSAFile(count, fasta_file):
    base_filename = ntpath.basename(fasta_file)
    input_filename = base_filename.split('.')[0] + "_processed.txt"
    f = open(input_filename, "r")
    lcount = 0
    sa = []
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
            lcount += 1
            sa = list(map(int, sa))
            continue
    count = lcount
    return sa, count


def runSearchBs(fasta_file, fastq_file, out_file_name):
    fasta_seqs = utils.get_seq_from_file(fasta_file, "fasta")
    fastq_seqs = utils.get_seq_from_file(fastq_file, "fastq")
    f = open(out_file_name, 'w')
    count = 0
    for fasta_seq in fasta_seqs:
        sa = []
        sa, count = readSAFile(count, fasta_file)
        # print(sa)
        # print(count)

        for fastq_seq in fastq_seqs:
            matched_indices = []
            first = findFirst(fastq_seq.seq, fasta_seq.seq, sa)
            if first != 0:
                last = findLastImpBs(fastq_seq.seq, fasta_seq.seq, sa, first)
                for idx in range(first, last):
                    # print('bs-search', fasta_seq.seq[sa[idx]:], sa[idx])
                    matched_indices.append(sa[idx] + 1)
            utils.output_sam(matched_indices, fasta_seq, fastq_seq, f)


def main():
    parser = argparse.ArgumentParser(description="Matches a pattern using the Binary-search implementation")
    parser.add_argument(dest="fasta_file", help="fasta file")
    parser.add_argument(dest="fastq_file", help="fastq file", nargs="?")
    parser.add_argument("-p", dest="preprocess",
                        action="store_true", help="preprocess genome")
    parser.add_argument("-o", dest="out_file_name", help="output filename")
    args = parser.parse_args()

    if args.preprocess:
        suffix_array.run_sa_build(args.fasta_file, 'bs')
        return

    runSearchBs(args.fasta_file, args.fastq_file, args.out_file_name)


if __name__ == "__main__":
    main()