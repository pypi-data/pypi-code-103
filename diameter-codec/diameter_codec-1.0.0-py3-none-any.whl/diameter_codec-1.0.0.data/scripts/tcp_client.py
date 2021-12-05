#!python

import os
import uuid
from pprint import pprint
from urllib.parse import urlparse
from ipaddress import ip_address
import socket
import typing
from datetime import datetime

from codec.diameter.diameter import Avp, DiameterHeader, Diameter
from codec.diameter.dictionary import DictionaryLayout, DefaultDictionaryLayout


def cer(host, port, xml_dict_path):
    avp_set: typing.Tuple = (
        Avp("Product-Name", "hello"),
        Avp("Origin-Realm", "zte.com.cn"),
        Avp("Origin-Host", "dmtsrv001.zte.com.cn")
    )
    dictionary_layout: DictionaryLayout = DefaultDictionaryLayout(xml_dict_path)
    header: DiameterHeader = DiameterHeader(application_id=0, command_code=257, avp_set=avp_set)
    encoded_message: bytes = Diameter(dictionary_layout).encode(header)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(encoded_message)
        data = s.recv(4096)
        print('Received', repr(data))


def s6b(host, port, xml_dict_path):
    avp_set: typing.Tuple = (
        Avp("Framed-IP-Address", ip_address('192.168.0.1')),
        Avp("Event-Timestamp", int(datetime.now().timestamp())),
        Avp("Acct-Session-Id", "test-29091980"),
        Avp("Origin-State-Id", 1),
        Avp("Acct-Multi-Session-Id", str(uuid.uuid4())),
        Avp("Origin-Host", "dmtsrv001.zte.com.cn"),
        Avp("Origin-Realm", "zte.com.cn"),
        Avp("Redirect-Host", urlparse("aaa://host.example.com;transport=tcp")),
        Avp("Redirect-Host-Usage", "ALL_USER"),
        Avp("Redirect-Host-Usage", "UNKNOWN"),
        Avp("Redirect-Host-Usage", ""),
        Avp("Redirect-Host-Usage", None),
        Avp("Error-Message", ""),
        Avp("WLAN-Identifier",
            (
                Avp("SSID", "etisalat-roam001"),
            )),
        Avp("EPS-Subscribed-QoS-Profile", (
           Avp("Allocation-Retention-Priority", (
                Avp("Priority-Level", 1),
            )),
         )),
    )

    dictionary_layout: DictionaryLayout = DefaultDictionaryLayout(xml_dict_path)
    header: DiameterHeader = DiameterHeader(application_id=16777250, command_code=265, avp_set=avp_set)
    encoded_message: bytes = Diameter(dictionary_layout).encode(header)
    pprint(f'send header={header} to server as encoded_message={encoded_message}')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(encoded_message)
        data = s.recv(4096)
        print('Received', repr(data))


def client():
    host = '127.0.0.1'
    port = 3868
    xml_dict_path: str = f'{os.getcwd()}/src/unittest/python/Diameter.xml'
    #   cer(host, port, xml_dict_path)
    s6b(host, port, xml_dict_path)


if __name__ == "__main__":
    client()
