#!/usr/bin/env python3

"""
|===========================================|
| C'est la partie qui permet de             |
| contacter des serveur et de les harceler. |
|===========================================|

Ce script permet de se connecter a des serveurs tcp
et de leur demander des services. C'est la partie de raisin
qui permet d'envoyer ailleur le travail a faire.

Ce fichier est fortement influance par ce lien:
    https://www.neuralnine.com/tcp-chat-in-python/
"""

import ipaddress
import socket
import select
import sys
import threading
import time

from ..tools import Printer, identity
from ..errors import *
from . import request, routing, dns as dns_tools


class Client(threading.Thread):
    """
    |===================================|
    | Client tcp lie a un seul serveur. |
    |===================================|

    Il faut creer un objet par connection.

    exemple
    -------
    :Example:
    >>> from raisin.communication import tcp_client
    >>> c = tcp_client.Client("adresse_ip", 20001) # Il faut qu'il y ai un serveur en ecoute.
    >>> c.start()
    """
    def __init__(self, ip, port):
        """
        |=========================|
        | Se connecte au serveur. |
        |=========================|

        * Ne retourne qu'apres que le serveur soit pret a ecouter.

        entree
        ------
        :param ip: Adresse ip (v4 ou v6) ou dns du serveur.
        :type ip: str
        :param port: Port d'ecoute du serveur.
        :type port: int
        """
        assert isinstance(ip, str), \
            "L'ip doit etre une chaine de caractere, pas un %s." \
            % type(ip).__name__
        assert isinstance(port, int), \
            "Le port doit etre un entier, pas un %s." \
            % type(port).__name__
        assert port >= 0, \
            "Le port doit etre positif. Or il vaut %d." % port

        threading.Thread.__init__(self)

        self.port = port # Port du serveur.
        self.version = None # Version ipv4 ou ipv6
        self.server_in_lan = None # Booleen qui permet de dire si le serveur que l'on
                                  # cherche a joindre est sur le meme reseau local que ce client.
        self.tcp_socket = None # Socket tcp du serveur.
        self.answer = None # La reponse du serveur.

        with Printer("Initialisation of client ip %s port %d..." % (ip, port)) as p:
            # Cas connection via nom de domaine.
            self.ip = dns_tools.is_domain(ip)
            if self.ip:
                p.show("Domain %s translated in %s." % (ip, self.ip))
            self.ip = self.ip if self.ip else ip

            # Cas d'une ipv6 ou d'une ipv4.
            if dns_tools.is_ipv6(self.ip):
                self.version = 6
            elif dns_tools.is_ipv4(self.ip):
                self.version = 4
            else:
                raise ValueError("Entree incorrecte, ce n'est ni "
                    "une ip, ni un nom de domaine accessible.")
            p.show("Server ipv%d: %s." % (self.version, self.ip))

            # Recherche reseau local ou pas.
            self.server_in_lan = ipaddress.ip_address(self.ip).is_private
            if self.server_in_lan:
                p.show("Server in local network (LAN).")
            else:
                p.show("Server non local (WAN).")
            p.show("Port: %d." % self.port)

            # Connection et initialisation.
            try:
                self.tcp_socket = socket.create_connection((self.ip, self.port))
            except OSError as err:
                self.tcp_socket = None
                raise ConnectionError(*err.args) from err
            self._initialization()

    def _initialization(self):
        """
        |===============================|
        | Etabli les premiers dialogues |
        | avec le serveur.              |
        |===============================|

        Cette methode est appellee par le constructeur.
        Elle permet d'envoyer les informations que demande
        le serveur avant d'accepter le client.
        """
        with Printer("Wait for the first automatic exchanges...") as p:
            request.send_mac(self.tcp_socket) # On envoi l'adresse mac.
            while True:
                message = routing.receive(self.tcp_socket) # On attend la reponse du serveur.

                if message["type"] == "info" and "welcome" in message:
                    p.show("The server say: %s." % repr(message["welcome"]))
                    break

                if message["type"] == "error":
                    p.show("The server say: %s" % repr(message["message"]))
                    raise ConnectionError(message["message"])

                routing.send_object(self.tcp_socket, request.answering(message))

    def run(self):
        """
        |====================|
        | Ecoute le serveur. |
        |====================|

        Methode special appelle par la classe parente
        au moment ou l'on fait: self.start().
        """
        while True:
            # Traitement des messages.
            with Printer("Waiting for a reponse...") as p:
                try:
                    message = routing.receive(self.tcp_socket) # On attend la reponse du serveur.
                except NotCompliantError as err:
                    p.show("Not complient request.")
                    raise err from err
                except OSError as err:
                    p.show("Erreur avec le socket TCP.")
                    try:
                        self.tcp_socket.shutdown(socket.SHUT_RDWR)
                        self.tcp_socket.close()
                    except OSError:
                        pass
                    raise err from err

                # Si le message est bien recu.
                if message["type"] == "error": # Si le serveur fait la gueule.
                    self.answer = message
                    try:
                        self.tcp_socket.shutdown(socket.SHUT_RDWR)
                        self.tcp_socket.close()
                    except OSError:
                        pass
                    p.show(message["message"])
                    raise OSError(message["message"])

                elif message["type"] == "answer": # Si le repond a une question
                    self.answer = message

                elif message["type"] == "question": # Si le serveur nous pose une question.
                    answer = request.answering(message)
                    if answer["type"] == "error":
                        routing.send_error(self.tcp_socket, answer["message"])
                        p.show(answer["message"])
                        raise OSError(answer["message"])
                    routing.send_object(self.tcp_socket, answer)

                elif message["type"] == "info":
                    if "goodbye" in message:
                        p.show("The server say: %s" % message["goodbye"])
                        break
                    raise NotImplementedError("La gestion des infos n'est pas codee.")

                else: # Si le serveur pete un cable
                    error = "Le type %s n'est pas reconnaissable." % repr(message["type"])
                    routing.send_error(self.tcp_socket, error)
                    raise NotCompliantError(error)

    def send(self, message):
        """
        |===============================|
        | Pose une question au serveur. |
        |===============================|

        entree
        ------
        :param message: La question a poser au serveur.
            Attention le serveur est tres capricieux,
            il faut que les messages soient tres polis.
        :type message: dict

        sortie
        ------
        :return: La reponse du serveur.
        :rtype: dict
        :raises OSError: Si le serveur n'est pas satisfait
            de la question ou si il y a un probleme de communication.
        """
        self.answer = None
        routing.send_object(self.tcp_socket, message)
        wait = 0
        while not self.answer:
            time.sleep(wait)
            wait = max(0.1, wait + 1/1199) # Pour atteindre wait=0.1 apres 60 secondes.
        if self.answer["type"] == "error":
            raise OSError(self.answer["message"])
        return self.answer

    def ask_challenge(self, public_key):
        """
        :seealso: ``raisin.communication.request.ask_challenge``
        """
        return request.ask_challenge(self.tcp_socket, public_key)

    def ask_network(self):
        """
        :seealso: ``raisin.communication.request.ask_network``
        """
        return request.ask_network(self.tcp_socket)

    def ask_identity(self):
        """
        :seealso: ``raisin.communication.request.ask_identity``
        """
        return request.ask_identity(self.tcp_socket)

    def ask_public_key(self):
        """
        :seealso: ``raisin.communication.request.ask_public_key``
        """
        return request.ask_public_key(self.tcp_socket)

    def close(self):
        """
        |=============================|
        | Met fin a la communication. |
        |=============================|
        """
        if self.tcp_socket is None:
            return
        request.send_goodbye(self.tcp_socket)
        try:
            self.tcp_socket.shutdown(socket.SHUT_RDWR)
            self.tcp_socket.close()
        except OSError:
            pass

    def __del__(self):
        """
        |==========================|
        | Aide le ramasse-miettes. |
        |==========================|
        """
        self.close()
