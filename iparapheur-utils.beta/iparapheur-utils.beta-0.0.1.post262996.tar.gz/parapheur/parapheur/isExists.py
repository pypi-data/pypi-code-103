# coding=utf-8
# module Parapheur
import os
from parapheur.parapheur import pprint


def isexistsdirectory(repertoire, verbose=False):
    if os.path.exists(repertoire):
        if verbose:
            pprint.header("#", False, ' ')
            pprint.info("Répertoire", False, ' ')
            pprint.info(repertoire.ljust(35), True, ' ')
            pprint.success('{:>10s}'.format("OK"), True)
        return True
    else:
        pprint.header("#", False, ' ')
        pprint.info("Répertoire", False, ' ')
        pprint.info(repertoire.ljust(35), True, ' ')
        pprint.warning('{:>10s}'.format("absent"))
        return False


def isexistssubdir(repertoire, sousrep, verbose=False):
    if os.path.exists("{0}/{1}".format(repertoire, sousrep)):
        if verbose:
            pprint.header("#", False, ' ')
            pprint.info("  subdir", False, ' ')
            pprint.info(sousrep.ljust(37), True, ' ')
            pprint.success('{:>10s}'.format("OK"), True)
        return True
    else:
        pprint.header("#", False, ' ')
        pprint.info("  subdir", False, ' ')
        pprint.info(sousrep.ljust(37), True, ' ')
        pprint.warning('{:>10s}'.format("absent"))
        return False


def isexistsfile(repertoire, fichier, verbose=False):
    if os.path.exists("{0}/{1}".format(repertoire, fichier)):
        if verbose:
            pprint.header("#", False, ' ')
            pprint.info(" fichier", False, ' ')
            pprint.info(fichier.ljust(37), True, ' ')
            pprint.success('{:>10s}'.format("OK"))
        return True
    else:
        pprint.header("#", False, ' ')
        pprint.info(" fichier", False, ' ')
        pprint.info(fichier.ljust(37), True, ' ')
        pprint.warning('{:>10s}'.format("absent"))
        return False
