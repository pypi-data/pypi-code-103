import networkx as nx
from typing import List, Tuple


def node_token_distances_single(edges: List[Tuple[int, int]],
                                num_nodes: int,
                                cutoff: int = 25
                                ) -> (List[int], List[int]):
    """ Compute Shortest Paths between Nodes """
    # Build undirected graph
    G = nx.Graph()  # Undirected Graph(!)
    G.add_nodes_from(range(num_nodes))
    G.add_edges_from(edges)

    # compute Shortest Path between all nodes
    pathlen = nx.all_pairs_shortest_path_length(G, cutoff=cutoff)
    pathlen = dict(pathlen)

    # compute node distances and the corresponding token distances
    nodedist = []
    tokendist = []
    indicies = []
    for i, row in pathlen.items():
        for j, val in row.items():
            if i > j:
                nodedist.append(val)
                tokendist.append(i - j)
                indicies.append((i, j))
    # done
    return nodedist, tokendist, indicies


def node_token_distances(all_edges: List[List[Tuple[int, int]]],
                         num_nodes: List[int],
                         cutoff: int = 25
                         ) -> (List[int], List[int]):
    """ Loop over each sentence to compute the shorted distance """
    nodedist, tokendist, indicies = [], [], []
    for i in range(len(num_nodes)):
        tmpnode, tmptok, tmpidx = node_token_distances_single(
            all_edges[i], num_nodes[i], cutoff=cutoff)
        nodedist.append(tmpnode)
        tokendist.append(tmptok)
        indicies.append(tmpidx)
    return nodedist, tokendist, indicies
