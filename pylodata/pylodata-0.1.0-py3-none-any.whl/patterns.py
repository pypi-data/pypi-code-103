"""
Methods for loading correspondence patterns.
"""
import codecs
from collections import defaultdict


def get_correspondence_patterns(path, positions=None, threshold=5):
    """
    Load correspondence pattern data.
    """
    positions = positions or ["c", "v"]
    with codecs.open(path, "r", "utf-8") as f:
        data = [[cell.strip() for cell in row.split("\t")] for row in f]

    patterns = {}
    doculects = data[0][3:-2]
    characters = defaultdict(int)
    for row in data[1:]:
        if row[1] in positions and int(row[2]) >= threshold:
            patterns[row[0]] = dict(zip(doculects, row[3:-2]))
            for char in row[3:-2]:
                characters[char] += 1
    characters = sorted(characters, key=lambda x: characters[x], reverse=True)
    return patterns, characters


def get_binary_correspondence_patterns(path, positions=None, threshold=5, missing="Ø"):
    """
    Load correspondence pattern data in binarized form.
    """
    patterns, characters = get_correspondence_patterns(
        path, positions=positions, threshold=threshold
    )
    bpats = {}

    for key, pattern in patterns.items():
        chars = [char for char in set(pattern.values()) if char != missing]
        for char in chars:
            new_pattern = {}
            for doculect, sound in pattern.items():
                if sound == char:
                    new_pattern[doculect] = ["1"]
                elif sound == missing:
                    new_pattern[doculect] = [missing]
                else:
                    new_pattern[doculect] = ["0"]
            bpats[key + "-" + char] = new_pattern
    return bpats, ["1", "0", "Ø"]
