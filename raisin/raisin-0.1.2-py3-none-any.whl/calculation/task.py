#!/usr/bin/env python3

"""
|=======================================================|
| Excecution d'une tache avec recuperation du contexte. |
|=======================================================|

Permet d'executer de facon aveugle un calcul bete et mechant.
Peut etre soit apele directement en cas de non parralelisation mais
dans la plus-part des cas, c'est ``raisin.calculation.task_management``
qui gere les taches d'un point de vu 'bas niveau'.
"""

import os
import time

import psutil

from raisin.tools import timeout_decorator, identity


class Task:
    """
    ** Decorateur dynamique. **
    ---------------------------

    Notes
    -----
    La gestion de l'utilisation du CPU ne se fait pas ici
    c'est le processus parent qui doit gerer cela.
    """
    def __init__(self, target, task_timeout):
        """
        Notes
        -----
        Il n'y a pas de verification sur les entrees
        car l'utilisateur n'est pas cence y metre les pieds.

        Parameters
        ----------
        target : callable
            La fonction que l'on decore.
        task_timeout : number
            Le temps maximum d'execution avant de lever
            une exception de type TimeoutError
        """
        self.target = target
        self.task_timeout = task_timeout
        self.proc = psutil.Process(pid=os.getpid()) # Permet d'avoir des informations.

    def __call__(self, *args, **kwargs):
        """
        ** Evalue la fonction et capture son contexte. **

        Returns
        -------
        dict
            Ce dictionaire contient le resultat ou l'erreur de la fonction
            ``self.target`` mais aussi plein d'autre informations.
            La forme exacte du dictionaire est decrite par le sous-champs
            'results' de la methode ``raisin.map_main.Map.get``.
        """
        result = {}
        start_cpu_time = self.proc.cpu_times().user

        try:
            result["value"] = timeout_decorator(self.task_timeout)(self.target)(*args, **kwargs)
        except Exception as e:
            result["value"] = None
            result["error"] = e
        else:
            result["error"] = None

        result["cpu_time"] = self.proc.cpu_times().user - start_cpu_time
        result["host"] = dict(identity)

        return result

