import socket
from pathlib import Path
import os


def get_root_path():
    # Renvoie suivant la config le chemin parent de research_and_development
    host = socket.gethostname()
    local = bool(os.getenv("local", "False").lower())
    if host == "ADLAPTOPCG":
        # local = not Path("Y:/").is_dir()
        rootpath = Path(r"C:/Users/Christophe Geissler/") if local else Path(r"Y:/")
    elif host == "cgeissler-portable":
        # local = False
        rootpath = Path(r"/davs://advestis.synology.me:5006/")
        # rootpath = rootpath / r"research_and_development/Reduction_de_Dimension_(NMTF)/Article_PF_clustering/"
    else:
        # local = False
        nas_connected = Path(r"/media/SERVEUR/production/").is_dir() # if not local else False
        rootpath = Path(r"/media/SERVEUR/production/") if nas_connected else Path(r"/home/cgeissler/local_data/")
    return rootpath


