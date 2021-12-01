import qrcode
import os
import re
def ssidgen():
    os.system("ls -1 /etc/NetworkManager/system-connections/ > /tmp/wifilist.txt")
    with open("/tmp/wifilist.txt", 'r') as file_handle:
    # read file content into list
        lines = file_handle.readlines()
# print list content
    for x in range(len (lines)):
        linex=lines[x]
        print(f"({x}) >>> {linex[0:-14]}")
    # print()
    inputnum = int(input("Enter Number of Name:"))
    print('\n')
    catt = lines[inputnum].rstrip("\n")
    # print(catt)
    os.system(f" sudo cat /etc/NetworkManager/system-connections/'{str(catt)}' > /tmp/wifi.txt",)
    file_handle.close()
    f = open("/tmp/wifi.txt",'r')
    with f as open_file:
        data = open_file.read()
        reg = []
        reg = re.findall(r'ssid=.*',data)
        for i in reg:
            #print (i)
            return i
        return ssidgen()
def pskgen():
    # os.system("ls -l /etc/NetworkManager/system-connections/")
    # catt = input("Enter wifiName:")
    # os.system(f" sudo cat /etc/NetworkManager/system-connections/{catt} > /tmp/wifi.txt",)
    f = open("/tmp/wifi.txt",'r')
    with f as open_file:
        data = open_file.read()
        reg = []
        reg = re.findall(r'psk=.*',data)
        for i in reg:
            #print (i)
            return i
        return pskgen()
def authtype():
    # os.system("ls -l /etc/NetworkManager/system-connections/")
    # catt = input("Enter wifiName:")
    # os.system(f" sudo cat /etc/NetworkManager/system-connections/{catt} > /tmp/wifi.txt",)
    f = open("/tmp/wifi.txt",'r')
    with f as open_file:
        data = open_file.read()
        reg = []
        reg = re.findall(r'key-mgmt=.*',data)
        for i in reg:
            #print (i)
            return i
        return authtype()
