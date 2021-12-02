import zoviz
import os


def guess_db_path_test():
    zoviz.guess_db_path()


def load_table_test():
    here = os.path.split(os.path.abspath(__file__))[0]
    ref_data_path = os.path.join(here, "zotero.sqlite")
    with zoviz.DB(ref_data_path) as z:  # Enter
        _ = z["creators"]  # Load table
    # Exit


def build_creator_graph_test():
    here = os.path.split(os.path.abspath(__file__))[0]
    ref_data_path = os.path.join(here, "zotero.sqlite")
    with zoviz.DB(ref_data_path) as z:
        _ = z.build_creator_graph(collection="Fusion")
