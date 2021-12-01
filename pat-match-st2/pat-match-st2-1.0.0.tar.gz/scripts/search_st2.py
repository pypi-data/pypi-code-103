import argparse
import ntpath

from scripts import utils
from scripts import gen_lcp


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

    def find(self, pattern, s):
        curr_node = self.root
        i = 0

        while i < len(pattern):
            curr_c = pattern[i]

            if curr_c not in curr_node.children:
                return None, None

            child = curr_node.children[pattern[i]]
            begIndex = child.begin
            endIndex = child.end
            j = i + 1

            while j - i < (endIndex - begIndex) and j < len(pattern) and begIndex + j - i < len(s) and pattern[j] == s[
                begIndex + j - i]:
                j += 1

            if j - i == (endIndex - begIndex):
                curr_node = child
                i = j
            elif j == len(pattern):
                return child, j - i
            else:
                return None, None

        return curr_node, None

    def find_matches(self, node, matched_indices_set):
        if node.label_index >= 0:
            matched_indices_set.add(node.label_index)

        values = node.children.values()
        for val in values:
            self.find_matches(val, matched_indices_set)


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


def run_search_st2(fasta_file, fastq_file):
    fasta_seqs = utils.get_seq_from_file(fasta_file, "fasta")
    fastq_seqs = utils.get_seq_from_file(fastq_file, "fastq")
    base_filename = ntpath.basename(fasta_file)
    output_filename = base_filename.split('.')[0] + "_exp_output.sam"
    f = open(output_filename, 'w')
    count = 0
    for fasta_seq in fasta_seqs:
        sa, lcp, count = readsalcpfile(count, len(fasta_seq), fasta_file)
        tree = SuffixTree()
        tree.createSuffixtree(fasta_seq + "$", sa, lcp)

        for fastq_seq in fastq_seqs:
            node, idx = tree.find(fastq_seq.seq, fasta_seq.seq)

            if node is not None:
                matched_indices = set()
                tree.find_matches(node, matched_indices)
                utils.output_sam(matched_indices, fasta_seq, fastq_seq, f)


def main():
    parser = argparse.ArgumentParser(description="Matches a pattern using the naive suffix-tree implementation")
    parser.add_argument(dest="fasta_file", help="fasta file")
    parser.add_argument(dest="fastq_file", help="fastq file", nargs="?")
    parser.add_argument("-p", dest="preprocess",
                        action="store_true", help="preprocess genome")
    args = parser.parse_args()

    if args.preprocess:
        gen_lcp.run_gen_lcp(args.fasta_file)
        return

    run_search_st2(args.fasta_file, args.fastq_file)


if __name__ == "__main__":
    main()
