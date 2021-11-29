#!/usr/bin/env python
# coding=utf-8

import parse
import isExists
from parapheur.parapheur import pprint, parse, isExists
from urlparse import urlparse
import socket
import connect
import execute
import os

defaut_iparapheur_root = "/opt/iParapheur/"
tomcat_conf_subdir = "tomcat/shared/classes/"
alfresco_conf_file = "alfresco-global.properties"
queries = []
query_root = "database/queries/orphans/"
exit_code = 0

# Get data from alfresco-global.properties for connecting database
isExists.isexistsdirectory(defaut_iparapheur_root, False)
isExists.isexistssubdir(defaut_iparapheur_root, tomcat_conf_subdir, False)
isExists.isexistsfile(defaut_iparapheur_root + tomcat_conf_subdir, alfresco_conf_file, False)
alfresco_conf = parse.parse(defaut_iparapheur_root + tomcat_conf_subdir + alfresco_conf_file)

# Get the dabatase connexion
cnx = connect.connect(alfresco_conf)

# Execute queries
query_files = os.listdir(query_root)
for file in query_files:
    f = open(query_root + file, "r")
    query = f.readline()
    queries.append(query)
queries_responses = execute.execute(cnx, queries)

# Return exit code for both queries
for response in queries_responses:
    if response != 0:
        exit_code = 1

if exit_code == 1:
    print(
        "Il y a des noeuds orphelins en base de données. Vous pouvez utilisez la commande 'ph-ipclean' pour les "
        "supprimer et générer les index")
else:
    print("Il n'y a pas de noeud orphelin en base de données.")

exit(exit_code)
