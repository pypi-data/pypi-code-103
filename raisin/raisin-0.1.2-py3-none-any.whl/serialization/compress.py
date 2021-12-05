#!/usr/bin/env python3

"""
|=================================================|
| Compression sans perte inteligente des donnees. |
| N'est pas encore implementee                    |
|=================================================|
"""

def compress_gen(gen, **kwargs):
    """
    |====================================|
    | Compresse  sans perte les donnees. |
    |====================================|

    * N'effecte aucune verifications sur les entrees.

    Parameters
    ----------
    :param gen: Generateur de paquet d'octet ayant deja une taille
        d'environ BUFFER_SIZE. Ce sont les donnees a compresser.
    :type gen: generator
    :param compresslevel: Taux relatif de compression:
        -1: Intelligente, compresse au mieu
            en fonction du debit demande.
            Si 'parallelization_rate' >= 0
        2: Legere compression, la plus rapide
           en temps de calcul.
        3: Legere compression qui maximise
           le ratio 'taille_gagnee/temps'.
        4: Moyenne compression qui vise un ratio
           environ egal a 95% du ratio maximum.
        5: Compression maximale qui ne se preocupe pas du temps.
    :type compresslevel: int
    :param parallelization_rate: Taux de paralelisation entre cpu.
        0: Aucune parallelisation, tout est excecute
           dans le processus courant.
        1: Pseudo parallelisation, reparti les operations
           dans des threads du module 'threading'.
        2: Legere parallelisation, utilise les differents coeurs
           de la machine avec le module 'multiprocessing'.
    :type parallelization_rate: int

    Returns
    -------
    :return: cede les paquets compresses.
    :rtype: bytes
    """
    yield from gen
