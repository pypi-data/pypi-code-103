#!/usr/bin/env python
# coding=utf-8

from parapheur.parapheur import pprint  # Colored printer
import sys

req_version = (3, 0)
cur_version = sys.version_info
isp3 = cur_version >= req_version
if isp3:
    # noinspection PyCompatibility,PyUnresolvedReferences
    import configparser as ConfigParser
else:
    # noinspection PyCompatibility
    import ConfigParser
import isExists
import io

defaut_iparapheur_root = "/opt/iParapheur"


def check_isexists_alfrescoglobal():
    # Alfresco-global.properties
    isExists.isexistsdirectory(defaut_iparapheur_root)
    isExists.isexistssubdir(defaut_iparapheur_root, "tomcat/shared/classes")
    return isExists.isexistsfile("{0}/tomcat/shared/classes"
                                 .format(defaut_iparapheur_root),
                                 "alfresco-global.properties")


def parse(conf):
    if not check_isexists_alfrescoglobal():
        pprint.error("BAD")
        sys.exit()
    CONFIG_PATH = conf.format(defaut_iparapheur_root)
    with open(CONFIG_PATH, 'r') as f:
        config_string = '[Parapheur]\n' + f.read()
    config_fp = io.BytesIO(config_string)
    config = ConfigParser.RawConfigParser()
    config.readfp(config_fp)

    return config
