#!/usr/bin/env python
# coding=utf-8

"""
AGPL-3.0-only Copyright (c) 2016-2021, Libriciel SCOP
Initiated and by Libriciel SCOP

contact@libriciel.coop
"""

import hashlib
import io
import multiprocessing
import os   # et tous pour un
import glob
import platform
import socket
import ssl
import subprocess
import sys
import time
import re
import xml.etree.ElementTree as ET


from urlparse import urlparse

# import MySQLdb
import pymysql.cursors
import requests
# from ..exceptions import SSLError
from pkg_resources import parse_version
# from pymysql.constants import ER

from parapheur.parapheur import pprint  # Colored printer

req_version = (3, 0)
cur_version = sys.version_info
isp3 = cur_version >= req_version
# pprint.log(cur_version)

if isp3:
    # noinspection PyCompatibility,PyUnresolvedReferences
    import configparser as ConfigParser
else:
    # noinspection PyCompatibility
    import ConfigParser

__author__ = 'Stephane Vast'
__version__ = '0.9.38'

defaut_install_depot = "/opt/_install"
defaut_iparapheur_root = "/opt/iParapheur"
versionIP_minimum = "4.6.0"
mysqluser = "alf"
mysqlpwd = ""
mysqlbase = ""
linux_family = ""


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


def isfileproperlydeleted(repertoire, fichier):
    pprint.header("#", False, ' ')
    pprint.info(" fichier", False, ' ')
    pprint.info(fichier.ljust(37), True, ' ')
    if not os.path.exists("{0}/{1}".format(repertoire, fichier)):
        pprint.success('{:>10s}'.format("absent, OK"))
        return True
    else:
        pprint.error('{:>10s}'.format("Present !"), True)
        return False


def isfolderfromtoday(repertoire):
    pprint.header("#", False, ' ')
    pprint.info(" date de dossier", False, ' ')
    pprint.info(repertoire.ljust(29), True, ' ')

    datetime_creation = os.stat(repertoire).st_ctime
    datetime_now = time.time()

    if (datetime_now - datetime_creation) < 86400:
        pprint.success('{:>10s}'.format("OK"), True)
        return True
    else:
        pprint.error('{:>10s}'.format("KO"))
        return False


def istextinfile(file_to_test, text, verbose=False):
    with open(file_to_test, 'r') as f_open:
        filedata = f_open.read()

    if text in filedata:
        if verbose:
            pprint.header("#", False, ' ')
            pprint.info(" contenu du fichier", False, ' ')
            pprint.info(os.path.basename(file_to_test).ljust(26), True, ' ')
            pprint.success('{:>10s}'.format("OK"), True)
        return True
    else:
        pprint.header("#", False, ' ')
        pprint.info(" contenu du fichier", False, ' ')
        pprint.info(os.path.basename(file_to_test).ljust(26), True, ' ')
        pprint.error('{:>10s}'.format("KO"))
        return False


def which(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def showtheheader():
    pprint.header('=' * 60)
    daText = "# ph-check v" + __version__
    pprint.header('{:20s}'.format(daText),
                  False, ' ')
    pprint.log("i-Parapheur", True, ' ')
    pprint.header("    résultats:", False, ' ')
    pprint.success("OK", True, ' ')
    pprint.warning("warn", True, ' ')
    pprint.error("Fail", True)
    pprint.header("# ")


# TODO TESTS
'''     Hardware    : taille Disque ?
        MySQL       : version? .... / NeSaitPas , local/déporté
        LibreOffice : version? .... / NeSaitPas
    Pour i-Parapheur, sécurité:
        Fournisseur certificats HTTPS (web,WS): ... , ... / NeSaitPas
        Date d'expiration cert. HTTPS (web,WS): ... , ... / NeSaitPas
        Version LiberSign : .....  / NeSaitPas	'''


def check_hardware():
    pprint.header("#", False, ' ')
    pprint.log("---- Check pre-requis systeme ----", True)

    pprint.header("#", False, ' ')
    pprint.info("Nombre de CPU disponibles (minimum 4)".ljust(46), False, ' ')
    nbcpu = multiprocessing.cpu_count()
    if nbcpu >= 4:
        pprint.success('{:>10d}'.format(nbcpu), True)
    elif nbcpu >= 2:
        pprint.warning('{:>10d}'.format(nbcpu))
    else:
        pprint.error('{:>10d}'.format(nbcpu))

    pprint.header("#", False, ' ')
    pprint.info("Taille Memoire totale (minimum 8 Go)".ljust(46), False, ' ')
    mem_bytes = os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES')
    mem_gib = mem_bytes / (1024. ** 3)  # e.g. 3.74
    if mem_gib >= 7.5:
        pprint.success('{:>7.2f} Go'.format(mem_gib), True)
    elif mem_gib > 5.75:
        pprint.warning('{:>7.2f} Go'.format(mem_gib))
    else:
        pprint.error('{:>7.2f} Go'.format(mem_gib))

    pprint.header("#", False, ' ')
    pprint.info("Plateforme {0} : architecture {1}".format(os.uname()[0],
                os.uname()[4]).ljust(46), False, ' ')
    l_arch = platform.architecture()[0]
    if l_arch == "64bit":
        pprint.success('{:>10s}'.format(l_arch), True)
    else:
        pprint.error('{:>10s}'.format(l_arch), True)
        pprint.error("Erreur: Le systeme doit etre 64bit pour recevoir"
                     " i-Parapheur. STOP", True)
        sys.exit()
    # pprint.log(platform.platform())
    # pprint.log(platform.release())
    # pprint.log(platform.system()) # Linux
    # pprint.log(platform.version())
    linux_family = 'inconnu'
    pprint.header("#", False, ' ')
    # pprint.log(platform.linux_distribution())  #('Ubuntu', '16.04', 'xenial')
    pprint.info("Distribution: {0} {1} ({2})".format(
        platform.linux_distribution()[0],
        platform.linux_distribution()[1],
        platform.linux_distribution()[2]).ljust(46), False, ' ')
    if platform.linux_distribution()[0] == 'Ubuntu':
        linux_family = 'Ubuntu'
        if platform.linux_distribution()[1] == '20.04':
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1] == '18.04':
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1] == '16.04':
            pprint.warning('{:>10s}'.format("obsolete"), True)
        else:
            pprint.error('{:>10s}'.format("non conforme"), True)
    elif platform.linux_distribution()[0] == 'debian':
        linux_family = 'Debian'
        if platform.linux_distribution()[1].startswith('9'):
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1].startswith('8'):
            pprint.error('{:>10s}'.format("obsolete"), True)
        else:
            pprint.error('{:>10s}'.format("non conforme"), True)
    elif platform.linux_distribution()[0] == 'CentOS Linux':
        linux_family = 'CentOS'
        if platform.linux_distribution()[1].startswith('8'):
            pprint.success('{:>10s}'.warning("Fin de vie"), True)
        elif platform.linux_distribution()[1].startswith('7'):
            pprint.success('{:>10s}'.format("OK"), True)
        else:
            pprint.error('{:>10s}'.format("non conforme"), True)
    elif platform.linux_distribution()[0] == 'Red Hat Enterprise Linux Server':
        linux_family = 'redhat'
        if platform.linux_distribution()[1].startswith('8'):
            pprint.success('{:>10s}'.format("OK"), True)
        elif platform.linux_distribution()[1].startswith('7'):
            pprint.success('{:>10s}'.format("OK"), True)
        else:
            pprint.error('{:>10s}'.format("non conforme"), True)
    else:  # Les autres cas 'SuSE', 'Gentoo', 'mandrake'
        pprint.error('{:>10s}'.format("inconnu"), True)

    pprint.header("#", False, ' ')
    pprint.info("swappiness (valeur <=10)".ljust(46), False, ' ')
    PROCFS_PATH = "/proc/sys/vm/swappiness"
    if os.path.isfile(PROCFS_PATH) and os.access(PROCFS_PATH, os.R_OK):
        myfile = open(PROCFS_PATH, 'r')
        for line in myfile:
            swappiness = int(line.rstrip("\n"))
            if swappiness > 10:
                pprint.warning('{:>10d}'.format(swappiness), True)
            else:
                pprint.success('{:>10d}'.format(swappiness), True)
        myfile.close()
    return linux_family
#  pprint.log(os.getlogin())
#  pprint.log(os.uname())


def check_server_socket(address, port, verbose):
    s = socket.socket()
    try:
        s.connect((address, port))
        # print "Connected to %s on port %s" % (address, port)
        s.close()
        return True
    except socket.error as e:
        if verbose:
            print("Connection to %s:%s failed: %s" % (address, port, e))
        return False


def issitereachable(theurl):
    pprint.header("#", False, ' ')
    pprint.info(" {0}".format(theurl).ljust(46), False, ' ')

    try:
        # The timeout parameter is set to 5 seconds
        # The HTTPS cert verification is out of scope for that test
        if theurl.startswith('https://'):
            requests.packages.urllib3.disable_warnings()
            response = requests.get(theurl, verify=ssl.CERT_NONE, timeout=5)
        else:
            response = requests.get(theurl, timeout=5)

        if not response.ok:
            pprint.error('{:>10s}'.format("Erreur"), True)
            pprint.error("Erreur lors de la requête {0}: Code d'erreur {1}".
                         format(theurl, response.status_code),
                         True)
            pprint.error(response.getvalue())
        else:
            pprint.success('{:>10s}'.format("OK"), True)

    except requests.exceptions.Timeout as toe:
        pprint.error('{:>10s}'.format("Erreur"), True)
        pprint.error("Erreur lors de la requête {0}: Time-out {1}".
                     format(theurl, toe))
    except requests.exceptions.ConnectionError as cee:
        pprint.error('{:>10s}'.format("Erreur"), True)
        pprint.error("Erreur de connexion à {0}: {1}".
                     format(theurl, cee))


# besoin HTTP/HTTPS sortant, accès http://crl.adullact.org validca.libriciel.fr
# http://libersign.libriciel.fr
def check_network_needed_basic():
    pprint.header("#", False, ' ')
    pprint.log("---- Check pre-requis accès internet ----", True)
    issitereachable("http://crl.adullact.org")
    issitereachable("http://validca.libriciel.fr")
    issitereachable("https://validca.libriciel.fr")
    issitereachable("https://libersign.libriciel.fr/extension.xpi")


def check_network_needed_new():
    pprint.header("#", False, ' ')
    pprint.log("---- Check accès à entretien services ----", True)
    issitereachable("https://nexus.libriciel.fr")
    issitereachable("https://sentry.libriciel.fr")
    issitereachable("https://bootstrap.pypa.io")
    issitereachable("https://pypi.org")


def check_mandatory_command(thecommand, verbose=False):
    if which(thecommand):
        if verbose:
            pprint.header("#", False, ' ')
            pprint.info("Commande : {0}".format(thecommand).ljust(46),
                        False, ' ')
            pprint.success('{:>10s}'.format("OK"))
    else:
        pprint.header("#", False, ' ')
        pprint.info("Commande : {0}".format(thecommand).ljust(46), False, ' ')
        pprint.error('{:>10s}'.format("Absent"), True)


def check_required_software(verbose=False):
    pprint.header("#", False, ' ')
    pprint.log("---- Check pre-requis logiciels selon manuel ----", True)

    # if isexistsdirectory(defaut_install_depot):
    #     isexistssubdir(defaut_install_depot, "confs")
    if not isexistsdirectory(defaut_iparapheur_root):
        pprint.error("Erreur: Le répertoire {0} doit être présent. STOP".
                     format(defaut_iparapheur_root), True)
        sys.exit()

    da_commands = ['at', 'tar', 'crontab', 'unzip', 'mailx', 'openssl',
                   'mysql', 'mysqldump', 'mysqlcheck', 'killall']
    for to_test in da_commands:
        check_mandatory_command(to_test, verbose)
    badGuess = barelyGuess_iParapheur_version_from_AMP(defaut_iparapheur_root)
    if badGuess != 'inconnu':
        if parse_version("4.5.2") <= parse_version(badGuess) \
           and parse_version(badGuess) < parse_version("4.7.0"):
            da_commands45 = ['/opt/jdk1.8.0_161/bin/java']
            for to_test in da_commands45:
                check_mandatory_command(to_test)
        if parse_version("4.6.0") <= parse_version(badGuess):
            da_commands46 = ['redis-server']
            for to_test in da_commands46:
                check_mandatory_command(to_test)
        check_java_version("1.8")
    else:
        pprint.error("WARN : could not recognize AMP as official.", True)


def check_java_version(minversion):
    if which('java'):
        import re
        version = subprocess.check_output(['java', '-version'],
                                          stderr=subprocess.STDOUT)
        # print version  # e.g: java version "1.8.0_201" etc...
        pattern = '\"(\d+\.\d+).*\"'  # noqa: W605
        result = re.search(pattern, version).groups()[0]  # e.g: 1.8

        pprint.header("#", False, ' ')
        pprint.info("Version detectee JAVA:     {0}".format(result).ljust(46),
                    False, ' ')
        if parse_version("1.8") <= parse_version(result):
            # ok
            pprint.success('{:>10s}'.format(">= 1.8, OK"), True)
        else:
            pprint.error('{:>10s}'.format("< 1.8.0"), True)
    else:
        pprint.header("#", False, ' ')
        pprint.warning(" BIEN Vérifier la bonne présence de JAVA JDK8")


def check_smtp_needed(smtp_srv):
    pprint.header("#", False, ' ')
    pprint.log("---- Check SMTP ----", True)
    if check_server_socket(smtp_srv, 25, True):
        pprint.header("#", False, ' ')
        pprint.info("un service SMTP est présent sur {0}"
                    .format(smtp_srv).ljust(46), False, ' ')
        pprint.success('{:>10s}'.format("ok"), True)

        pprint.warning('{:>10s}'.format("TODO"), True)
        # TODO : check si mail send is possible?

    else:
        pprint.warning("  ko")


def parse_conf_for_url(file, regex, expected, clean_list):
    file1 = open(file, 'r')
    lines = file1.readlines()
    for line in lines:
        if line.__contains__(regex):
            words = line.split()
            word = words[-1]
            for clean in clean_list:
                word = re.sub(clean, "", word)
            pprint.header("#", False, ' ')
            pprint.info("  URL détectée: {0} ".format(word).ljust(48), False,
                        ' ')
            if word == expected:
                pprint.success('{:>10s}'.format("OK"), True)
            else:
                pprint.error('{:>10s}'.format("KO"), True)
                pprint.log("    Actually expected : {0}".format(expected))


# # OpenSSL: récupérer la chaîne de certificats SSL d’un host
# # https://blog.hbis.fr/2017/02/11/openssl-certificate_chain/
# echo | openssl s_client -connect iparapheur-partenaires.libriciel.fr:443 \
#   -showcerts 2>&1 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' \
#   > mycert.pem
        # -- check it against name exposed
        # cafile = 'cacert.pem'
        # r = requests.get(url, verify=cafile)

        # If you use verify=True then requests uses its own CA
        # debian
        # os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(
        #    '/etc/ssl/certs/', 'ca-certificates.crt')  # debian
        # 'ca-bundle.crt') # centos

def check_https_cert_is_ok(serveur, port):
    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_REQUIRED
    # context.verify_mode = ssl.CERT_NONE
    context.check_hostname = True

    # get server cert
    command_line = "echo | openssl s_client -connect {0}:{1} -showcerts 2>&1 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > /tmp/checkmycert.pem".format(serveur, port)
    cert = subprocess.check_output(command_line, shell=True)
    context.load_verify_locations("/tmp/checkmycert.pem")

    # if linux_family == 'CentOS' or linux_family == 'redhat':
    #     context.load_verify_locations("/etc/ssl/certs/ca-bundle.crt")
    # else:
    #     context.load_verify_locations("/etc/ssl/certs/ca-certificates.crt")
    try:
        conn = context.wrap_socket(socket.socket(socket.AF_INET),
                                   server_hostname=serveur)
        conn.connect((serveur, port))
        cert = conn.getpeercert()
        # pprint.log(cert['notAfter'])
        timestamp = ssl.cert_time_to_seconds(cert['notAfter'])

        from datetime import datetime
        datetext = datetime.utcfromtimestamp(timestamp).strftime("%d %b %Y")

        pprint.header("#   ", False, ' ')
        pprint.info("Certificat expire le {0}".format(datetext).
                    ljust(46), False, ' ')
        if timestamp > time.time():
            pprint.success("encore!")
        else:
            pprint.error("expiré")
    except ssl.CertificateError as certe:
        print(certe)


def check_https_service_config(varconfig, varihmconfig):
    pprint.header("#", False, ' ')
    pprint.log("---- Check configuration service HTTPS basique ----", True)

    if not isexistsdirectory("/etc/nginx"):
        pprint.header("#   ", False, ' ')
        pprint.warning("Pas de configuration NginX, "
                       "c'est pourtant le serveur HTTPS à utiliser", True)
        return False
    checkforcerts = False
    if isexistsdirectory("/etc/nginx/conf.d"):
        if isexistsfile("/etc/nginx/conf.d", "parapheur_ssl.conf"):
            checkforcerts = True
    if isexistsdirectory("/etc/nginx/ssl"):
        if isexistsfile("/etc/nginx/ssl", "recup_crl_nginx.sh"):
            clean_list = ["/validca.tgz", "/validca.md5sum",
                          "http://", "https://"]
            parse_conf_for_url("/etc/nginx/ssl/recup_crl_nginx.sh",
                               "/usr/bin/wget -q", "validca.libriciel.fr",
                               clean_list)
        if isexistssubdir("/etc/nginx/ssl", "validca"):
            isfolderfromtoday("/etc/nginx/ssl/validca")

    # Vérifier process Nginx pas trop vieux (p/r lancement crontab) ?
    line = subprocess.check_output('nginx -v', stderr=subprocess.STDOUT,
                                   shell=True).decode("utf-8")
    outr = line.rstrip("\n").rstrip(" ").split("nginx/")[1].split(" ", 1)[0]
    pprint.header("#", False, ' ')
    pprint.info("Version detectee NginX:     {0}".format(outr.rstrip()).
                ljust(46), False, ' ')
    if parse_version("1.8.0") < parse_version(outr.rstrip()):
        pprint.success('{:>10s}'.format(">1.8.0, OK"), True)
    else:
        pprint.error('{:>10s}'.format("< 1.8.0"), True)

    # LOCALHOST sanity
    nginxserver = "localhost"
    nginxport = 443
    pprint.header("#", False, ' ')
    pprint.info("NginX sur {0}:{1}".format(nginxserver, nginxport).
                ljust(46), False, ' ')
    if not check_server_socket(nginxserver, nginxport, False):
        pprint.warning('{:>10s}'.format("inactif"), True)
    else:
        pprint.success('{:>10s}'.format("actif"), True)

    # Point d'entree WEB
    nginxserver = varihmconfig.get("Parapheur", "parapheur.url")
    pprint.header("#", False, ' ')
    pprint.info("NginX sur {0}:{1}".format(nginxserver, nginxport).
                ljust(46), False, ' ')
    if not check_server_socket(nginxserver, nginxport, False):
        pprint.warning('{:>10s}'.format("inactif"), True)
    else:
        pprint.success('{:>10s}'.format("actif"), True)

        # TODO FIX: check_https_cert_is_ok(nginxserver, nginxport)

    # Point d'entree WEB SERVICES
    nginxserver = varconfig.get("Parapheur", "parapheur.hostname")
    pprint.header("#", False, ' ')
    pprint.info("NginX sur {0}:{1}".format(nginxserver, nginxport).
                ljust(46), False, ' ')
    if not check_server_socket(nginxserver, nginxport, False):
        pprint.warning('{:>10s}'.format("inactif"), True)
    else:
        pprint.success('{:>10s}'.format("actif"), True)
        # check sur certificat serveur
        try:
            # requests.get("https://"+nginxserver, verify=True)

            # TODO FIX: check_https_cert_is_ok(nginxserver, nginxport)
            # temporary revert
            pass

        except requests.exceptions.SSLError as e:
            pprint.header("#", False, ' ')
            text = format(e.message)
            if 'SSL: CERTIFICATE_VERIFY_FAILED' in text:
                pprint.info("  1 CERTIFICATE_VERIFY_FAILED".
                            ljust(46), False, ' ')
            else:
                pprint.info(text.ljust(46), False, ' ')
            pprint.error('{:>10s}'.format("Alerte"), True)

    istextinfile("/var/www/parapheur/alfresco/iparapheur.wsdl", nginxserver)

    if checkforcerts is True:
        pprint.warning('{0:>10s}'.format("TODO"), True, ' ')
        print(" check sur certificat HTTPS: valide, etc.")

    return nginxserver


def check_mysql_service_config(varconf):
    pprint.header("#", False, ' ')
    pprint.log("---- Check configuration service MySQL ----  TODO", True)

    # Extract mysqlserver from db.url schema:
    # defaults to: db.url=jdbc:mysql://localhost/alfresco
    # so cut out the 'jdbc:' stream and parse the resulting URL afterwards
    mysqldburl = varconf.get("Parapheur", "db.url")
    urlparsed = urlparse(mysqldburl[5:])
    # pprint.info(urlparsed)
    mysqlserver = urlparsed.hostname  # "localhost"
    mysqlport = 3306
    if urlparsed.port is not None:
        mysqlport = urlparsed.port

    pprint.header("#", False, ' ')
    pprint.info("Service MySQL sur {0}:{1}".format(mysqlserver, mysqlport).
                ljust(46), False, ' ')
    if not check_server_socket(mysqlserver, mysqlport, True):
        pprint.warning('{:>10s}'.format("inactif"), True)
        return False
    else:
        pprint.success('{:>10s}'.format("actif"), True)

        mysqluser = varconf.get("Parapheur", "db.username")
        mysqlpwd = varconf.get("Parapheur", "db.password")
        mysqlbase = varconf.get("Parapheur", "db.name")
        pprint.header("#", False, ' ')
        pprint.info("DB '{3}' sur {0}@{1}:{2}".
                    format(mysqluser, mysqlserver, mysqlport, mysqlbase).
                    ljust(46), False, ' ')

        try:
            cur_max_cnx = ""
            parametre_mysql = ""

            cnx = pymysql.connect(user=mysqluser, password=mysqlpwd,
                                  host=mysqlserver, port=mysqlport,
                                  database=mysqlbase)
            pprint.success('{:>10s}'.format("OK"), True)

            cursor = cnx.cursor()
            query = "SELECT @@GLOBAL.max_connections as res;"
            cursor.execute(query)
            for res in cursor:
                cur_max_cnx = res[0]
            pprint.header("#", False, ' ')
            pprint.info('Nombre de connexions maxi      = {:>6d}'.
                        format(cur_max_cnx).ljust(46), False, ' ')
            if cur_max_cnx < 360:
                pprint.error('{:>10s}'.format("< 360"), True)
            else:
                pprint.success('{:>10s}'.format(">=360, OK"), True)

            query = "SELECT @@GLOBAL.innodb_file_per_table as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('innodb_file_per_table          = {0:>6d}'.
                        format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql != 1:
                pprint.error('{0:>10s}'.format("!= 1"), True)
            else:
                pprint.success('{0:>10s}'.format("=1, OK"), True)

            query = "SELECT @@GLOBAL.open_files_limit as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('open_files_limit               = {0:>6d}'.
                        format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql < 8192:
                pprint.error('{0:>10s}'.format("< 8192"), True)
            else:
                pprint.success('{0:>10s}'.format(" OK"), True)

            query = "SELECT @@GLOBAL.wait_timeout as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('wait_timeout                   = {0:>6d}'.
                        format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql < 28800:
                pprint.error('{0:>10s}'.format("< 28800"), True)
            else:
                pprint.success('{0:>10s}'.format("  OK"), True)

            query = "SELECT @@GLOBAL.innodb_locks_unsafe_for_binlog as res;"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('innodb_locks_unsafe_for_binlog = {0:>6d}'.
                        format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql != 1:
                pprint.error('{0:>10s}'.format("!= 1"), True)
            else:
                pprint.success('{0:>10s}'.format("=1, OK"), True)

            # Latest queries : test for DB integrity
            # -- Find children of nodes with no parents
            query = "SELECT COUNT(*) FROM alf_child_assoc " \
                    "WHERE parent_node_id IN " \
                    "( SELECT id FROM alf_node WHERE node_deleted =0 AND " \
                    "id NOT IN ( SELECT root_node_id FROM alf_store ) AND " \
                    "id NOT IN ( SELECT child_node_id FROM alf_child_assoc ) "\
                    ");"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('Recherche noeuds orphelins 1/2 = {0:>6d}'
                        .format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql != 0:
                pprint.error('{0:>10s}'.format("REINDEXER"), True)
            else:
                pprint.success('{0:>10s}'.format("=0, OK"), True)
            # -- find nodes with no parent
            query = "SELECT COUNT(*) FROM alf_node " \
                    "WHERE node_deleted =0 AND " \
                    "id NOT IN ( SELECT root_node_id FROM alf_store ) AND " \
                    "id NOT IN ( SELECT child_node_id FROM alf_child_assoc );"
            cursor.execute(query)
            for res in cursor:
                parametre_mysql = res[0]
            pprint.header("#", False, ' ')
            pprint.info('Recherche noeuds orphelins 2/2 = {0:>6d}'
                        .format(parametre_mysql).ljust(46), False, ' ')
            if parametre_mysql != 0:
                pprint.error('{0:>10s}'.format("REINDEXER"), True)
            else:
                pprint.success('{0:>10s}'.format("=0, OK"), True)

            cursor.close()

        except pymysql.InternalError as ie:
            icode, imessage = ie.args
            pprint.error('internal error')
            print ">>>>>>>>>>>>>>>>", icode, imessage
        except pymysql.Error as ierr:
            pprint.error('{0:>10s}'.format("Erreur"), True)
            icode, imessage = ierr.args
            print ">>>>>>>>>>>>>>>>", icode, imessage
            # if err.errno == ER.ACCESS_DENIED_ERROR:
            #    print("Something is wrong with your user name or password")
            # elif err.errno == ER.BAD_DB_ERROR:
            #    print("Database does not exist")
            # else:
            #    print(err)
        except Exception as e:  # noqa: F841
            pprint.error("Somethin' got wrong...")
        else:
            cnx.close()
        pprint.warning('{0:>10s}'.format("TODO"), True)


def check_isexists_alfrescoglobal():
    pprint.header("#", False, ' ')
    pprint.log("---- Exists alfresco-global.properties  ? ----  ", True)

    # Alfresco-global.properties
    isexistsdirectory(defaut_iparapheur_root)
    isexistssubdir(defaut_iparapheur_root, "tomcat/shared/classes")
    return isexistsfile("{0}/tomcat/shared/classes"
                        .format(defaut_iparapheur_root),
                        "alfresco-global.properties")


def analyse_is_param_in_conf(keyarray, paramconfarray, prefix):
    for param_key in keyarray:
        try:
            param_value = paramconfarray.get("Parapheur", param_key)
            pprint.header("#", False, ' ')
            pprint.info("{2} {0} = {1}".format(param_key, param_value, prefix))
        except ConfigParser.NoOptionError as e:
            pprint.header("#", False, ' ')
            pprint.error("{1}  OMG, need this: {0}".format(param_key, prefix))


def check_config_alfrescoglobal(varconf, ihmvarconf, version_presente):
    pprint.header("#", False, ' ')
    pprint.log("---- Check alfresco-global.properties ----  TODO", True)

    alf_dir_root = varconf.get("Parapheur", "dir.root")
    db_url = varconf.get("Parapheur", "db.url")
    # pprint.info(varconf.options("Parapheur"))
    # pprint.info(varconf.items("Parapheur"))

    pprint.header("#", False, ' ')
    pprint.info("alf_dir_root = {0}".format(alf_dir_root))
    pprint.header("#", False, ' ')
    pprint.info("database URL = {0}".format(db_url))

    needed_alfresco_global = ['dir.root',
                              'db.url',
                              'index.recovery.mode']
    analyse_is_param_in_conf(needed_alfresco_global, varconf, " ")

    if parse_version("4.3.2") <= parse_version(version_presente):
        needed_alfresco_global_params_4_3_2 = [
            'parapheur.ihm.creerdossier.maindocuments.max',
            'parapheur.libersign.tag.signature.name',
            'parapheur.libersign.tag.signature.name.tenants']
        needed_iparapheur_global_params_4_3_2 = [
            'parapheur.ihm.creerdossier.maindocuments.max']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_3_2,
                                 varconf, " ")
        analyse_is_param_in_conf(needed_iparapheur_global_params_4_3_2,
                                 ihmvarconf, "I")

    if parse_version("4.4.0") <= parse_version(version_presente):
        needed_alfresco_global_params_4_4_0 = [
            'openOffice.test.cronExpression',
            'parapheur.exploit.xemelios.command']
        needed_iparapheur_global_params_4_4_0 = [
            'parapheur.ihm.password.strength',
            'parapheur.ihm.aide.libersign.url',
            'parapheur.extension.libersign.firefox.url',
            'parapheur.extension.libersign.chrome.url',
            'parapheur.extension.libersign.native.url']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_4_0,
                                 varconf, " ")
        analyse_is_param_in_conf(needed_iparapheur_global_params_4_4_0,
                                 ihmvarconf, "I")

    if parse_version("4.4.1") <= parse_version(version_presente):
        needed_alfresco_global_params_4_4_1 = [
            'parapheur.document.lockedPDF.accept',
            'parapheur.hostname']
        needed_iparapheur_global_params_4_4_1 = [
            'parapheur.ihm.admin.users.connected.threshold']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_4_1,
                                 varconf, " ")
        analyse_is_param_in_conf(needed_iparapheur_global_params_4_4_1,
                                 ihmvarconf, "I")

    if parse_version("4.5.0") <= parse_version(version_presente):
        needed_alfresco_global_params_4_5 = [
            'parapheur.cachetserver.security.key',
            'parapheur.libersign.tag.cachet.name',
            'parapheur.libersign.tag.cachet.name.tenants',
            'parapheur.notification.retards.cron',
            'parapheur.cachetserver.warnexpiration.cronexpression',
            'parapheur.cachetserver.warnexpiration.daysuntilexpiration']
        needed_iparapheur_global_params_4_5 = [
            'parapheur.ihm.archives.show',
            'parapheur.ihm.attest.show']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_5,
                                 varconf, " ")
        analyse_is_param_in_conf(needed_iparapheur_global_params_4_5,
                                 ihmvarconf, "I")

    if parse_version("4.6.0") <= parse_version(version_presente):
        needed_alfresco_global_params_4_6_0 = [
            'parapheur.pastell.mailsec.connector.host',
            'parapheur.pastell.mailsec.connector.port',
            'parapheur.pastell.mailsec.redis.channel',
            'redis.host',
            'redis.port',
            'parapheur.notify.secretaire.enabled']
        needed_iparapheur_global_params_4_6 = [
            'parapheur.admin.s2low.actes.show',
            'parapheur.admin.s2low.helios.show',
            'parapheur.admin.s2low.mailsec.show',
            'parapheur.admin.pastell.mailsec.show',
            'parapheur.admin.fast.show',
            'parapheur.admin.srci.show',
            'parapheur.admin.horodate.show',
            'parapheur.admin.mailservice.show',
            'parapheur.admin.archiland.show',
            'parapheur.admin.signature.xadesdet.show',
            'parapheur.admin.signature.xadesecd.show',
            'parapheur.admin.signature.xadesdia.show',
            'parapheur.admin.signature.pkcs7aio.show',
            'parapheur.admin.signature.pkcs1.show']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_6_0,
                                 varconf, " ")
        analyse_is_param_in_conf(needed_iparapheur_global_params_4_6,
                                 ihmvarconf, "I")
    if parse_version("4.6.4") <= parse_version(version_presente):
        needed_alfresco_global_params_4_6_4 = [
            'system.usages.enabled',
            'parapheur.ws.creerdossier.autoselectsigformat.ifunsigned',
            'parapheur.ws.creerdossier.autoselectsigformat.ifunsigned.pdf']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_6_4,
                                 varconf, " ")
    if parse_version("4.6.6") <= parse_version(version_presente):
        needed_alfresco_global_params_4_6_6 = [
            'parapheur.suppleance.text',
            'parapheur.read.pes.withpdf']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_6_6,
                                 varconf, " ")
    if parse_version("4.6.8") <= parse_version(version_presente):
        needed_alfresco_global_params_4_6_8 = ['parapheur.libersign.tampon.signature.info']  # noqa: E501
        needed_iparapheur_global_params_4_6_8 = ['parapheur.admin.templates.show']  # noqa: E501
        analyse_is_param_in_conf(needed_alfresco_global_params_4_6_8,
                                 varconf, " ")
        analyse_is_param_in_conf(needed_iparapheur_global_params_4_6_8,
                                 ihmvarconf, "I")

    if parse_version("4.7.0") <= parse_version(version_presente):
        needed_alfresco_global_params_4_7 = [
            'parapheur.pdfstamp.connector.host',
            'parapheur.pdfstamp.connector.port',
            'parapheur.crypto.connector.host',
            'parapheur.crypto.connector.port',
            'system.content.orphanProtectDays',
            'system.content.orphanCleanup.cronExpression',
            'system.content.eagerOrphanCleanup']
        needed_iparapheur_global_params_4_7 = [
            'pes-viewer.auth.token',
            'pdf-stamp.auth.token',
            'pastell-connector.auth.token',
            'crypto.auth.token',
            'rgpd.dpo',
            'rgpd.hebergeur']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_7,
                                 varconf, " ")
        analyse_is_param_in_conf(needed_iparapheur_global_params_4_7,
                                 ihmvarconf, "I")
    if parse_version("4.7.7") <= parse_version(version_presente):
        needed_alfresco_global_params_4_7_7 = [
            'parapheur.filename.signature.detachee',
            'parapheur.filename.signature.externe']
        analyse_is_param_in_conf(needed_alfresco_global_params_4_7_7,
                                 varconf, " ")


def check_config_ghostscript():
    pprint.header("#", False, ' ')
    pprint.log("---- Check config GhostScript ----", True)
    libgs_path = defaut_iparapheur_root + "/common/lib/libgs.so"
    if not isexistsfile("{0}/common/lib".format(defaut_iparapheur_root),
                        "libgs.so"):
        return
    libgsstat = os.stat(libgs_path)
    pprint.header("#", False, ' ')
    pprint.info("Taille libgs.so = {0} octets".format(libgsstat.st_size).
                ljust(46), False, ' ')
    if libgsstat.st_size < 19 * 1024 * 1024:
        pprint.error('{0:>10s}'.format("< 19Mo"), True)
    else:
        pprint.success('{0:>10s}'.format("> 19Mo, OK"), True)
    command_line = "ldconfig -n /opt/iParapheur/common/lib/ -v | grep libgs.so"
    output = subprocess.check_output(command_line, shell=True)
    outl, outr = output.split("-> ")
    pprint.header("#", False, ' ')
    # pprint.info("Version detectee: {0}".format(outr.rstrip()), False, ' ')
    pprint.info("Version detectee: {0}".format(outr.rstrip()).ljust(46),
                False, ' ')
    if parse_version("libgs.so.9.19") < parse_version(outr.rstrip()):
        if parse_version(outr.rstrip()) <= parse_version("ligs.so.9.27"):
            pprint.success('{:>10s}'.format("> 9.19, OK"), True)
        else:
            pprint.error('{:>10s}'.format("!=9.27, KO"), True)
    else:
        pprint.error('{:>10s}'.format("< 9.20"), True)


# New service used for 4.7 onwards
def check_pdfrender_service(version_presente):
    # 4.7.0  : libpoppler-libriciel.1.0.0.so
    # 4.7.1  : libpoppler-libriciel.so compilee par distro.
    # 4.7.2+ : libriciel-pdf
    if parse_version("4.7.2") <= parse_version(version_presente):
        if not isexistsfile("{0}/common/lib".format(defaut_iparapheur_root),
                            "libriciel-pdf"):
            return
        librpdf_path = defaut_iparapheur_root + "/common/lib/libriciel-pdf"
        lddOut = subprocess.check_output(['ldd', librpdf_path])
        for line in lddOut.splitlines():
            if "not found" in line:
                arr = line.split(" => ")
                pprint.header("#", False, ' ')
                pprint.info("     dépendance non satisfaite : ", False, ' ')
                pprint.error(arr[0].strip('\t'), True)


def check_files_needed():
    pprint.header("#", False, ' ')
    pprint.log("---- Check présence fichiers post-config ----", True)
    da_files = ['backup_parapheur.sh', 'custom-wsdl.sh',
                'iparaph-updateAMP.sh',
                'logrotate-iparapheur.conf', 'nettoieEntrepot.sh',
                'nettoieLogs.sh', 'purge-xemwebview.sh', 'srgb.profile',
                'verdanai.ttf', 'warn_needPurge.sh']
    for to_test in da_files:
        isexistsfile("/opt/iParapheur", to_test)


def check_tomcat_libs_cleanup(version_presente):
    pprint.header("#", False, ' ')
    pprint.log("---- Check nettoyage common/libs ----", True)
    if parse_version("4.7.0") <= parse_version(version_presente):
        da_files = ['libfreetype.so', 'libgif.so', 'libjpeg.so',
                    'libMagickCore.so', 'libMagick++.so', 'libMagickWand.so',
                    'libpng12.so', 'libpng.so', 'libwmf.so', 'libstdc++.so.5',
                    'libz.so', 'libgs.so']
    else:
        da_files = ['libz.so']
    for to_test in da_files:
        isfileproperlydeleted(defaut_iparapheur_root+"/common/lib", to_test)


# chapitre  XEMELIOS / PES viewer
def check_pesviewer_temp_directories():
    # on commence par l'existence des repertoires de base
    if not isexistsdirectory("/var/tmp/bl-xemwebviewer"):
        pprint.header("#   ", False, ' ')
        pprint.error("La visionneuse PES ne fonctionnera pas: "
                     "manquent les répertoires temporaires.")
        return 0
    else:
        # verif droits d'accès 755
        da_reps = ['/var', '/var/tmp', '/var/tmp/bl-xemwebviewer']
        for test_rep in da_reps:
            accessrights = os.stat(test_rep).st_mode & 0o777
            if not accessrights & 0o055:
                pprint.header("#   ", False, ' ')
                pprint.error("Droits 755 requis pour {0}. KO".format(test_rep))
        # verif existence+droits des sous-repertoires
        da_subreps = ['xwv-cache', 'xwv-extract', 'xwv-shared']
        for to_test in da_subreps:
            if not isexistssubdir("/var/tmp/bl-xemwebviewer", to_test):
                pprint.header("#   ", False, ' ')
                pprint.error("La visionneuse PES ne fonctionnera pas: "
                             "manque le répertoire {0}.".format(to_test))
            else:
                accessrights = os.stat("/var/tmp/bl-xemwebviewer/"
                                       + to_test).st_mode & 0o777
                if not accessrights & 0o077:
                    pprint.header("#   ", False, ' ')
                    pprint.error("Droits 777 requis pour {0}. KO".format(to_test))  # noqa: E501


# look at /opt/iParapheur/tomcat/conf/Catalina/localhost/alfresco.xml
def check_is_pes_url_declarated(baseinstalldir):
    alfrescoPath = baseinstalldir + "/tomcat/conf/Catalina/localhost/"
    alfrescoXml = "alfresco.xml"
    if isexistsfile(alfrescoPath, alfrescoXml):
        rootAcegi = ET.parse(alfrescoPath + alfrescoXml).getroot()
        search_env = 'Environment'
        # search_value = './/name'
        found = False
        for env in rootAcegi.findall(search_env):
            name = env.get('name')
            if name == 'iparapheur-blex/bl-xemwebviewer-url':
                found = True
        if not found:
            pprint.error('   "alfresco.xml" est incomplet.')
        else:
            pprint.info('   URL "pes-viewer" connue en {0}'.
                        format(env.get('value')))


def check_xemwebview_service_config(basedir, version_presente):
    pprint.header("#", False, ' ')
    pprint.log("---- Check configuration service Xemwebviewer ---- TODO", True)
    if not isexistsfile("/etc/init.d", "xemwebview"):
        check_pesviewer_service_config(basedir)
    check_pesviewer_temp_directories()
    check_is_pes_url_declarated(basedir)


# Generic checks for : crypto, pastell-connector pdf-stamp, pes-viewer
def check_side_service(srvname, host, tcp_port):
    pprint.header("#", False, ' ')
    pprint.log("---- Check configuration service {0} ----".format(srvname),
               True)
    if tcp_port == 8005:
        pprint.header("#   ", False, ' ')
        pprint.error("Attention: Le port 8005 est réservé à TOMCAT")
    isexistsfile("/etc/systemd/system/", "{0}.service".format(srvname))
    if not isexistsdirectory("/opt/{0}".format(srvname)):
        pprint.header("#   ", False, ' ')
        pprint.warning("Le service {0} ne semble pas être en place.".
                       format(srvname))
    elif not os.path.islink("/opt/{0}/{0}.jar".format(srvname)):
        pprint.header("#   ", False, ' ')
        pprint.warning("Le service {0} n'est pas correctement installé.".
                       format(srvname))
    else:
        import pwd
        try:
            pwd.getpwnam('{0}'.format(srvname))
            pprint.header("#", False, ' ')
            pprint.info("Check du compte linux '{0}'".
                        format(srvname).ljust(46), False, ' ')
            pprint.success('{:>10s}'.format("OK"), True)
            real_owner_dir = pwd.getpwuid(os.stat("/opt/{0}".
                                          format(srvname)).st_uid).pw_name
            real_owner_lnk = pwd.getpwuid(os.stat("/opt/{0}/{0}.jar".
                                          format(srvname)).st_uid).pw_name
            pprint.header("#", False, ' ')
            pprint.info("Check des droits sur /opt/{0} ".
                        format(srvname).ljust(46), False, ' ')
            if real_owner_dir == srvname and real_owner_lnk == srvname:
                pprint.success('{:>10s}'.format("OK"), True)
            else:
                pprint.error('{:>10s}'.format("KO"), True)
        except KeyError:
            pprint.header("#   ", False, ' ')
            pprint.warning('Le service {0} est mal installé, le compte Linux '
                           '"{1}" est absent.'.format(srvname, srvname))
        # checks TCP-port, is-service-running?
        pprint.header("#", False, ' ')
        pprint.info("Service {2} sur {0}:{1}".format(host, tcp_port, srvname).
                    ljust(46), False, ' ')
        if not check_server_socket(host, tcp_port, True):
            pprint.warning('{:>10s}'.format("inactif"), True)
        else:
            pprint.success('{:>10s}'.format("actif"), True)
        # TODO : detect version, maybe is update available ?


# Chapitre  Crypto
def check_crypto_service_config():
    default_host = "127.0.0.1"
    default_port = 8007
    check_side_service("crypto", default_host, default_port)


# Chapitre  pdf-stamp
def check_pdfstamp_service_config():
    default_host = "127.0.0.1"
    default_port = 8004
    check_side_service("pdf-stamp", default_host, default_port)


# Chapitre  Pes-viewer
def check_pesviewer_service_config(basedir):
    default_host = "127.0.0.1"
    default_port = 8888
    check_side_service("pes-viewer", default_host, default_port)
    check_pesviewer_temp_directories()
    check_is_pes_url_declarated(basedir)
    isfileproperlydeleted("/etc/init.d", "xemwebview")


# chapitre  Pastell Connector
def check_pastellconnector_service_config():
    default_host = "127.0.0.1"
    default_port = 8002
    check_side_service("pastell-connector", default_host, default_port)


def check_alfresco_sh(basedir, filename):
    IP_ALFRESCO_SH = "{0}/{1}".format(basedir, filename)
    if not isexistsfile(basedir, filename):
        pprint.header("#   ", False, ' ')
        pprint.warning("Mais où diable se cache '{0}' ?".format(filename))
        return -1
    # TODO: detect 'ulimit' statements, 'cd $INSTALLDIR' , 'umask 022'
    hasInstallDir = False
    hasUlimit1 = False
    hasUlimit2 = False
    hasUmask = False
    with open(IP_ALFRESCO_SH, 'r') as f:
        for line in f:
            if 'cd $INSTALLDIR' in line:
                hasInstallDir = True
            if 'ulimit -Hn' in line:
                hasUlimit1 = True
            if 'ulimit -Sn' in line:
                hasUlimit2 = True
            if 'umask 022' in line:
                hasUmask = True
    if not hasInstallDir:
        pprint.header("#    ", False, ' ')
        pprint.warning("     Il manque '{1}' dans le {0}".
                       format(filename, "cd $INSTALLDIR"))
    if not hasUlimit1:
        pprint.header("#    ", False, ' ')
        pprint.warning("     Il manque '{1}' dans le {0}".
                       format(filename, "ulimit -Hn 16384"))
    if not hasUlimit2:
        pprint.header("#    ", False, ' ')
        pprint.warning("     Il manque '{1}' dans le {0}".
                       format(filename, "ulimit -Sn 16384"))
    if not hasUmask:
        pprint.header("#    ", False, ' ')
        pprint.warning("     Il manque '{1}' dans le {0}".
                       format(filename, "umask 022"))


def barelyGuess_iParapheur_version_from_AMP(basedir):
    hashVersionDict = dict([
        ('fcfaea0654fb04547bf9ae3d3dac993bf0128b1653da794720621a6ee1b6e2eb', '4.4.0'),  # noqa: E501
        ('f154b03e4b7f460a6c010476e4f7a3e9ae0c7537b7da588ab1789c4eb119d022', '4.4.1'),  # noqa: E501
        ('5f83fe48ff110bae2262aef085255a582e06c85025f7bcfbbe3991cec318f75b', '4.4.2'),  # noqa: E501
        ('a9cf1bdaa16a7a32452d6a7e16a420ef0e01d4ee56492a4e8842cad6c94b5e2e', '4.4.2'),  # noqa: E501
        ('cf347fc3a6226c30b8c684c8e7ebcef857d8bb1d45628f7b98a0d30b44bf72ff', '4.5.0'),  # noqa: E501
        ('9848b8ceda248e77a6bdc2eaab244cd482f4232126dbb99cf2a1f12df31fa8ea', '4.5.1'),  # noqa: E501
        # ('f5f34f098894ee7865ce9dc9b0d7aa46a633a9ae30f3782ab6bd671948ebea8f', '4.5.2'),  # noqa: E501
        ('f5f34f098894ee7865ce9dc9b0d7aa46a633a9ae30f3782ab6bd671948ebea8f', '4.5.3'),  # noqa: E501
        ('2a3f529706af89e1ed1ce9cb4ecf722b3537e8487de90518a91b68d44793d713', '4.6.0'),  # noqa: E501
        ('ff25b2080959a09d4e066c9f7fd208a1abf57a1eb60d6a322963c7d0b230e685', '4.6.1'),  # noqa: E501
        ('8c1b803042cd0f180bdcbca550878e513a380a636e38c2e9b4216ff0358536ae', '4.6.2'),  # noqa: E501
        ('397580a00697ee8b3926d6a458caeba05f5838e4f591971e6befce57301db852', '4.6.3'),  # noqa: E501
        ('129bde0c2b32566582f632673862a4a7e666dfcbfa5534b4f0c3903c26a035d4', '4.6.4'),  # noqa: E501
        ('0f453910fedef480c3ee4a2652bb9de3eef08aa2a165c9b5b9294f713a97497a', '4.6.5'),  # noqa: E501
        ('not-known-hash--------------------------------------------------', '4.6.6'),  # noqa: E501
        ('56a7f952d0c6925be159843b7c6665e87446a3edb290b17a7b740d86ba2c54d6', '4.6.7'),  # noqa: E501
        ('d48d3a0cabf978751b61891d4b63346a7bd91c827ba6ff71ef16995a2cf87498', '4.6.8'),  # noqa: E501
        ('c100e76ffa93809e721fcf29174c8ebbe77950535f1e1bb921ed0291ff8ff144', '4.7.0'),  # noqa: E501
        ('3b47d588bc97a568ee3b0b1b4654318e5653caf9a0bd01d23b97a17ec4d55892', '4.7.1'),  # noqa: E501
        ('e6a19c0f81203f07cf1436177890cab59c1eb0fd8c7d58db196c34c9922e7735', '4.7.2'),  # noqa: E501
        ('d464f1319488479e74f429e442add6b8c7c1bf5a2a92c50b3c6c8618660614b1', '4.7.3'),  # noqa: E501
        ('e690bfee9104cc6443ed89463002b3bda35443b37ae2b3b12129fcbe937e6396', '4.7.4'),  # noqa: E501
        ('8d3ae20aca1a1ddacd710be2441b26cd1b36f060f5805efc416b80fd56bb7f63', '4.7.5'),  # noqa: E501
        ('1ef11253b8b5df66cae76d76cb5893fb4ea91a987a83c7b01fff100ee751a845', '4.7.6'),  # noqa: E501
        ('72d4b6026029e46fcab95a714ba60651d1c3d1241028ca8e3cfc6d2e2946ee67', '4.7.7')  # noqa: E501
        ])
    IP_AMP_PATH = glob.glob("{0}/{1}".format(
        basedir, "amps/iparapheur-amp-*.amp"))[0]
    if os.path.exists(IP_AMP_PATH):
        ampHash = sha256_checksum(IP_AMP_PATH)
        return hashVersionDict.get(ampHash, 'inconnu')
    else:
        return 'inconnu'


def barelyGuess_iParapheur_version_from_WAR(ipWarHash):
    hashVersionDict = dict([
        ('ce248f4f3a7d56e15e5b030432bab8b226c019b21c1067a7b7ea29f0142d2476', '4.4.0'),  # noqa: E501
        ('a8efc9f586530f2fcce01afe65ee3030c4722424585557f77a4f0138d205627c', '4.4.1'),  # noqa: E501
        ('a5435b34b255d51a8f121da90dc8399d7ee5df1ee098601f64f25e063d11b40f', '4.4.2'),  # official # noqa: E501
        ('be105b1f7ea85d7240ab401560a4a69d1e2abd4d93ac7cc9ccc50bbde058f378', '4.4.2'),  # noqa: E501
        ('5e4d3fd17a87a383a31cf93cb5faceb56cfd0211ad3a7a7de624b85334cf72a4', '4.5.0'),  # noqa: E501
        ('82d6156a17e701ad2213569f8a9f7736f64f547f4c8b32f461a4e9d044ecda92', '4.5.1'),  # noqa: E501
        ('3ac125b9ba0c82003f8e2410ede004c7062c1f3c32964567e9a5c2510e7ed210', '4.5.2'),  # noqa: E501
        ('08b4ad4bad639018e20057a7763205251996280d8ff23aa7c0b431ffef1c593e', '4.5.3'),  # noqa: E501
        ('fa1fc3f6c6f0fb7431d23d682481642fcbd77ccffc19645f824ab0f4e6973336', '4.6.0'),  # noqa: E501
        ('10b38f4acfbbb2f4c63682735f103085c9d18efb6121d5417061bba7e256293f', '4.6.1'),  # noqa: E501
        ('28672e0cb1e02ffb893dacbb5dcbe8871daa99b5cc88de831058f0de5e1d1a75', '4.6.2'),  # noqa: E501
        ('a9b653e4a8a82a04eb697f5221abe04a0efdda8476ea4be7b64f650d5d44f9d7', '4.6.3'),  # noqa: E501
        ('f0d189053efe446c59f1eb5aa1d0329a09bc94eac78642da8c7b56bd5b327180', '4.6.4'),  # noqa: E501
        ('747fa8ec7f2eb076033d26cde0072ec05ae0798eb2e929e465e095b8cb934610', '4.6.5'),  # noqa: E501
        ('not-known-hash--------------------------------------------------', '4.6.6'),  # noqa: E501
        ('4d5ef88ed7b03521042036369e1155e125733c32959718ce81ce205fc99b0003', '4.6.7'),  # noqa: E501
        ('8d5360a9bb34aba7b61797f6ea5f813c43e6ec7a22df53ff13ef88a1c7a84737', '4.6.8'),  # noqa: E501
        ('6269cf4ded6bf4e4e235101c142857eb902530edbe464420dea2c9718b4b1b57', '4.7.0'),  # noqa: E501
        ('d57c9a980e26aa3ef22e272c2717c9fd8a3c0b381c65d58a453eb9af64b16a6c', '4.7.1'),  # noqa: E501
        ('5b70f42d376176f081d350948e56891dbf3e27578fe110e3dfa99018851b8838', '4.7.2'),  # noqa: E501
        ('2501882f4e9af74ec5827ce3dd0337286204d0caddbb10c99546fd0c0f502b80', '4.7.3'),  # noqa: E501
        ('0d2b2d31b8e4cd9eb4f77bc22f8251ee0605407b96c35c923aa239f2a522093a', '4.7.4'),  # noqa: E501
        ('e9f1c8489a24b79c0f1c21b756b0a9f4a635f3ba6c21ce3bc0121563198c7734', '4.7.5'),  # noqa: E501
        ('f83d0818812857c3a5894635bff6fc3f5a3d42c9ac30981d0299aa3b267c1e57', '4.7.6'),  # noqa: E501
        ('c083badb3f29480d4111d49cde0912c1c04fea6db0297af0a3d01f783b1ff2e3', '4.7.7')  # noqa: E501
        ])
    return hashVersionDict.get(ipWarHash, 'inconnu')


# chapitre anti-fraude
def guess_iParapheur_version(basedir):
    pprint.header("#", False, ' ')
    IP_MODULE_PATH = "{0}/{1}".format(
        basedir,
        "tomcat/webapps/iparapheur/META-INF/maven/org.adullact.iparapheur/"
        "iparapheur-surf-webapp/pom.properties")
    if not os.path.exists(IP_MODULE_PATH):
        pprint.error("Impossible de deviner la version de i-Parapheur")
        return -1
    with open(IP_MODULE_PATH, 'r') as f:
        module_string = '[Parapheur]\n' + f.read()
    module_fp = io.BytesIO(module_string)
    leMdodule = ConfigParser.RawConfigParser()
    leMdodule.readfp(module_fp)
    versionIP = leMdodule.get("Parapheur", "version")
    pprint.info("Version detectee sur le serveur:", False, ' ')
    if "SNAPSHOT" in versionIP:
        pprint.warning('{:>13s}'.format("Problème de détection"), True)
    elif parse_version(versionIP_minimum) <= parse_version(versionIP):
        pprint.success('{:>10s}'.format(versionIP), False, ' ')
        pprint.success('{:>13s}'.format(" >{0}, OK".format(versionIP_minimum)),
                       True)
    else:
        pprint.success('{:>10s}'.format(versionIP), False, ' ')
        pprint.error('{:>13s}'.format("non supportée"), True)
    return versionIP


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()


def hash_the_binfile(basedir, subdir, binfile):
    da_fullfile = "{0}/{1}/{2}".format(basedir, subdir, binfile)
    if os.path.exists(da_fullfile):
        # pprint.info("   {0}  trouvé".format(binfile))
        return sha256_checksum(da_fullfile)
    else:
        pprint.header("#   ", False, ' ')
        pprint.warning(" '{0}' introuvable, normal???".format(binfile))
        return -1


def check_iParapheur_version_is_valid(basedir):
    pprint.header("#", False, ' ')
    pprint.log("---- Check i-Parapheur version ----  TODO", True)
    # NB: Le hash(alfresco.war) est inutile, puisque contextuel à l'instance.
    # Celui du fichier AMP est "presque" plus pertinent...
    versionFromAMP = barelyGuess_iParapheur_version_from_AMP(basedir)
    da_hash = hash_the_binfile(basedir, "tomcat/webapps", "iparapheur.war")
    # pprint.info("Hash WAR: {0}".format(da_hash), False)
    versionFromWAR = barelyGuess_iParapheur_version_from_WAR(da_hash)
    pprint.header("#", False, ' ')
    pprint.info("Version detectee sur AMP: {0}".format(versionFromAMP), False)
    pprint.header("#", False, ' ')
    pprint.info("Version detectee sur WAR: {0}".format(versionFromWAR), False)
    da_version = guess_iParapheur_version(basedir)
    if da_version == -1:
        return -1
    return da_version


def check_symbolic_link(root, file):
    pprint.header("#", False, ' ')
    pprint.info("Lien symbolique {0} ".format(file).ljust(46), False, ' ')
    if os.path.islink(root + file):
        pprint.success('{:>10s}'.format("OK"), True)
    else:
        pprint.error('{:>10s}'.format("KO"), True)


def check_static_ressources(nginxservice):
    pprint.header("#", False, ' ')
    pprint.log("---- Check ressources statiques /var/www/ ----  ", True)
    var_www_root = "/var/www/parapheur"
    alfresco_root = "/alfresco/"
    applets_root = "/applets/"
    libersign_root = "/libersign/"
    xml_root = "/xml/"
    wsdl = "iparapheur.wsdl"
    applet_jar = "SplittedSignatureApplet.jar"
    make_script = "make.sh"
    xmlmime = "xmlmime"
    wsdl_clean_list = ["location=\"https://", ":443/ws-iparapheur\"/>",
                       ":443/ws-iparapheur-no-mtom\"/>"]
    make_clean_list = ["SERVER_PATH=\"https://libersign-test.",
                       "SERVER_PATH=\"https://libersign.", "\""]
    wsdl_regex = "<soap:address location="
    make_regex = "SERVER_PATH="
    make_expected_url = "libriciel.fr"
    if isexistsdirectory(var_www_root):
        if isexistssubdir(var_www_root, alfresco_root):
            # check_symbolic_link(var_www_root + alfresco_root, wsdl)
            if isexistsfile(var_www_root + alfresco_root, wsdl):
                parse_conf_for_url(var_www_root + alfresco_root + wsdl,
                                   wsdl_regex, nginxservice,
                                   wsdl_clean_list)
        if isexistssubdir(var_www_root, applets_root):
            check_symbolic_link(var_www_root + applets_root, applet_jar)
        if isexistssubdir(var_www_root, libersign_root):
            if isexistsfile(var_www_root + libersign_root, make_script):
                parse_conf_for_url(var_www_root + libersign_root + make_script,
                                   make_regex, make_expected_url,
                                   make_clean_list)
        if isexistssubdir(var_www_root, xml_root):
            isexistsfile(var_www_root + xml_root, xmlmime)


def check_overall_fqdn_consistency(baseinstall, varconfig, varihmconfig):
    pprint.header("#", False, ' ')
    pprint.log("---- Check Coherence FQDN ----  ", True)

    # Point d'entree navigateur
    webFQDN = varihmconfig.get("Parapheur", "parapheur.url")
    # Point d'entree WEB SERVICES
    wsFQDN = varconfig.get("Parapheur", "parapheur.hostname")

    # common error: still have '/iparapheur' at the end of webFQDN
    if webFQDN.endswith("/iparapheur"):
        pprint.header("#", False, ' ')
        pprint.warning("Penser à enlever '/iparapheur' de parapheur.hostname")
        # webFQDN = ini_string.replace(sstring, '')        # TODO encours
        webFQDN = re.sub("/iparapheur$", '', webFQDN)

    # First thing : is the endpoint still alive as it should be ?
    for var_fqdn in [webFQDN, wsFQDN]:
        if not check_server_socket(var_fqdn, 443, False):
            pprint.header("#", False, ' ')
            pprint.info("NginX sur {0}:{1}".format(var_fqdn, 443).
                        ljust(46), False, ' ')
            pprint.warning('{:>10s}'.format("inactif"), True)
    # NginX /etc/nginx/conf.d/parapheur.conf  et  parapheur_ssl.conf
    pprint.log("  todo : check in conf.d/parapheur.conf")
    pprint.log("  todo : check in conf.d/parapheur_ssl.conf")
    # Tomcat scripts/ctl.sh
    pprint.log("  todo : check in scripts/ctl.sh")
    # Tomcat conf/Catalina/localhost/alfresco.xml
    pprint.log("  todo : check in localhost/alfresco.xml")
    # Tomcat   shared/classes/alfresco-global.properties
    pprint.log("  todo : check in alfresco-global.properties")
    # Tomcat   shared/classes/iparapheur-global.properties
    pprint.log("  todo : check in iparapheur-global.properties")
    # WSDL  /var/www/parapheur/alfresco/iparapheur.wsdl
    #   pprint.log("  todo : alfresco/iparapheur.wsdl (améliorer)")
    if not istextinfile("/var/www/parapheur/alfresco/iparapheur.wsdl", wsFQDN):
        pprint.header("#", False, ' ')
        pprint.warning(" -->{0}  absent dans iparapheur.wsdl".format(webFQDN))
    # /etc/hosts  : présence dans /etc/hosts
    if not istextinfile("/etc/hosts", webFQDN):
        pprint.header("#", False, ' ')
        pprint.warning(" -->{0}  absent dans /etc/hosts".format(webFQDN))
    if not istextinfile("/etc/hosts", wsFQDN):
        pprint.header("#", False, ' ')
        pprint.warning(" -->{0}  absent dans /etc/hosts".format(wsFQDN))
    # if not istextinfile("/etc/hosts", "FakeTest"):
    #    pprint.header("#", False, ' ')
    #    pprint.warning(" -->{0}  absent dans /etc/hosts".format("FakeTest"))


def check_ws_mca_status(baseinstalldir):
    pprint.header("#", False, ' ')
    pprint.log("---- Check internal MCA status for web-services ----  ", True)
    acegiPath = baseinstalldir + "/tomcat/webapps/alfresco/WEB-INF/"
    acegiFile = "applicationAcegi.xml"
    if isexistsfile(acegiPath, acegiFile):
        rootAcegi = ET.parse(acegiPath + acegiFile).getroot()
        search_bean = '{http://www.springframework.org/schema/beans}bean'
        search_value = './/{http://www.springframework.org/schema/beans}value'
        for bean in rootAcegi.findall(search_bean):
            value = bean.get('id')
            if value == 'filterChainProxy':
                for a in bean.findall(search_value):
                    value_stuff = a.text
                    # print ('value: ', value_stuff)
                    pprint.header("#", False, ' ')
                    pprint.info("  Configuration {0} ".format(acegiFile).
                                ljust(45), False, ' ')
                    if 'channelProcessingFilter,' not in value_stuff:
                        pprint.success('{:>10s}'.format("no keystore"), True)
                    else:
                        pprint.error('{:>10s}'.format("keystore"), True)


def check_CVE_2020_1938(config):
    # vulnerabilite sur AJP. Solution: virer AJP 8009
    pprint.header("#", False, ' ')
    pprint.log("---- Check CVE-2020-1938 for this server ----  ", False, '  ')
    # checks 127.0.0.1:8009
    #    pprint.header("#", False, ' ')
    #    pprint.info("TOMCAT AJP sur {0}:{1}".format(host, tcp_port).
    #                ljust(46), False, ' ')
    if not check_server_socket("127.0.0.1", 8009, False):
        pprint.success('{:>10s}'.format("protégé"), False)
    else:
        pprint.warning('{:>10s}'.format("vulnérable"), True)
        pprint.warning(" Désactiver le connecteur AJP:8009 dans server.xml")
    pass


def parse_crontab(file, file2):
    file1 = open(file, 'r')
    lines = file1.readlines()
    f = open(file2, "w")
    for line in lines:
        if line.startswith(("0", "1", "2", "3", "4", "5", "6", "7",
                            "8", "9", "*")):
            f.write(line)
    f.close()


def check_crontab_jobs(version_ip_int):
    pprint.header("#", False, ' ')
    pprint.log("---- Check CRONTAB entries ----  ", True)
    vanilla_string = "files/crontab/" + str(version_ip_int) + ".txt"
    expected_crontab = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                    '..', vanilla_string)
    parse_crontab(expected_crontab, "/tmp/expected_crontab.txt")
    os.system('crontab -l > /tmp/crontab.txt')
    parse_crontab("/tmp/crontab.txt", "/tmp/clean_crontab.txt")
    os.system('diff /tmp/expected_crontab.txt /tmp/clean_crontab.txt >'
              ' /tmp/crontab_diff.txt')
    crontab_diff = open("/tmp/crontab_diff.txt", "r")
    lines = crontab_diff.readlines()
    for line in lines:
        if line.startswith("<"):
            pprint.warning(line, False, "")
        elif line.startswith(">"):
            pprint.info(line, False, "")
    os.system('/bin/rm /tmp/expected_crontab.txt /tmp/crontab.txt'
              ' /tmp/clean_crontab.txt /tmp/crontab_diff.txt')


def check_is_multi_tenancy_mode(baseinstalldir, verbose=False):
    pprint.header("#", False, ' ')
    pprint.log("---- Check repository mode ----  ", True)
    pprint.header("#", False, ' ')
    pprint.info("  Mode mono/multi tenancy pour l'entrepot ".
                ljust(45), False, ' ')
    # /opt/iParapheur /tomcat/shared/classes/alfresco/extension/mt/
    mtPath = baseinstalldir + "/tomcat/shared/classes/alfresco/extension/mt/"
    mtFile1 = "mt-admin-context.xml"
    mtFile2 = "mt-contentstore-context.xml"
    mtFile3 = "mt-context.xml"
    if (os.path.exists("{0}/{1}".format(mtPath, mtFile1)) and
            os.path.exists("{0}/{1}".format(mtPath, mtFile2)) and
            os.path.exists("{0}/{1}".format(mtPath, mtFile3))):
        pprint.warning('{:>10s}'.format("multi-tenant"), True)
    else:
        pprint.success('{:>10s}'.format("mono"), False)


################################################################
################################################################
showtheheader()
linux_family = check_hardware()
check_network_needed_basic()
check_required_software()
check_smtp_needed("localhost")

if not check_isexists_alfrescoglobal():
    pprint.error("BAD")
    sys.exit()

ALF_CONFIG_PATH = "{0}/tomcat/shared/classes/alfresco-global.properties".format(defaut_iparapheur_root)  # noqa: E501
IHM_CONFIG_PATH = "{0}/tomcat/shared/classes/iparapheur-global.properties".format(defaut_iparapheur_root)  # noqa: E501
'''
def get_config_app(varfichier):
 ### lire https://stackoverflow.com/questions/2819696/parsing-properties-file-in-python/25493615#25493615  # noqa: E501
 ####   https://stackoverflow.com/questions/2885190/using-pythons-configparser-to-read-a-file-without-section-name
 with open(varfichier, 'r') as f:
     config_string = '[Parapheur]\n' + f.read()
 # config_fp = StringIO.StringIO(config_string)
 config_fp = io.BytesIO(config_string)
 config = ConfigParser.RawConfigParser()
 return config.readfp(config_fp)
'''
with open(ALF_CONFIG_PATH, 'r') as f:
    config_string = '[Parapheur]\n' + f.read()
config_fp = io.BytesIO(config_string)
config = ConfigParser.RawConfigParser()
config.readfp(config_fp)
# alfrescoconfig = get_config_app(CONFIG_PATH)
# print(config.items("Parapheur"))
# print(config.get("Parapheur", "dir.root"))
with open(IHM_CONFIG_PATH, 'r') as f:
    ihmconfig_string = '[Parapheur]\n' + f.read()
ihmconfig_fp = io.BytesIO(ihmconfig_string)
ihmconfig = ConfigParser.RawConfigParser()
ihmconfig.readfp(ihmconfig_fp)
print(config.get("Parapheur", "dir.root"))
print(ihmconfig)

nginxservice = check_https_service_config(config, ihmconfig)

# check health of MySQL configuration
check_mysql_service_config(config)

# tests présence verdanai.ttf , srgb.profile ,etc.
check_files_needed()

# ulimit ET la commande "cd" dans alfresco.sh
check_alfresco_sh(defaut_iparapheur_root, "alfresco.sh")

# ctl.sh : limite à 30 mini pour shutdown

# Controles "anti-fraude"
version_ip = check_iParapheur_version_is_valid(defaut_iparapheur_root)
if version_ip == -1:
    pprint.error("Problème sur déploiement des WAR. STOP.")
    sys.exit()

# tests nettoyage libs obsoletes dans common/lib
check_tomcat_libs_cleanup(version_ip)

# Major shift towards v5 !
if parse_version("4.7.0") <= parse_version(version_ip):
    # new 4.7 PDF renderer
    check_pdfrender_service(version_ip)
    check_network_needed_new()
    # New services: crypto , pdf-stamp , pes-viewer
    check_crypto_service_config()
    check_pdfstamp_service_config()
    check_pesviewer_service_config(defaut_iparapheur_root)
else:
    # check "libgs" bien comme il faut
    check_config_ghostscript()
    # good old xemwebviewer
    check_xemwebview_service_config(defaut_iparapheur_root, version_ip)

# Le connecteur PA a été introduit en v4.6
if parse_version("4.6.0") <= parse_version(version_ip):
    check_pastellconnector_service_config()

# Vérification des éléments dans /var/www/parapheur
check_static_ressources(nginxservice)

# Coherence du parametrage du nom commun FQDN
check_overall_fqdn_consistency(defaut_iparapheur_root, config, ihmconfig)

# Le mode MCA est-il bien désactivé?
check_ws_mca_status(defaut_iparapheur_root)

# Ne manque-t-il pas quelques paramètres?
check_config_alfrescoglobal(config, ihmconfig, version_ip)

# known CVE checks
check_CVE_2020_1938(config)

# check CRONTAB
if parse_version("4.7.0") <= parse_version(version_ip):
    check_crontab_jobs(470)
elif parse_version("4.6.8") <= parse_version(version_ip):
    check_crontab_jobs(468)
elif parse_version("4.6.0") <= parse_version(version_ip):
    check_crontab_jobs(460)
else:
    check_crontab_jobs(450)

# warn if multi-tenancy
check_is_multi_tenancy_mode(defaut_iparapheur_root)

pprint.info(".end.")
