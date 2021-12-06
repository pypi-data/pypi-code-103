import argparse
import ntpath

from scripts import utils
from scripts import gen_lcp

ans = []


def convert_to_real_cigar(simulated_cigar_str):
    n = len(simulated_cigar_str)
    res = []
    i = 0

    while i < n:
        current_alpha = simulated_cigar_str[i]
        j = i

        while j < n:
            next_alpha = simulated_cigar_str[j]

            if current_alpha != next_alpha:
                break

            j = j + 1

        res.append(f"{j - i}{current_alpha}")
        i = j

    return "".join(res)


class Node:
    def __init__(self, label_index=0, begin=0, end=0, node=None):
        self.begin = begin
        self.end = end
        self.label_index = label_index
        self.parent = node
        self.children = {}


class SuffixTree:
    def __init__(self):
        self.root = Node()

    def splitedge(self, str, sa, node, indx, start):
        newnode = Node(-1, node.begin, node.begin + indx)
        newleaf = Node(sa, start, len(str))
        node.begin = node.begin + indx
        node.parent.children[str[newnode.begin]] = newnode
        newnode.parent = node.parent
        newnode.children[str[newleaf.begin]] = newleaf
        newleaf.parent = newnode
        newnode.children[str[node.begin]] = node
        node.parent = newnode
        return newleaf

    def createSuffixtree(self, str, sa, lcp):
        leaf = Node(sa[0], sa[0], len(str), self.root)
        self.root.children[str[sa[0]]] = leaf

        for i in range(1, len(str)):
            depth = len(str) - sa[i - 1] - lcp[i]
            while depth and depth >= leaf.end - leaf.begin:
                depth = depth - (leaf.end - leaf.begin)
                leaf = leaf.parent

            if depth == 0:
                newleaf = Node(sa[i] + 1, sa[i] + lcp[i], len(str), leaf)
                leaf.children[str[newleaf.begin]] = newleaf
                newleaf.parent = leaf

            else:
                newleaf = self.splitedge(str, sa[i] + 1, leaf, leaf.end - leaf.begin - depth, sa[i] + lcp[i])

            leaf = newleaf

    def approx_search(self, node, is_beg, start, end, pattern, pattern_idx, cigar, cigar_idx, dist, s):
        if start == len(s):
            return
        if dist < 0:
            return
        if pattern_idx == len(pattern):
            self.find_matches(node, cigar)
            return
        if start == end:
            values = node.children.values()
            for val in values:
                self.approx_search(val, is_beg, val.begin, val.end, pattern, pattern_idx, cigar, cigar_idx, dist, s)
            return
        if dist == 0 and s[start] != pattern[pattern_idx]:
            return
        cost = 0
        if s[start] != pattern[pattern_idx]:
            cost = 1
        if cigar_idx < len(cigar):
            cigar[cigar_idx] = "M"
        else:
            cigar.append("M")
        self.approx_search(node, False, start + 1, end, pattern, pattern_idx + 1, cigar, cigar_idx + 1, dist - cost, s)

        if cigar_idx < len(cigar):
            cigar[cigar_idx] = "I"
        else:
            cigar.append("I")

        self.approx_search(node, False, start, end, pattern, pattern_idx + 1, cigar, cigar_idx + 1, dist - 1, s)
        if not is_beg:
            if cigar_idx < len(cigar):
                cigar[cigar_idx] = "D"
            else:
                cigar.append("D")
            self.approx_search(node, False, start + 1, end, pattern, pattern_idx, cigar, cigar_idx + 1, dist - 1, s)

    def find_matches(self, node, cigar):
        while(len(cigar)>0 and cigar[len(cigar)-1]=="D"):
            cigar.pop()
            continue
        st = convert_to_real_cigar("".join(cigar))
        if len(node.children) == 0:
            ans.append((node.label_index, st))

        values = node.children.values()
        for val in values:
            self.find_matches(val, cigar)


def readsalcpfile(count, strlen, fasta_file):
    base_filename = ntpath.basename(fasta_file)
    input_filename = base_filename.split('.')[0] + "_sa-lcp.txt"
    f = open(input_filename, "r")
    lcount = 0
    sa = []
    lcp = []
    for line in enumerate(f):
        if lcount < count:
            lcount += 1
            continue
        num = line[1]
        if lcount < count + strlen + 1:
            sa.append(int(num))
            lcount += 1
            continue
        if lcount < count + strlen * 2 + 2:
            lcp.append(int(num))
            lcount += 1
            continue
    count = lcount
    return sa, lcp, count


def run_search_st2(fasta_file, fastq_file, out_file_name, distance):
    fasta_seqs = utils.get_seq_from_file(fasta_file, "fasta")
    fastq_seqs = utils.get_seq_from_file(fastq_file, "fastq")
    f = open(out_file_name, 'w')
    cigar = []
    count = 0
    for fasta_seq in fasta_seqs:

        sa, lcp, count = readsalcpfile(count, len(fasta_seq), fasta_file)
        tree = SuffixTree()
        tree.createSuffixtree(fasta_seq + "$", sa, lcp)

        for fastq_seq in fastq_seqs:
            cigar =[]
            tree.approx_search(tree.root, True, 0, 0, fastq_seq, 0, cigar, 0, distance, fasta_seq+"$")
            utils.output_sam(ans, fasta_seq, fastq_seq, f)
            ans.clear()


def main():
    parser = argparse.ArgumentParser(description="Matches a pattern using the naive suffix-tree implementation")
    parser.add_argument(dest="fasta_file", help="fasta file")
    parser.add_argument(dest="fastq_file", help="fastq file", nargs="?")
    parser.add_argument("-p", dest="preprocess",
                        action="store_true", help="preprocess genome")
    parser.add_argument("-d", dest="distance", help="distance")
    parser.add_argument("-o", dest="out_file_name", help="output filename")
    args = parser.parse_args()

    if args.preprocess:
        gen_lcp.run_gen_lcp(args.fasta_file)
        return

    run_search_st2(args.fasta_file, args.fastq_file, args.out_file_name, int(args.distance))


if __name__ == "__main__":
    main()
