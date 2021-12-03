from pathlib import Path
import os


def create_dir(dirpath):
    "Create directory tree to `dirpath`; ignore if already exists"
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    return dirpath


def write_graph(dirpath, graph, format):
    """Write ``rdflib.Graph`` "graph" to ``pathlib.Path`` "dirpath".

    Doesn't return anything."""
    dirpath = Path(dirpath)
    create_dir(dirpath)
    with open(dirpath / (dirpath.parts[-1] + ".{}".format(format)), "wb") as f:
        graph.serialize(f, format=format, encoding="utf-8")
