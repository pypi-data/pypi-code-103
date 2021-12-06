set_including_weak_vectors = set([
    # Nondominated
    (41, 37, 31),
    (23, 46, 43),
    (34, 29, 44),
    (50, 24, 44),
    (28, 40, 43),
    (30, 31, 39),
    (31, 30, 34),
    (28, 48, 35),
    (39, 28, 53),
    (21, 55, 47),
    (27, 36, 58),
    (24, 45, 38),

    # Dominated
    (41, 39, 32),
    (40, 46, 43),
    (35, 35, 44),
    (51, 24, 45),
    (28, 50, 44),
    (38, 31, 40),
    (50, 60, 70),
    (38, 48, 58),
    (39, 28, 54)
])

def weakly_dominates(left, right):
    return all((x <= y for x, y in zip(left, right)))

def dominates(left, right):
    if left == right: return False
    return weakly_dominates(left, right)

def _remove_dominated(nds):
    filtered = set()
    for nd in nds:
        if ( not any(dominates(other, nd) for other in nds) ):
            filtered.add(nd)
    return filtered


results = _remove_dominated(set_including_weak_vectors)
