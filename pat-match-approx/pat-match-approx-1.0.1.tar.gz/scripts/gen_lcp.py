import argparse
import ntpath

from scripts import utils


class Node:
    def __init__(self, label_index=0, begin=0, end=0):
        self.begin = begin
        self.end = end
        self.label_index = label_index
        self.children = {}
        self.suffixIndex = -1


class SuffixTree:
    def __init__(self, s):
        s += '$'
        self.root = Node()
        self.root.children[s[0]] = Node(0, 0, len(s))

        for i in range(1, len(s)):
            curr_node = self.root
            j = i
            while j < len(s):
                if s[j] in curr_node.children:
                    child = curr_node.children[s[j]]
                    begIndex = child.begin
                    endIndex = child.end
                    k = j + 1

                    while k - j < (endIndex - begIndex) and s[k] == s[begIndex + k - j]:
                        k = k + 1

                    if k - j == (endIndex - begIndex):
                        curr_node = child
                        j = k
                    else:
                        existing_suffix = s[begIndex + k - j]
                        new_suffix = s[k]
                        split = Node(child.label_index, begIndex, begIndex + k - j)
                        split.children[new_suffix] = Node(i, k, len(s))
                        split.children[existing_suffix] = child
                        child.begin = begIndex + k - j
                        child.end = endIndex
                        curr_node.children[s[j]] = split
                else:
                    curr_node.children[s[j]] = Node(i, j, len(s))

    def getSAbyDFS(self, node, lent, height, sa):
        leaf = 1
        i = 0
        for val in sorted(node.children):
            child = node.children[val]
            leaf = 0
            self.getSAbyDFS(child, lent, height + child.end - child.begin, sa)
        if leaf == 1:
            sa.append(node.label_index)

    def getLCP(self, st, sa):
        inverse_sa = [-1] * len(sa)
        for i, suffix in enumerate(sa):
            inverse_sa[suffix] = i
        lcp_array = [-1] * len(sa)
        lcp_array[0] = 0
        lcp = 0
        for i in inverse_sa:
            if i > 0:
                i0, i1 = sa[i], sa[i - 1]
                while st[i0 + lcp] == st[i1 + lcp]:
                    lcp += 1
                lcp_array[i] = lcp
                lcp = max(0, lcp - 1)
            else:
                lcp = 0
        return lcp_array


def run_gen_lcp(fasta_file):
    fasta_seqs = utils.get_seq_from_file(fasta_file, "fasta")
    base_filename = ntpath.basename(fasta_file)
    output_filename = base_filename.split('.')[0] + "_sa-lcp.txt"

    f = open(output_filename, "w")

    for fasta_seq in fasta_seqs:
        sa = []
        tree = SuffixTree(fasta_seq)
        tree.getSAbyDFS(tree.root, len(fasta_seq), 0, sa)
        lcp = tree.getLCP(fasta_seq + "$", sa)
        for element in sa:
            f.write(str(element) + "\n")
        for element in lcp:
            f.write(str(element) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Matches a pattern using the naive suffix-tree implementation")
    parser.add_argument(dest="fasta_file", help="fasta file")
    args = parser.parse_args()
    run_gen_lcp(args.fasta_file)


if __name__ == "__main__":
    main()
