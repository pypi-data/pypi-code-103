from typing import List, Tuple
# import spacy
# import stanza
# import trankit


def extract_edges_from_spacy(corpus: str,
                             model  # : spacy.lang
                             ) -> (List[List[Tuple[int, int]]], List[int]):
    """ Parse all sentences with SpaCy, and extract parent-child relations
          from the dependency tree as edges.
    """
    # parse string into sentences
    docs = model(corpus)

    # extract edges of dependency tree
    all_edges = []
    num_nodes = []
    for snt in docs.sents:
        # extract edges
        edges = [(0 if t.dep_ == 'ROOT' else (t.head.i + 1), t.i + 1)
                 for t in snt
                 if isinstance(t.i, int)]
        # adjust ids
        d = min([c for p, c in edges]) - 1
        edges = [(max(0, p - d), c - d) for p, c in edges]
        # store everything
        all_edges.append(edges)
        num_nodes.append(len(snt) + 1)

    # done
    return all_edges, num_nodes


def extract_edges_from_stanza(corpus: str,
                              model  #: stanza.pipeline.core.Pipeline
                              ) -> (List[List[Tuple[int, int]]], List[int]):
    """ Parse all sentences with Stanza, and extract parent-child relations
          from the dependency tree as edges.
    """
    # parse string into sentences
    docs = model(corpus)

    # extract edges of dependency tree
    all_edges = []
    num_nodes = []
    for snt in docs.sentences:
        # extract edges
        edges = [(t.head, t.id) for t in snt.words if isinstance(t.id, int)]
        # store everything
        all_edges.append(edges)
        num_nodes.append(len(snt.words) + 1)

    # done
    return all_edges, num_nodes


def extract_edges_from_trankit(corpus: str,
                               model  # : trankit.pipeline.Pipeline
                               ) -> (List[List[Tuple[int, int]]], List[int]):
    """ Parse all sentences with Trankit, and extract parent-child relations
          from the dependency tree as edges.
    """
    # parse string into sentences
    docs = model(corpus)

    # extract edges of dependency tree
    all_edges = []
    num_nodes = []
    for snt in docs.get("sentences"):
        # extract edges
        edges = [(t.get("head"), t.get("id"))
                 for t in snt.get("tokens")
                 if isinstance(t.get("id"), int)]
        # store everything
        all_edges.append(edges)
        num_nodes.append(len(snt.get("tokens")) + 1)

    # done
    return all_edges, num_nodes
