#!/usr/bin/env python3

"""
|==============================================|
| Graphe qui represente un cluster de travail. |
|==============================================|

* C'est l'element de base qui permet pour un ordinateur
d'avoir une vision fine de ces voisins.

* Le graphe doit etre lance par le serveur local qui tourne sur ce PC.
"""

import os
import queue
import random
import re
import socket
import subprocess
import sys
import threading
import time
import warnings

import raisin
from raisin.errors import *
from raisin.tools import Printer, identity
from raisin.application.settings import settings
import raisin.communication.tcp_client as tcp_client
from .. import basegraph
from . import computer, router, connection, SERVERS
from raisin.communication.constants import RESERVED_PORTS, PORT


class Network(basegraph.BaseGraph):
    """
    |======================================|
    | Specialisation d'un graphe abstrait. |
    |======================================|

    * Ce graphe represente precisement l'etat actuel
    du cluster de travail.
    * Il doit etre initialisé.
    """
    def __init__(self, network_data=None, is_main=True, minimalist=False):
        """
        |================================================|
        | Initialise le graphe qui represente le reseau. |
        |================================================|

        * Tente d'abord de charger le graphe depuis le fichier
        de d'enregistrement si il existe.
        * S'assure que le graphe soit coherent par raport aux parametres.
        Cette verification a pour but d'eviter les melanges entre reseaux.
        * Si le graphe n'est pas celui du bon reseau ou bien qu'il n'existe
        pas, il est cree de toutes pieces.

        Parameters
        ----------
        :param network_data: Le reseau serialize.
            * Si il est omis (None), recherche si il se trouve
            dans le fichier "~.raisin.network.rsn".
            * Si ce fichier n'existe pas, un reseau tout neuf est genere.
            * Si cet argument est specifie, il doit sortir tout droit de
            la methode ``serialize`` de la classe ``Network``.
        :type network_data: generator or list.
        :param is_main: Permet de savoir si cet initialisateur est bien le principal.
            Autrement dit, si ``main`` == True, alors un graph complet avec les scan et tout
            va etre fait, sinon, il se contente de construire le graph a partir des donnees.
        :type is_main: boolean
        :param minimalist: Si il est vrai, le graphe est crer sans aucune connaissance.
            Il ne doit pas etre changer, c'est pour simplifier la recursivite. L'utilisateur n'a pas a y toucher.
        :type minimalist: boolean

        Returns
        -------
        :return: Le graphe instancie, verifie et initialise.
        :rtype: Network
        """
        network_file = os.path.join(os.path.expanduser("~"), ".raisin", "network.rsn")
        super().__init__(directed=True, comment="Cluster")
        self.network_name = None # Doit etre initialise.

        # Cas graphe minimaliste.
        if minimalist:
            self.build()
            return
        
        # Remplissage avec les donnees fournies ou les donnees trouvee dans le fichier.
        if os.path.exists(network_file) or network_data is not None:
            with Printer("Making cluster graph with given datas..."):
                nodes = {
                    "Computer": computer.Computer,
                    "Internet": router.Internet,
                    "InBoxing": router.InBoxing,
                    "OutBoxing": router.OutBoxing}
                if network_data is None:
                    with open(network_file, "rb") as f:
                        network_data = list(raisin.load(f)) # Le 'list' c'est pour eviter ValueError: read of closed file.
                for kind, attr in network_data: # Generateur des noeuds puis des arcs.
                    if kind in nodes:
                        node = nodes[kind](**attr["init"])
                        node.init(attr["adaptive"])
                        self.add_vertex(node)
                    elif kind == "Connection":
                        conn = connection.Connection(
                            self.__getitem__(attr["init"]["vs"], is_vertex=True),
                            self.__getitem__(attr["init"]["vd"], is_vertex=True))
                        conn.init(attr["adaptive"])
                        self.add_arrow(conn)
                    elif kind == "properties":
                        for key, value in attr.items():
                            setattr(self, key, value)
                    else:
                        raise TypeError("Le reseau ne possede pas de %s." % repr(kind))
        else:
            self.network_name = settings["server"]["network_name"]

        # Verification, preparation pour la suite:
        if not self.verification(): # Si le graphe n'est pas legal.
            if not is_main: # Si c'est un graph secondaire.
                raise NotCompliantError("Le graphe n'est pas conforme.") # On est sans pitier.
            for node in self.get_vertices(): # Si par contre on est entrain de construire le graphe principal,
                del self[node] # on se contente de repartir a 0.
            self.network_name = settings["server"]["network_name"]

        # On complete le graphe actuel.
        if is_main: # Seulement dans le cas ou on est dans le constructeur principale.
            with Printer("Upgrade network graph with minimalist graph..."):
                self.merge(Network(is_main=False, minimalist=True))

    def verification(self):
        """
        |==================================================|
        | S'assure que le graphe est celui du bon cluster. |
        |==================================================|

        Returns
        ------
        :return: True si le graphe est OK, False sinon.
        :rype: boolean
        """
        if settings["server"]["network_name"] != self.network_name:
            return False
        from raisin.application.hmi.checks import network_name_verification
        name_ok = network_name_verification(self.network_name)
        del network_name_verification
        return name_ok

    def build(self):
        """
        |==================================|
        | Complete le tout premier graphe. |
        |==================================|

        Il y a 4 possibilitees:
        1) Reseau mondial.
            -> Se connecte a un serveur pour recuperer les informations.
        2) Rejoindre un cluster specifique.
            -> Demande les informations a ce serveur.
        3) Administrer son propre reseau.
            -> Initialise les reseau minimal ou on est le seul.
        4) Scanner le reseau local.
            -> Scane le reseau local sur les ports 20001-20009
        """
        def scan(ip, graph_queue, p):
            """
            Recherche si l'adresse ip existe.
            Si c'est le cas, recherche les ports ouverts.
            Si il y en a, et que c'est un port de serveur raisin,
            une connection est etablie, le client est pousse dans la file.
            """
            # Verification de l'existance de l'ip.
            try:
                hostname, alias, addresslist = socket.gethostbyaddr(ip)
            except socket.herror: # Si ca echoue ca veut pas forcement dire qu'il n'y a pas un serveur.
                capt = {} if identity["python_version"] < "3.7" else {"capture_output": True} # Pour eviter l'erreur "got an unexpected keyword argument 'capture_output'".
                std = " > /dev/null" if identity["python_version"] < "3.7" and identity["system"] == "linux" else "" # Stratageme pour cacher la sortie standard.
                if subprocess.run("ping -c 1 %s%s" % (ip, std),
                        shell=True, **capt).returncode:
                    return
                hostname, addresslist = ip, [ip]
                p.show("Found ip '%s'." % hostname)
            else:
                p.show("%s found at the ip '%s'." % (repr(hostname), ", ".join(addresslist)))
            
            # Scan du port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if 0 == sock.connect_ex((ip, PORT)):
                sock.close()
                p.show("port %d for %s is open." % (PORT, repr(hostname)))
                try:
                    graph = tcp_client.Client(ip, PORT).ask_network()
                except Exception:
                    return
                else:
                    graph_queue.put(graph)
                    return
            sock.close()            
        
        def complete(network_data):
            """
            Ajoute a self, les noeuds et les arcs.
            'graph' et un graph serialise livre par un serveur.
            """
            self.merge(Network(network_data=network_data, is_main=False))

        with Printer("Initialization of the minimalist cluster graph...") as p:
            self.network_name = settings["server"]["network_name"] # Si il y a un changement de cluster, on s'adapte.

            # Creation du reseau minimaliste.
            internet = router.Internet()
            outboxing = router.OutBoxing(mac=None)
            myself = computer.Computer(identity["mac"])
            self.add_vertex(internet) # Le noeud internet global.
            self.add_vertex(outboxing) # La boxe pour les requettes sortantes.
            self.add_vertex(myself) # Soit meme.
            self.add_arrow(connection.Connection(myself, outboxing))
            self.add_arrow(connection.Connection(outboxing, internet))

            self.add_arrow(connection.Connection(outboxing, myself))
            if settings["server"]["port_forwarding"]:
                inboxing = router.InBoxing(mac=None)
                inboxing.add_attr("table", {(settings["server"]["port_forwarding"], identity["mac"]),})
                inboxing.add_attr("ipv4", str(identity["ipv4_wan"]) if identity["ipv4_wan"] else "")
                inboxing.add_attr("ipv6", str(identity["ipv6"]) if identity["ipv6"] else "")
                inboxing.add_attr("dns_ipv4", settings["server"]["dns_ipv4"] if settings["server"]["dns_ipv4"] else "")
                inboxing.add_attr("dns_ipv6", settings["server"]["dns_ipv6"] if settings["server"]["dns_ipv6"] else "")
                self.add_vertex(inboxing)
                
                self.add_arrow(connection.Connection(inboxing, myself))
                self.add_arrow(connection.Connection(internet, inboxing))

            # Si il faut se lier au reseau mondial.
            if self.network_name == "main":
                p.show("Connection to the mondial network.")
                servers = [s.split("@") for s in SERVERS]
                random.shuffle(servers)
                for port, ip in servers:
                    try:
                        network_data = tcp_client.Client(ip, int(port)).ask_network()
                    except ConnectionError:
                        continue
                    else:
                        complete(network_data)
                        return
                warnings.warn("Aucun serveur n'est accessible.", RuntimeWarning)

            # Si il faut se lier a un reseau specifique.
            if re.search(r"^\d+@[a-zA-Z0-9_\.:]{5,}$", self.network_name):
                p.show("Connection to %s." % repr(self.network_name))
                port, ip = network_name.split("@")
                network_data = tcp_client.Client(ip, int(port)).ask_network()
                complete(network_data)

            # Si il faut scanner le reseau local.
            elif self.network_name == "":
                p.show("Local network scan.")
                graph_queue = queue.Queue()
                ip_base = ".".join(str(identity["ipv4_lan"]).split(".")[:-1]) + ".%d"
                threads = []
                for addr in (ip_base % i for i in range(256)):
                    while True:
                        if threading.active_count() < 64: # Nombre de threads simultanes.
                            threads.append(threading.Thread(target=scan, args=(addr, graph_queue, p)))
                            threads[-1].start()
                            break
                        else:
                            time.sleep(1)
                            threads = [th for th in threads if th.is_alive()]
                
                # On attend que tout ait ete scanne.
                while threads:
                    time.sleep(1)
                    threads = [th for th in threads if th.is_alive()]
                
                # Traitement du resultat si il est la.
                while not graph_queue.empty():
                    complete(graph_queue.get())

            # Si ce n'est rien de tout ca.
            else:
                ValueError("'%s' n'est pas reconnaissable pour initialiser le reseau."
                    % repr(self.network_name))

    def record(self):
        """
        |=========================================|
        | Met a jour le fichier d'etat du graphe. |
        |=========================================|

        * Le fichier mis a jour c'est '~/.raisin/network.rsn'.

        :raise: FileNotFoundError si raisin n'est pas installe.
        """
        import raisin

        root = os.path.join(os.path.expanduser("~"), ".raisin")
        if not os.path.exists(root):
            raise FileNotFoundError("'raisin' n'est pas installe. "
                "veuillez executer: '%s -m raisin install'" % sys.executable)
        
        with open(os.path.join(root, "network.rsn"), "wb") as f:
            raisin.dump(self.serialize(), f)

    def serialize(self):
        """
        |======================|
        | Serialize ce graphe. |
        |======================|

        * Fait pour etre utilise avec ``raisin.serialize(self.serialize())``.

        Returns
        -------
        :return: Un generateur des informations suffisantes pour
            reconstituer les noeuds puis les arcs.
        :rtype: generator
        """
        yield ("properties", {"network_name": self.network_name})
        for node in self.get_vertices():
            yield (type(node).__name__, {"init": node.get_attr(), "adaptive": node.init()})
        for conn in self.get_segments():
            yield (type(conn).__name__, {"init": conn.get_attr(), "adaptive": conn.init()})

    def merge(self, other):
        """
        |==================================|
        | Met a jour les valeurs du graphe |
        | a partir du graphe 'other'.      |
        |==================================|

        * Ne retourne rien, met juste le graphe a jour.

        Parameters
        ----------
        :param other: L'autre graphe dont on tire les informations.
        :type other: Network
        """
        assert isinstance(other, Network), \
            "'other' has to be of type Network, not %s." % type(other).__name__

        with Printer("Merging networks...") as p:
            for node_other in other.get_vertices():
                if isinstance(node_other, (router.InBoxing, router.OutBoxing, computer.Computer)):
                    try: # On tente de recuperer le noeud pour le comparer.
                        node_self = self[node_other.name] 
                    except KeyError: # Si il fait ajouter un nouveau noeud.
                        p.show("New %s." % node_other)
                        if node_other.n in self.id2vertex:
                            node_other.n = 1 + max(self.id2vertex)
                        self.add_vertex(node_other)
                    else: # Si il faut merger les 2 noeuds.
                        p.show("Merge %s." % node_other)
                        if node_self.n != node_other.n: # Si les noeuds n'ont pas le meme id mais sont en realite les meme.
                            if node_other.is_older(node_self): # Si c'est nous qui somme en tord.
                                p.show(f"Change id {node_self.n} to id {node_other.n}.") # On s'adapte.
                                self.mv_vertex_id(node_self, node_other.n)
                        node_self.merge(node_other)

            for conn_other in other.get_segments(): 
                if conn_other.vs.name in self:
                    conn_other.vs = self[conn_other.vs.name]
                if conn_other.vd.name in self:
                    conn_other.vd = self[conn_other.vd.name] 
                try: # On tente de recuperer la connection pour la comparer.   
                    conn_self = self[(conn_other.vs.name, conn_other.vd.name)] 
                except KeyError: # Si la connection est nouvelle.
                    p.show("New %s." % conn_other)
                    if conn_other.n in self.id2segment:
                        conn_other.n = 1 + max(self.id2segment)
                    self.add_arrow(conn_other)
                else: # Si la connection existe deja.
                    p.show("Merge %s." % conn_other)
                    conn_self.merge(conn_other)
