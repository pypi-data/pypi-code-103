import argparse
import ntpath

from scripts import utils


def create_sa(text):
    n = len(text)
    sa = [0 for i in range(n)]
    map_sa = {}
    suffix = [0 for i in range(n)]
    sub = ''
    for i in range(n - 1, -1, -1):
        sub = text[i] + sub
        map_sa[sub] = i
        suffix[i] = sub
    suffix.sort()
    # print(suffix)
    # print(map_sa)
    j = 0
    for i in range(0, n):
        # print(key)
        sa[j] = map_sa[suffix[i]]
        j = j + 1
    # print(f"Suffix array for'{text}' is")
    # for i in range(0, n):
    #     print(sa[i], suffix[i])
    return sa


def get_fm_index(bwt_sa):
    freq = {'$': 0}
    elem = {'$'}
    for char in bwt_sa:
        freq[char] = 0
        elem.add(char)
    elem = list(elem)
    elem.sort()
    for char in bwt_sa:
        freq[char] += 1
    first_occur = {'$' : 0}
    for i in range(1, len(elem)):
        first_occur[elem[i]] = first_occur[elem[i - 1]] + freq[elem[i - 1]]
    fm_index = {}
    for e in elem:
        fm_index[e] = [0] * (len(bwt_sa) + 1)
    for i in range(len(bwt_sa)):
        add_new_ele = {bwt_sa[i]: 1}
        for e in elem:
            fm_index[e][i + 1] = fm_index[e][i] + add_new_ele.get(e, 0)
    return first_occur, fm_index


def get_bwtSA(text, sa, f):
    bwt = ''
    for i in range(0, len(text)):
        bwt = bwt + (text[sa[i] - 1])
    return bwt


def run_sa_build(fasta_file, search_file):
    fasta_seqs = utils.get_seq_from_file(fasta_file, "fasta")
    base_filename = ntpath.basename(fasta_file)
    output_filename = base_filename.split('.')[0] + "_processed.txt"

    f = open(output_filename, "w")

    for fasta_seq in fasta_seqs:
        sa = create_sa(fasta_seq.seq + "$")
        f.write('sa')
        f.write('\f')
        for element in sa:
            f.write(str(element) + " ")
        f.write("\f")
        if search_file == 'bs':
            f.write("\n")
        else:
            bwtSA = get_bwtSA(fasta_seq.seq + "$", sa, f)
            f.write(str(bwtSA))
            f.write("\f")
            first_occur, fm_index = get_fm_index(bwtSA)
            f.write(str(first_occur))
            f.write("\f")
            f.write(str(fm_index))
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Matches a pattern using the naive suffix-tree implementation")
    parser.add_argument(dest="fasta_file", help="fasta file")
    args = parser.parse_args()
    default_search = 'bs'
    run_sa_build(args.fasta_file, default_search)


if __name__ == "__main__":
    main()
