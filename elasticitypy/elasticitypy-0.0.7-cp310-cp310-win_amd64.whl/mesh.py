from typing import Tuple, List, Callable, Set


def tet_edges(tet: Tuple[int, int, int, int]) -> List[Tuple[int, int]]:
    out = []
    for i in range(0, 2):
        out.append((tet[i], tet[i + 1]))
    out.append((tet[0], tet[2]))
    for i in range(0, 3):
        out.append((tet[i], tet[3]))
    return out


class Group:
    id: int
    vers: Set[int]
    edges: Set[Tuple[int, int]]
    tets: Set[Tuple[int, int, int, int]]

    def __init__(self, id: int, vers: Set[int], edges: Set[Tuple[int, int]], tets: Set[Tuple[int, int, int, int]]):
        self.id, self.vers, self.edges, self.tets = id, vers, edges, tets


class Mesh:
    pts: List[Tuple[float, float, float]]
    edges: Set[Tuple[int, int]]
    tets: List[Tuple[int, int, int, int]]
    group_num: int

    def __init__(self, pts: List[Tuple[float, float, float]], tets: List[Tuple[int, int, int, int]]):
        self.group_num = 1
        self.pts = pts
        self.edges = set()
        self.tets = []
        for tet in tets:
            tet = sorted(tet)
            tet = (tet[0], tet[1], tet[2], tet[3])
            for edges in tet_edges(tet):
                self.edges.add(edges)
            self.tets.append(tet)

    def def_group(self, cond: Callable[[float, float, float], bool]):
        id = self.group_num
        self.group_num += 1
        vers = set()
        edges = set()
        tets = set()
        for tet in self.tets:
            tet_in_group = True
            for edge in tet_edges(tet):
                edge_in_group = True
                for ver in edge:
                    x, y, z = self.pts[ver]
                    if cond(x, y, z):
                        vers.add(ver)
                    else:
                        edge_in_group = False
                        tet_in_group = False
                if edge_in_group:
                    edges.add(edge)
            if tet_in_group:
                tets.add(tet)
        return Group(id, vers, edges, tets)
