import zoviz
import os
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import lorem

if matplotlib.get_backend() != "Agg":
    matplotlib.use("Agg")  # Headless mode for dockerized build


def draw_multigraph_test():
    here = os.path.split(os.path.abspath(__file__))[0]
    ref_data_path = os.path.join(here, "zotero.sqlite")
    with zoviz.DB(ref_data_path) as z:
        g = z.build_creator_graph(collection="Fusion")
        layout = nx.spring_layout(g)
        _ = zoviz.draw_multigraph(g, pos=layout)


def draw_community_graph_test():
    here = os.path.split(os.path.abspath(__file__))[0]
    ref_data_path = os.path.join(here, "zotero.sqlite")
    with zoviz.DB(ref_data_path) as z:
        g = z.build_creator_graph(collection="Fusion")
        for n in g.nodes:
            n.name = lorem.sentence().split()[0:2]
            n.name = n.name[0] + " " + n.name[1]
        _ = zoviz.draw_community_graph(g)
    # Use this test to generate the docs
    docs_path = os.path.join(os.path.split(here)[0], "docs", "source")
    plt.title("Names scrambled for example")
    plt.savefig(os.path.join(docs_path, "community_graph.png"),
                bbox_inches='tight', pad_inches=0.1)
