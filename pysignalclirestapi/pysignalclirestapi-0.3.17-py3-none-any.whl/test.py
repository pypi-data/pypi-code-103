#import sys,os
#sys.path.append(os.getcwd())

#from pysignalclirestapi import SignalCliRestApi
from .api import SignalCliRestApi


a = SignalCliRestApi("http://127.0.0.1:8080", "+4368181186254") #"+4368181186254")
#a = api.SignalCliRestApi("http://192.168.1.20:8080", "+4368120376269")
#print(a.receive())
#print(a.create_group("bla", ["+436802057104"]))
#a.send_message("test", recipients=["group.TTVrS1owancxZW03ekJQK0R1VnNUTXAzQ1kyeU1sd2UrQzR5NGF1b1lVYz0="])
#a.update_profile("test")
#print(a.list_groups())
#a.send_message("--test", recipients=["+436802057104"], filenames=["/home/bernhard/Downloads/Zusammenfassung.pdf"])
#a.send_message("--test", recipients=["+436802057104"], filenames=["/tmp/hero_screenshot.png", "/tmp/hero_screenshot.png"])
a.send_message("test", recipients=["+436802057104"])
