
# Author: Pietro Marini <backvm@fastmail.com>
# License: BSD 3 clause

import sys

import logging

from xml.dom import minidom

from paramiko import SSHClient

from paramiko import WarningPolicy

# https://github.com/jbardin/scp.py
from scp import SCPClient


def get_disks_for_domain(dom_name, conn):
    '''
         # This function returns the list of disks of the domain dom_name
    '''
    dom = conn.lookupByName(dom_name)

    if dom is None:
        logging.info('Failed to find the domain '+dom_name, file=sys.stderr)

        sys.exit(1)

    raw_xml = dom.XMLDesc(0)

    xml = minidom.parseString(raw_xml)

    diskTypes = xml.getElementsByTagName('disk')

    disks = []

    for diskType in diskTypes:

        diskNodes = diskType.childNodes

        for diskNode in diskNodes:

            if diskNode.nodeName[0:1] != '#':

                if 'file' in diskNode.attributes.keys():

                    disks.append(diskNode.attributes['file'].value)

    return raw_xml, disks


def progress4(filename, size, sent, peername):
    sys.stdout.write("(%s:%s) %s's progress: %i%%\r"
            % (peername[0], peername[1],
                filename, float(sent)/float(size)*100))


def success(rc):
    if rc == 0:
        return "SUCCESS"
    else:
        return "FAIL(rc=%s)" % rc


def prepare_scp(dest_server, dest_username, dest_password):
    ssh = SSHClient()

    ssh.set_missing_host_key_policy(WarningPolicy())

    ssh.connect(dest_server, username=dest_username, password=dest_password)

    scp = SCPClient(ssh.get_transport(), progress4=progress4)

    return scp
