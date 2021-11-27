"""Contains all the necessary code to run various features like searching in net,running files,etc"""
import datetime
import difflib
import os
import random
import subprocess
import webbrowser
from pathlib import Path

from talk1.talk1 import talk


# .....Time and Greeting............
def greeting(nam):
    """Function to greet the user based on time of the day"""
    try: talk(f"Good morning {nam}") if datetime.datetime.now().hour < 12 else talk(f"Good evening {nam}")
    except Exception as e: print(e, "Sorry i could not do what you requested. Try again later")


def tell_time():
    """"To tell the current time"""
    talk(f"It is {datetime.datetime.now().hour} {datetime.datetime.now().minute}")


# ...........Programmes..........................
def wordpad():
    try:
        subprocess.Popen("C:\\Windows\\System32\\write.exe")
        talk('I have opened wordpad for you')
    except Exception as e: print(e, "Sorry i could not do what you requested. Try again later")


def whatsapp():
    try:
        subprocess.Popen(os.path.join(os.path.join(os.environ["USERPROFILE"]), "AppData\\Local\\WhatsApp\\WhatsApp.exe"))
        talk('I have opened whatsapp for you')

    except Exception as e: print(e, "Sorry i couldn't do what you requested Try again later")


def gimp():
    try:
        subprocess.Popen("C:\\Program Files\\GIMP 2\\bin\\gimp-2.10.exe")
        talk("I have opened gimp for you")
    except: talk("Sorry i could not open gimp ")


def firefox():
    try:
        subprocess.Popen("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
        talk("i have opened firefox for you")
    except: talk("Sorry, could not open firefox")


def photoshop():
    try:
        os.system("start photoshop")
        talk("i have opened photoshop for you")
    except: talk("Sorry, could not open photoshop")


def vscode():
    try:
        os.system("code")
        talk("i have opened visual studio code for you")
    except: talk("Sorry, could not open visual studio code")


def vlc():
    try:
        os.system("vlc")
        talk("i have opened vlc for you")
    except: talk("Sorry, could not open vlc")


def telegram():
    try:
        os.system("telegram")
        talk("i have opened telegram for you")
    except: talk("Sorry, could not open telegram ")


def powerpoint():
    try:
        os.system("start powerpnt")
        talk("i have opened powerpoint for you")
    except: talk("Sorry, could not open powerpoint ")


def msword():
    try:
        os.system("start winword")
        talk("i have opened word for you")
    except: talk("Sorry, could not open word")


def calc():
    try:
        os.system("calc")
        talk("i have opened calculator for you")
    except: talk("Sorry, could not open calculator")


def notepad():
    try:
        os.system("notepad")
        talk("i have opened notepad for you")
    except: talk("Sorry, could not open notepad")


# .........browser and net related................
def web(searchword):
    try:
        webbrowser.open(("https://www.google.com/search?client=firefox-b-d&q=" + searchword), new=1)
        talk(f"This is what I found for {searchword}")
    except:
        webbrowser.open(searchword, new=1)
        print("Sorry i could not do what you requested Try again later")


def youtube(srch):
    webbrowser.open(f"https://www.youtube.com/results?search_query={srch}")
    talk('Here is what you requested')

# .............folders......................
def download():
    try:
        os.startfile(Path(os.path.join(os.path.join(os.environ["USERPROFILE"]), "Downloads")))
        talk('Here is what you requested')
    except: talk("Sorry, could not open the downloads folder")


def desktop():
    try:
        os.startfile(Path(os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")))
        talk('Here is what you requested')
    except: talk("Sorry, could not open the desktop folder")


def musicFolder():
    try:
        os.startfile(Path(os.path.join(os.path.join(os.environ["USERPROFILE"]), "Music")))
        talk('Here is what you requested')
    except:
        talk("Sorry, could not open the Music folder")


def joke():
    try:
        jokeslist = [
            "My friend was explaining electricity to me, but I was like, wat ?",
            "I failed math so many times at school, I can’t even count",
            "Never trust atoms; they make up everything",
            "George is searchword fool",
            "The future, the present, and the past walk into searchword bar. Things got searchword little tense",
            "It was an emotional wedding. Even the cake was in tiers",
            ]
        jokeselected = random.choice(jokeslist)
        talk(jokeselected)
    except: talk("Give me time to think. please try again")


# ...........shutdown,restart and log off.....
def shutdown():
    try:
        # /s is for shutdown ,/t is for timeout and 5 is the delay time
        talk("Shutting down your computer in 5 seconds. Bye bye")
        subprocess.call(["shutdown", "/s", "/t", "5"])
    except: talk("Sorry.Something went wrong")


def restart():
    try:
        # /r is for restart ,/t is for timeout and 5 is the delay time
        talk("Restarting your computer in 5 seconds. Bye bye")
        subprocess.call(["shutdown", "/r", "/t", "5"])
    except: talk("Sorry.Something went wrong")


webdict = {
    "facebook": "https://www.facebook.com/",
    "instagram": "https://www.instagram.com/",
    "insta": "https://www.instagram.com/",
    "whatsapp": "https://web.whatsapp.com/",
    "wa": "https://web.whatsapp.com/",
    "george": "https://github.com/georgerahul24",
    "elizabeth": "https://github.com/swarley2021",
    "austin": "https://github.com/AustinBert",
    "parthan": "https://github.com/PARTHAN27",
    "diya": "https://github.com/diyapratheep123",
    "netflix": "https://www.netflix.com/",
    "primevideo": "https://www.primevideo.com/",
    "hotstar": "https://www.hotstar.com/",
    "spotify": "https://www.spotify.com/",
    "pinterest": "https://in.pinterest.com/",
    "quora": "https://www.quora.com/",
    "meet": "https://meet.google.com",
    }
websitelist = [web for web in webdict]


# ......websites..............
def websiteopen(website):
    try:
        approx_match = difflib.get_close_matches(website, websitelist, cutoff=0.7, n=1)
        print(f"Approximated {website} to {approx_match[0]}")
        webbrowser.open(webdict[approx_match[0]])
        talk(f"opening {approx_match[0]}")
    except: talk(f"Sorry,could not find {website}")
