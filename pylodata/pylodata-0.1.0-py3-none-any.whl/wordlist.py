"""
Facilities for wordlist manipulations.
"""
from collections import defaultdict


def get_binary_patterns(wordlist, ref="cogid", missing="Ø"):
    """
    Calculate presence-absence matrix from the wordlist.

    :params ref: The reference column storing cognate sets.
    """
    patterns = {}
    etd = wordlist.get_etymdict(ref=ref)

    # calculate missing data per concept
    present = {doculect: set() for doculect in wordlist.cols}
    for idx, doculect, concept in wordlist.iter_rows("doculect", "concept"):
        present[doculect].add(concept)
    for cogid, row in etd.items():
        pattern = {doculect: "0" for doculect in wordlist.cols}
        idxs = []
        for cell in row:
            if cell:
                idxs += cell
        concepts = set([wordlist[idx, "concept"] for idx in idxs])
        for cell, language in zip(row, wordlist.cols):
            if cell:
                pattern[language] = "1"
            else:
                if not concepts.intersection(present[language]):
                    pattern[language] = missing

        patterns[cogid] = pattern
    return patterns, ["1", "0", missing]


def get_multistate_patterns(wordlist, ref="cogid", missing="Ø"):
    patterns = {
        concept: {doculect: [] for doculect in wordlist.cols}
        for concept in wordlist.rows
    }

    characters = defaultdict(int)
    for idx, doculect, concept, cogid in wordlist.iter_rows("doculect", "concept", ref):
        patterns[concept][doculect] += [str(cogid)]
        characters[str(cogid)] += 1
    for concept in patterns:
        for doculect in wordlist.cols:
            if not patterns[concept][doculect]:

                patterns[concept][doculect] = [missing] if missing else []
    return patterns, sorted(characters, key=lambda x: characters[x], reverse=True)
