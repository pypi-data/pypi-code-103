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
    if len(node.children) == 0:
        print(node.label_index, "".join(cigar))

    values = node.children.values()
    for val in values:
        self.find_matches(val, cigar)