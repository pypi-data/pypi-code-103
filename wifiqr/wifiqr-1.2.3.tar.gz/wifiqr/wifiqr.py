#author = Pyae Phyo Hein
#idea from https://github.com/kokoye2007/wifi-qr
#MIT License
#https://github.com/lakhanmankani/wifi_qrcode_generator (Some of code copy from this repo)
#31.12.2019
import sys
import os
from . import wifi_qrcode_created
# import wifi_qrcode_created
from . import wifi_qrcode_gener
# import wifi_qrcode_gener
from . import wifi_qrcode_scanner
# import wifi_qrcode_scanner
def wifiqr():
    xdgop = "xdg-open '/tmp/key.png'"
    print('1) Create Wifi QR Code')
    print('2) Generate Wifi QR Code')
    print('3) Scan QR Code')
    chmanu = input('Select Option ')
    if chmanu == "1":
        wifi_qrcode_created.qrcrt()
        os.system(xdgop)
    elif chmanu == "2":
        ssidraw = wifi_qrcode_gener.ssidgen()
        pskraw = wifi_qrcode_gener.pskgen()
        ssid = ssidraw[5:]
        hidden = False
        autheraw = wifi_qrcode_gener.authtype().upper()
        authentication_type = autheraw[9:12]
        password = pskraw[4:]
        code = wifi_qrcode_created.wifi_qrcode(ssid, hidden, authentication_type, password)
        code.save('/tmp/key.png')
        os.system(xdgop)
        print("The qr code has been generated.")
    elif chmanu == "3":
        wifi_qrcode_scanner
    else:
        print('\n\n!!!!!!!!!!!!!!!Something Wrong!!!!!!!!!!!!!!!\n\n')