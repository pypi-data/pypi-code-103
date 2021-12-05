#!/usr/bin/env python3

"""
|========================================|
| C'est la partie qui permet de recevoir |
| des clients et de leur repondre.       |
|========================================|

Ce script permet seulement de faire le lien entre
les clients et le reste du programe. Les reponses
aux requettes ne sont pas faites ici.

Ce fichier est fortement influance par ce lien:
    https://www.neuralnine.com/tcp-chat-in-python/
"""

import multiprocessing
import os
import queue
import re
import socket
import sys
import threading
import time
import uuid

from raisin import dumps, loads
from raisin.graph.clustergraph import network
from ..tools import Printer, identity, timeout_decorator
from ..application.settings import settings
from ..errors import *
from . import checks, request, routing


def client_load():
    """
    |===============================|
    | Recherche l'etat des clients. |
    |===============================|

    sortie
    ------
    :return: Un tuple contenant 3 listes:
        - La liste 'waitlisted' des clients
            en attente de validation.
        - La liste 'whitelisted' des clients
            acceptes par l'administrateur.
        - La liste 'blacklisted' des clients
            refuses par l'administrateur.
    :rtype: (list, list, list)
    """
    waitlisted = []
    whitelisted = []
    blacklisted = []
    wait_path = os.path.join(
        os.path.expanduser("~"), ".raisin", "waitlisted.txt")
    white_path = os.path.join(
        os.path.expanduser("~"), ".raisin", "whitelisted.txt")
    black_path = os.path.join(
        os.path.expanduser("~"), ".raisin", "blacklisted.txt")

    # waitlisted: (time client)
    if os.path.exists(wait_path):
        with open(wait_path, "r") as f:
            waitlisted = [
                [t, loads(c)] for t, c in
                [l.split() for l in f.readlines()]]

    # whitelisted: (mac time)
    if os.path.exists(white_path):
        with open(white_path, "r") as f:
            whitelisted = [
                l.rstrip().split()
                for l in f.readlines()]

    # blacklisted: (mac time state)
    if os.path.exists(black_path):
        with open(black_path, "r") as f:
            blacklisted = [
                l.rstrip().split()
                for l in f.readlines()]

    return waitlisted, whitelisted, blacklisted

def client_dump(waitlisted, whitelisted, blacklisted):
    """
    |============================|
    | Enregistre la nouvelle     |
    | configuration des clients. |
    |============================|

    entree
    ------
    :param waitlisted: La liste des clients en attente.
        [(time, client), ...]
    :type waitlisted: list
    :param whitelisted: La liste des clients acceptes.
        [(mac, time), ...]
    :type whitelisted: list
    :param blacklisted: La liste des clients a refuser.
        [(mac, time, state), ...]
    :type blacklisted: list
    """
    wait_path = os.path.join(
        os.path.expanduser("~"), ".raisin", "waitlisted.txt")
    white_path = os.path.join(
        os.path.expanduser("~"), ".raisin", "whitelisted.txt")
    black_path = os.path.join(
        os.path.expanduser("~"), ".raisin", "blacklisted.txt")

    # waitlisted: (time client)
    if not waitlisted and os.path.exists(wait_path):
        os.remove(wait_path)
    else:
        with open(wait_path, "w", encoding="utf-8") as f:
            f.write("".join(
                "%s %s\n" % (time, dumps(client))
                for time, client in waitlisted))

    # whitelisted: (mac time)
    if not whitelisted and os.path.exists(white_path):
        os.remove(white_path)
    else:
        with open(white_path, "w", encoding="utf-8") as f:
            f.write("".join(
                "%s %s\n" % (mac, time)
                for mac, time in whitelisted))

    # blacklisted: (mac time state)
    if not blacklisted and os.path.exists(black_path):
        os.remove(black_path)
    else:
        with open(black_path, "w", encoding="utf-8") as f:
            f.write("".join(
                "%s %s %s\n" % (mac, time, state)
                for mac, time, state in blacklisted))

def client_remove(mac):
    """
    |================================|
    | Supprime des listes ce client. |
    |================================|

    entree
    ------
    :param mac: L'adresse mac du client a supprimer.
    :type mac: str

    sortie
    ------
    :raises KeyError: Si ce client n'est pas recence.
    """
    assert isinstance(mac, str), \
        "'mac' have to be str, not %s." % type(mac).__name__
    assert re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", mac), \
        "%s is not a valid mac address." % repr(mac)

    with Printer("Delete client %s." % mac) as p:
        waitlisted, whitelisted, blacklisted = client_load()
        found = False

        new_waitlisted = [(t, c) for t, c in waitlisted if c["mac"] != mac]
        if new_waitlisted != waitlisted:
            p.show("Client removed from the waitlisted.")
            found = True

        new_whitelisted = [(m, t) for m, t in whitelisted if m != mac]
        if new_whitelisted != whitelisted:
            p.show("Client removed from the whitelisted.")
            found = True

        new_blacklisted = [(m, t, s) for m, t, s in blacklisted if m != mac]
        if new_blacklisted != blacklisted:
            p.show("Client removed from the blacklisted.")
            found = True

        if not found:
            raise KeyError("The client %s was not found." % mac)

        client_dump(new_waitlisted, new_whitelisted, new_blacklisted)

def client_accept(mac):
    """
    |==========================================|
    | Deplace le client vers la liste blanche. |
    |==========================================|

    entree
    ------
    :param mac: L'adresse mac du client a deplacer.
    :type mac: str

    sortie
    ------
    :raises KeyError: Si ce client n'est pas recence.
    """
    assert isinstance(mac, str), \
        "'mac' have to be str, not %s." % type(mac).__name__
    assert re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", mac), \
        "%s is not a valid mac address." % repr(mac)

    with Printer("Moove client %s to whitelisted." % mac) as p:
        client_remove(mac)
        waitlisted, whitelisted, blacklisted = client_load()
        whitelisted.append((mac, time.strftime("%Y-%m-%dT%H:%M:%S")))
        client_dump(waitlisted, whitelisted, blacklisted)
        p.show("Client appened to the 'whitelisted'.")

def client_exile(mac):
    """
    |========================================|
    | Deplace le client vers la liste noire. |
    |========================================|

    entree
    ------
    :param mac: L'adresse mac du client a deplacer.
    :type mac: str

    sortie
    ------
    :raises KeyError: Si ce client n'est pas recence.
    """
    assert isinstance(mac, str), \
        "'mac' have to be str, not %s." % type(mac).__name__
    assert re.fullmatch(r"(?:[0-9a-f]{2}:){5}[0-9a-f]{2}", mac), \
        "%s is not a valid mac address." % repr(mac)

    with Printer("Moove client %s to blacklisted." % mac) as p:
        client_remove(mac)
        waitlisted, whitelisted, blacklisted = client_load()
        blacklisted.append((mac, time.strftime("%Y-%m-%dT%H:%M:%S"), "definitive"))
        client_dump(waitlisted, whitelisted, blacklisted)
        p.show("Client appened to the 'blacklisted'.")


class Server:
    """
    |================================================|
    | Serveur raisin qui accepte les clients raisin. |
    |================================================|

    C'est un serveur qui supporte les requettes ipv6 et ipv4.
    Il accepte plusieurs clients a la fois jusqu'a la limite autorisee.

    exemple
    -------
    :Example:
    >>> from raisin.communication import tcp_server
    >>> s = tcp_server.Server()
    >>> s.start() # Methode bloquante.
    """
    def __init__(self):
        """
        Constructeur qui initialise juste les
        sockets de facon locale.
        """
        with Printer("Initialisation of TCP servers...") as p:
            # graphe pour le reste du monde
            self.graph = network.Network() # Avant de se metre en ecoute, on regarde notre environement.

            # partie environement
            self.clients = {}       # C'est tous les clients connectes definitivement, apres avoir passe les tests.
            self.waiting = set()    # La liste des clients en attente de l'aprobation de l'administrateur.
            self.client_queue = queue.Queue() # La queue des clients qui attende qu'on leur donne un petit processus rien que pour eux.

            # partie serveur
            self.port = settings["server"]["port"]
            self.listen = settings["server"]["listen"]
            self.ipv4 = identity["ipv4_lan"]
            self.ipv6 = identity["ipv6"]
            if self.ipv4 is None and self.ipv6 is None:
                raise ConnectionError(
                    "Impossible de detecter l'ip, peut etre n'y a-t-il pas internet?")

            addr = ("", self.port)  # Toutes les interfaces, port 'self.port'
            self.tcp_socket_bis = None
            if identity["python_version"] >= "3.8":
                if socket.has_dualstack_ipv6():
                    self.tcp_socket = socket.create_server(addr,
                        family=socket.AF_INET6, dualstack_ipv6=True, reuse_port=True)
                else:
                    self.tcp_socket = socket.create_server(addr, reuse_port=True)
            else: # La gestion mixe ipv6 ipv4 n'est disponible que a partir de python3.8 .
                if self.ipv6:
                    self.tcp_socket_bis = socket.socket(
                        socket.AF_INET6,        # socket internet en ipv6
                        socket.SOCK_STREAM)     # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
                    self.tcp_socket_bis.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                    self.tcp_socket_bis.bind(addr)
                self.tcp_socket = socket.socket(
                    socket.AF_INET,         # socket internet plutot qu'un socket unix
                    socket.SOCK_STREAM)     # creation d'un TCP/IP socket, SOCK_STREAM=>TCP
                self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # on tente de reutiliser le port si possible
                self.tcp_socket.bind(addr)
            # On empeche que la file d'attente soit plus longue
            # que le nombre max de clients acceptable.
            self.tcp_socket.listen(settings["server"]["listen"])
            if self.tcp_socket_bis:
                self.tcp_socket_bis.listen(settings["server"]["listen"])

            # Partie information (hmi).
            if self.ipv4 and self.ipv6:
                message = "aux adresses '%s' et '%s'" % (self.ipv6, self.ipv4)
            else:
                message = "a l'adresse '%s'" % (self.ipv6 if self.ipv6 else self.ipv4)
            p.show("En ecoute sur le port %d %s..." % (self.port, message))

    def accept(self, client_id, is_a):
        """
        |=====================|
        | Memorise le client. |
        |=====================|

        Ajoute le client passe en parametre dans la liste blanche
        ou a la liste noir si l'utilisateur le veut.
        Si il faut attendre l'approbation de l'utilisateur,
        cette fonction est bloquante.
        Si l'utilisateur est trop long a se decider. Le client
        est blackliste et un mail est envoye a l'utilisateur.

        entree
        ------
        :param client_id: Carte d'identite du client.
        :type client_id: dict
        :param is_a: Sortie de self.is_accepted()
        :type is_a: boolean ou None

        sortie
        ------
        :return: True si le client est en mis en liste blanche, False sinon.
        :rtype: boolean
        """
        @timeout_decorator(3600)
        def graphic_accept():
            """
            Retourne True si c'est ok.
            Retourne False si c'est pas bon.
            Retourne Timeout si c'est indecis.
            """
            import raisin.application.hmi.dialog as dialog
            question =  "'%s' shouaite se connecter.\n" % client_id["username"] \
                        + "Il travail sur l'os '%s'.\n" % client_id["os_version"] \
                        + "Sur le PC '%s'.\n" % client_id["hostname"] \
                        + "Il est localise en '%s' a '%s'.\n" % (client_id["country"], client_id["city"]) \
                        + "Il pretend avoir l'adresse mac '%s'.\n" % client_id["mac"]
            try:
                return dialog.question_binaire(question, default=None, existing_window=None)
            except KeyboardInterrupt as e:
                raise TimeoutError from e

        with Printer("Ask to user for accept a new client...") as p:

            # On s'assure que l'utilisateur n'ai pas encore donne son avis.
            if is_a == True:
                p.show("The client is already accepted.")
                return True
            if is_a == False:
                p.show("This client is already baned.")
                return False

            # Si on peut lui demander graphiquement de suite, on le fait.
            import raisin.application.hmi as hmi
            if hmi.tkinter:
                try:
                    rep = graphic_accept() # On lui laisse 1 heure pour repondre.
                except TimeoutError:
                    rep = False
            else:
                rep = None

            # On enregistre ensuite le client dans les bases de donnees.
            if rep:
                with open(os.path.join(os.path.expanduser("~"),
                        ".raisin", "whitelisted.txt"), "a") as f:
                    f.write("%s %s\n" % (
                        client_id["mac"],
                        time.strftime("%Y-%m-%dT%H:%M:%S")))
                p.show("The client %s is now accepted." % client_id["mac"])
                if client_id["mac"] in self.waiting:
                    self.waiting.remove(client_id["mac"])
                return True
            else:
                with open(os.path.join(os.path.expanduser("~"),
                        ".raisin", "blacklisted.txt"), "a") as f:
                    f.write("%s %s %s\n" % (
                        client_id["mac"],
                        time.strftime("%Y-%m-%dT%H:%M:%S"),
                        "wait" if rep == None else "definitive"))
                if rep == False:
                    p.show("The client %s is now definitively baned." \
                        % client_id["mac"])
                    if client_id["mac"] in self.waiting:
                        self.waiting.remove(client_id["mac"])
                    return False

            # Enregistrement de ce client dans la liste d'attente.
            with open(os.path.join(os.path.expanduser("~"),
                    ".raisin", "waitlisted.txt"), "a") as f:
                f.write("%s %s\n" % (
                    time.strftime("%Y-%m-%dT%H:%M:%S"),
                    dumps(client_id)))

            # Envoi d'un mail.
            try:
                with open(os.path.join(os.path.expanduser("~"),
                        ".raisin", "last_mail.txt"), "r") as f:
                    last_mail = time.mktime(
                        time.strptime(f.read(), "%Y-%m-%dT%H:%M:%S\n"))
            except FileNotFoundError:
                last_mail = 0
            if time.time() - last_mail > 24*3600: # Si cela fait plus d'un jour qu'on a pas envoye de mail.
                with open(os.path.join(os.path.expanduser("~"),
                        ".raisin", "waitlisted.txt"), "r") as f:
                    waitings = [(
                        time.mktime(time.strptime(t, "%Y-%m-%dT%H:%M:%S")),
                        loads(c))
                        for t, c in [l.split() for l in f.readlines()]] # Les clients en attente.
                clients = [c for t, c in waitings[::-1] if t > last_mail] # Les nouveaux clients.
                message = "Des nouveaux clients attendent que vous les acceptiez.\n" \
                        + "Ce mail est envoye depuis:\n\t%s\n\n" % "\n\t".join(
                            ("%s: %s" % p for p in dict(identity).items())) \
                        + "Pour accepter un client tapez:\n" \
                        + "\t'%s -m raisin client --accept client_mac'\n" % sys.executable \
                        + "Pour refuser un client tapez:\n" \
                        + "\t'%s -m raisin client --exile client_mac'\n" % sys.executable \
                        + "Pour voir tous les clients en attente:\n" \
                        + "\t'%s -m raisin client status'\n" % sys.executable \
                        + "'client_mac' est l'adresse mac d'un client unique.\n" \
                        + "Voici la liste des.du nouveau.x client.s en attente:\n\n" \
                        + "%s" % "\n\n".join(
                            "\n".join("%s: %s" % p for p in c.items())
                            for c in clients)
                import raisin.communication.mail as mail
                mail.send(settings["account"]["email"], "raisin: client waiting", message)
                with open(os.path.join(os.path.expanduser("~"),
                        ".raisin", "last_mail.txt"), "w") as f:
                    f.write(time.strftime("%Y-%m-%dT%H:%M:%S\n"))
                del mail
            if client_id["mac"] in self.waiting:
                self.waiting.remove(client_id["mac"])
            return False

    def clean(self):
        """
        |==============================|
        | Suprime les clients decedes. |
        |==============================|

        Cela permet de faire un peu de menage.

        sortie
        ------
        :return: La liste des clefs rsa des clients morts.
        :rtype: list
        """
        with Printer("Cleaning up dead clients...") as p:
            morts = [pk for pk, cl in self.clients.items()
                if not cl["thread"].is_alive()]
            if morts:
                self.clients = {pk: cl for pk, cl in self.clients.items()
                    if pk not in morts}
                p.show("%d clients have just been exterminated." % len(morts))
            else:
                p.show("No genocide: everyone stays alive.")
            return morts

    def close(self):
        """
        Permet de fermer proprement les sockets.
        """
        with Printer("Shutdown the server..."):
            if hasattr(self, "clients"): # Si le graphe n'a pas echoue
                for client in self.clients.values():
                    try:
                        client["socket"].shutdown(socket.SHUT_RDWR) # Empeche imediatement les connections.
                        client["socket"].close() # Demande au socket de mourir.
                    except OSError:
                        pass
            if hasattr(self, "tcp_socket"): # Si le constructeur n'a pas echoue.
                self.tcp_socket.close()
            if hasattr(self, "tcp_socket_bis"): # Si le constructeur n'a pas echoue.
                if self.tcp_socket_bis:
                    self.tcp_socket_bis.close()


    def handle(self, client_socket, key):
        """
        |====================================|
        | Satisfait les besoins d'un client. |
        |====================================|

        Cette methode doit etre lancee dans un thread.
        Sinon elle bloquerait tout et seul le premier
        client serait servis.
        Cette methode est bloquante.

        entree
        ------
        :param client_socket: Socket tcp du client que l'on ecoute.
        :type client_socket: socket.socket
        :param key: Clef publique du client.
        :type key: str

        sortie
        ------
        :return: True si la discution s'est bien passee. False si il y a un qouac.
        :rtype: boolean
        """
        while True:
            # Traitement des messages.
            with Printer("Waiting for a reponse...") as p:
                try:
                    message = routing.receive(client_socket) # Fonction bloquante, attend un message.
                except NotCompliantError:
                    p.show("Not complient request.")
                    del self.clients[key]
                    return False
                except OSError:
                    p.show("Erreur avec le socket TCP.")
                    try:
                        client_socket.shutdown(socket.SHUT_RDWR)
                        client_socket.close()
                    except OSError:
                        pass
                    if key in self.clients:
                        del self.clients[key]
                    return False
                else: # Si le message est bien recu.
                    if message["type"] == "error": # Si le client boude.
                        p.show("The client is not happy: %s" % message["message"])
                        del self.clients[key]
                        return False

                    elif message["type"] == "question": # Si le client pose une question.
                        answer = request.answering(message, network=self.graph)
                        if answer["type"] == "error":
                            routing.send_error(client_socket, answer["message"])
                            p.show(answer["message"])
                            if key in self.clients:
                                del self.clients[key]
                            return False
                        routing.send_object(client_socket, answer)

                    elif message["type"] == "info": # Si le client se met a causer tout seul.
                        if "goodbye" in message: # Si le client veut metre fin a la discution
                            p.show("The client say: %s" % message["goodbye"])
                            if key in self.clients:
                                del self.clients[key]
                            return True
                        p.show("ERROR: The client send %s." % repr(message))
                        error = "L'information %s n'est pas recevable." % repr(message)
                        routing.send_error(client_socket, error)
                        return False

                    elif message["type"] == "result":
                        raise NotImplementedError("Envoyer le resultat au destinataire.")
                        # Si le destinataire il est connecte, allors on lui envoi.
                        # Sinon, aller consulter la table de routage (mise a jour de la table.)

                    else:
                        p.show("ERROR: The client send a %s." % repr(message["type"]))
                        error = "Le type %s n'est pas reconnaissable." % repr(message["type"])
                        routing.send_error(client_socket, error)
                        return False

    def is_accepted(self, mac):
        """
        |====================================|
        | S'assure que le client est fiable. |
        |====================================|

        Ne pose aucune question a l'utilisateur, retourne sans attendre.

        entree
        ------
        :param mac: C'est l'adresse mac du client qui passe a la casserole.
        :type mac: str

        sortie
        ------
        :return: True si le client a le droit de se connecter, False sinon.
        :rtype: boolean
        """
        with Printer("Testing if a pecific client is accepted...") as p:
            # Client deja en liste noire?
            blacklisted = os.path.join(os.path.expanduser("~"), ".raisin", "blacklisted.txt")
            if os.path.exists(blacklisted):
                with open(blacklisted, "r", encoding="utf-8") as f:
                    if mac in (l.split()[0] for l in f.readlines()):
                        p.show("The client %s is blacklisted." % mac)
                        return False

            # Client deja en liste blanche?
            whitelisted = os.path.join(os.path.expanduser("~"), ".raisin", "whitelisted.txt")
            if os.path.exists(whitelisted):
                with open(whitelisted, "r", encoding="utf-8") as f:
                    if mac in (l.split()[0] for l in f.readlines()):
                        p.show("The client %s is accepted." % mac)
                        return True

            # Faut-il accepter tout le monde?
            if settings["server"]["accept_new_client"]:
                p.show("The client %s is automaticaly accepted." % mac)
                return True

            # Client deja en attente?
            if mac in self.waiting:
                p.show("The client %s is already on hold." % mac)
                return False
            self.waiting.add(mac)
            p.show("Maybe, we must ask the question.")
            return None

    def put_graph(self, new_graph):
        """
        Met à jour le graph dans le réseau.
        """
        raise NotImplementedError

    def prevent(self, ip_client, port_client, client_socket):
        """
        |===================================|
        | Harcelle le client pour s'assurer |
        | qu'il soit de bonne fois.         |
        |===================================|

        * Des qu'un client shouaite se connecter au serveur,
        la fonction principale du serveur expedie le client
        dans cette methode de facon a etre rapidement disponible
        pour en servir de nouveaux.

        :param ip_client: L'adresse ip du client.
        :type ip_client: str
        :param port_client: Le port de sortie du client.
        :type port_client: int
        :param client_socket: Socket tcp du client que l'on ecoute.
        :type client_socket: socket.socket

        :raises: Exception si le client refuse de se soumetre totalement.
        :return: ...
        """
        try:
            with Printer("Un client d'ip %s se connecte via le port %d..." \
                    % (ip_client, port_client)) as p:
                # On s'assure qu'il n'y ai pas trop de monde.
                if len(self.clients) >= settings["server"]["listen"]:
                    routing.send_error(client_socket,
                        "There are already too many connections.")
                    raise ConnectionRefusedError(
                        "Customer expelled because there are already "
                        "too many connections.")

                with Printer("We make some tests about the customer..."):

                    # Recuperation adresse mac.
                    try:
                        mac = routing.receive(client_socket, timeout=600)
                    except socket.timeout:
                        routing.send_error(client_socket,
                            "You are too slow to send your mac address.")
                        raise TimeoutError("Customer expelled because "
                            "he is too slow to send his mac address.")
                    except NotCompliantError:
                        raise ThreatenError(
                            "Customer expelled because he is threatening.") # Le message d'erreur est deja envoye depuis 'receive'
                    if checks.check_info(mac) or "mac" not in mac:
                        routing.send_error(client_socket, "He did not give his mac address.")
                        raise ThreatenError("Customer expelled because "
                            "he did not give his mac address.")

                    # Recuperation de la clef publique.
                    if 1: # Il faudrait regarder si on ne connait pas deja la clef publique a partir de mac.
                        public_key = request.ask_public_key(client_socket)
                        if not public_key:
                            raise ThreatenError("Customer expelled "
                                "because we don't have his public key.") # Le message d'erreur est deja envoye.

                    # On s'assure qu'il n'usurpe pas l'identitee d'un autre.
                    if settings["server"]["force_authentication"]:
                        if not request.ask_challenge(client_socket, public_key):
                            raise ThreatenError(
                                "Customer expelled because he's a crook.") # Le message d'erreur est deja envoye.

                    # Recuperation de l'identifiant.
                    if 1: # Il faudrait regarder si on ne connait pas deja l'identifiant du client a aprtir de l'adresse mac.
                        client_id = request.ask_identity(client_socket)
                        if not client_id:
                            raise ThreatenError("Customer expelled because "
                                "we don't have his identity.") # Le message d'erreur est deja envoye.

                    # Verification qu'il appartient au bon cluster.
                    if client_id["network_name"] != settings["server"]["network_name"]:
                        routing.send_error(client_socket, "You are not in the same cluster.")
                        raise ThreatenError("Customer expelled because he is not in the same cluster.")

                    # On s'assure que ce client est le bienvenu.
                    autorization = self.is_accepted(mac["mac"])
                    if autorization == None: # Si il faut demander l'avis de l'utilisateur.
                        threading.Thread(
                            target=self.accept,
                            args=(client_id, autorization)).start() # On pose la question a l'utilisateur
                        routing.send_error(client_socket,
                            "You have to wait for user approval.")
                        raise ThreatenError("Customer expelled because he "
                            "have to wait for user approval.") # Mais on attend pas qu'il reponde.
                    elif autorization == False: # Si il faut le virer.
                        routing.send_error(client_socket, "You are blacklisted.")
                        raise ThreatenError("Customer expelled because he "
                            "is blacklisted.")

                    # On s'assure que le client n'est pas deja connecte.
                    self.clean() # On netoie son potentiel cadavre.
                    if public_key in self.clients:
                        routing.send_error(client_socket,
                            "you are already connected.")
                        raise ThreatenError("Customer expelled because he "
                            "is already connected.")

                # On lui shouaite la bienvenue.
                request.send_welcome(client_socket)

        except Exception: # Si il y a eu un pepin avec ce client.
            return # On le laisse tomber.

        else: # Si le client semble par trop vilain.
            # On le met en file d'attente pour qu'il soit pris en charge.
            self.client_queue.put(("ok_client",
                {"mac": mac["mac"],
                 "port_client": port_client,
                 "ip_client": ip_client,
                 "public_key": public_key,
                 "client_socket": client_socket,
                 "public_key": public_key}))

    def start(self):
        """
        |===============================|
        | Acceuil les nouveaux clients. |
        |===============================|

        * Point d'entree du serveur. C'est cette methode qui le demarre.

        Si le client est accepte, il est ajoute dans les clients connectes
        et un nouveau processus est cree rien que pour lui.
        Comme c'est ici que les clients debarquent tout d'abord, on est extremement mefiant
        envers eux pour une question de securitee. Plein de tests dont fait de
        facon a s'assurer qu'ils soit bien en regles.
        """
        def listen_socket(self):
            """
            Ajoute les nouveau clients a la file lorsqu'ils arrivent.
            """
            while True:
                element = self.tcp_socket.accept()
                self.client_queue.put(("new_client", element))

        def listen_socket_bis(self):
            """
            Ajoute les nouveau clients a la file lorsqu'ils arrivent.
            """
            while True:
                element = self.tcp_socket_bis.accept()
                self.client_queue.put(("new_client", element))

        threading.Thread(target=listen_socket, args=(self,)).start()
        if self.tcp_socket_bis:
            threading.Thread(target=listen_socket_bis, args=(self,)).start()

        while True:
            nature, element = self.client_queue.get() # On attend qu'un evenement se produise.
            if nature == "new_client": # Si un tout nouveau client essaie de se connecter.
                client_socket, info = element # On ne fait pas directement
                ip_client = info[0]           # client_socket, (ip_client, port_client)
                port_client = info[1]         # car le deuxieme tuple contient parfois 4 elements.
                threading.Thread(
                    target=self.prevent,
                    args=(ip_client, port_client, client_socket)
                    ).start()
            elif nature == "ok_client": # Si le client n'est pas nouveau et qu'il vient de franchir le test
                self.clients[element["public_key"]] = { # Alors on cre un processus rien que pour lui.
                    "mac": element["mac"],
                    "port": element["port_client"],
                    "ip": element["ip_client"],
                    "socket": element["client_socket"],
                    "thread": multiprocessing.Process(
                        target=self.handle,
                        args=(element["client_socket"], element["public_key"]))}
                self.clients[element["public_key"]]["thread"].start()
            else:
                raise ValueError("La nature des client ne peut etre que "
                    "'new_client' ou 'ok_client'. not %s." % repr(nature))

    def __del__(self):
        """
        |==========================|
        | Aide le ramasse-miettes. |
        |==========================|
        """
        self.close()


def main():
    """
    Lance le serveur.
    """
    Server().start()

if __name__ == "__main__":
    main()
