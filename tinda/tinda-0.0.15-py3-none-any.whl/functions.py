#----------------------------------------------------------------------
##################    MODULES     #####################################
#----------------------------------------------------------------------
try:
    import os
    import sys
    import cv2
    import time
    import math
    import wave
    import random
    import pynput
    import turtle
    import pandas
    import pyaudio
    import platform
    import requests
    import argparse
    import pyautogui
    import threading
    import speedtest
    import webbrowser
    import numpy as np
    import pyttsx3 as tts
    from tqdm import tqdm
    import mediapipe as mp
    import speech_recognition
    from datetime import date
    from bs4 import BeautifulSoup
    from datetime import datetime
    import wikipedia
    from wikipedia.wikipedia import search
    import webbrowser
    print("'+'")
except:
    print("'-'")








#----------------------------------------------------------------------
#   GLOBAL VARIABLES
#----------------------------------------------------------------------

OSname = platform.system()
OsName = platform.platform()

fpfill = "##############################################################"

# spacer - provide int value as parameter.
def pspacer(x=1):
    for i in range(x):
        print("\n")

# random number generator
def rNG(x=0000, y=9999):
    random_number_generator = random.randint(x,y)
    return random_number_generator


def executable(x=""):
    os.startfile(x)

def fileSave(x=""):# takes .extention as input
    naam = str("DOWNLOADED"+str(random.randint(0000,9999))+x)
    return naam

def userInput():
    print("Enter input below:")
    i = input()
    return i


#----------------------------------------------------------------------
# DICTIONATIES, static
#----------------------------------------------------------------------


functions_dict = {"bol":"Using pyttsx3, converts string to audio",
                "open_link_dict": "opens web-browser from links_dict input key",
                "speedTest":"looks for nearest server and tests the internet speed",
                "Skills": "lists all bot skills",
                "openLink": "input link as parameter to open in default web browser",
                "rNG": "GENERATES A RANDOM NUMBER BETWEEN 0000,9999",
                "linkDownload" : "input link as parameter to download in default directory",
                "detectHand" : "Detects hand: d: cv2, mediapipe",
                "imageBlack" : "numpy array generrated black image pop-up on screen",
                "fileSave" : "saves files(no-overwrites) in default directory with DOWNLOADED_name",
                "imageRead" : "Shows image on screen: source required parameter",
                "imageResize" : "(source, scale=50)",
                "imageGray": "Shows grayscaled image of source",
                "imageBlur" : "Shows blurred image",
                "videoRead" : "Shows video on screen from source",
                "execuable" : "starts an executable file: input file path.extention of the file",
                "audioToText" : "dependency: pip install SpeechRecognition",
                "playMusic" : "input music directory",
                "Zoe" : "current if else voice bot version 0.0.0, MOVED TO SEPERATE REPO MEENA",
                "pyPI" : "pypi upload instructuons, zoe knows by 'python index'",
                "Creeper" : "Collets audio data from source for further machine learning processes.",
                "Shutdown" : "Shuts down system in specified time or 10 seconds default",
                "aShutdown" : "aborts shutdown",
                "showDesktop" : "shows desktop using pyautogui",
                "open_cmd" : "if on windows system, opens command prompt",
                "wifi_password" : "netsh wlan show profiles key=clear",
                "HandServo" : "d:pyfirmata, p:('port',pin,angle), servo movement class; zero, one, rotate, back_and_forth, new_angle",
                "get_city" : "returns name of the current city through ip, no parameter required",
                "wifi_password_help" : "only works on windows, does what it says"
                "wiki_search" : "from a given keyword, will return summary from wikipedia",
                "google_image" : "from a given keyword, will open google images in webbroser"}

botSkillsD ={"botType":"needs string input of what to type, waits 3 seconds and will paste the input at the cusor position",
        "botDate":"#Z: print current date",
        "botGetMousePosition":"#Z: gets mouse position as tuple of (x,y)",
        "botGotoMousePosition":"goes to specified mouse position as above parameters",
        "botCloseApp" : "#Z: implemented to close a full screen windows app by left mouse click",
        "botMinimizeApp" : "#Z: implementes to minimize a full screen app on windows",
        "botLeftClick":"#Z: clicks left mouse button and releases right away",
        "botTime":"#Z: prints and says current time in 12 hour format",
        "Time" : "returns time",
        }

linksD = {"youtube":"https://www.youtube.com",
        "google": "https://www.google.com/",
        "github": "https://github.com/",
        "pypi":"https://pypi.org/",
        "netflix": "https://www.netflix.com/browse",
        "instagram": "https://www.instagram.com/",
        "scarlett": "https://images.hdqwalls.com/download/2018-scarlett-johansson-1i-1920x1080.jpg",
        "py_wallpaper" : "https://images.hdqwalls.com/wallpapers/python-programming-syntax-4k-1s.jpg",
        "speechrecognition":"https://www.analyticsvidhya.com/blog/2019/07/learn-build-first-speech-to-text-model-python/",
        "regexCheat" : "https://cheatography.com/mutanclan/cheat-sheets/python-regular-expression-regex/"}

#----------------------------------------------------------------------
#----------------------------------------------------------------------


'''search wikipeadia titles from input query'''
def wiki_titles_search(x=str):
    y = wikipedia.search(x)
    for i in y:
        return i

wiki_titles_search("python")


# wiki_titles_search('deep learning')

def wiki_search(x=str, length=2):
    y = wikipedia.search(x)
    for i in y:
        i = i.lower()
        if i == x:
            z = str(wikipedia.summary(i, length))
            # p = (wikipedia.page(i).content)
            # r = (wikipedia.page(i).references)
            # c = (wikipedia.page(i).categories)
            # l = (wikipedia.page(i).links)
            # t = (wikipedia.page(i).title)
            # print(f'/References are:{r}')
            # print(f'Categories are: {c}')
            # print(f'Links are:{l}')
            # print(f'Title is:{t}')
            return z

# wiki_search('scarlett johansson')

'''open google image from search query in webbrowser'''
def google_image(x=str):
    webbrowser.open(f'https://www.google.com/search?q={x}&tbm=isch')

# google_image('scarlett johansson')


'''extract text from html'''
def get_text_from_html(x=''):
    y = BeautifulSoup(x)        # create a BeautifulSoup object
    # print(y.body.find('div', attrs={'class':'container'}).text)
    return y.body.find('div', attrs={'class':'container'}).text


# helper setup function: not implemented yet.
# ADDING MORE DEPENDENCIES

# def full_setup():
#     try:
#         os.system('pip install Pillow')
#     except Exception as e:
#         print(f"The following error occured: {e}")


#-------------------------------------------------------------------
#-------------------------------------------------------------------


'''search google from query and return result'''
def search_google(query):
    try:
        webbrowser.open_new_tab("https://www.google.com/search?q={}".format(query))
    except Exception as e:
        print(f"The following error occured: {e}")


#-------------------------------------------------------------------
#-------------------------------------------------------------------
# this function is for meenna: 'pip install meena'
'''search youtube from voice input query and return result'''
def search_google_voice():
    recognizer = speech_recognition.Recognizer()
    bol("What are we looking for?")
    done = False
    while not done:
        try:
            with speech_recognition.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio =  recognizer.listen(mic)
                keyword = recognizer.recognize_google(audio)
                keyword = keyword.lower()
                webbrowser.open_new_tab("https://www.youtube.com/results?search_query={}".format(keyword))
                bol("Roger")
        except speech_recognition.UnknownValueError:
            done = True
            recognizer = speech_recognition.Recognizer()

# this function is for meenna: 'pip install meena'
def searchYoutube():
    recognizer = speech_recognition.Recognizer()
    bol("What are we looking for?")
    done = False
    while not done:
        try:
            with speech_recognition.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                audio =  recognizer.listen(mic)
                keyword = recognizer.recognize_google(audio)
                keyword = keyword.lower()
                webbrowser.open_new_tab("https://www.youtube.com/results?search_query={}".format(keyword))
                bol("Roger")
        except speech_recognition.UnknownValueError:
            done = True
            recognizer = speech_recognition.Recognizer()


def killChrome():
    try:
        os.system('TASKKILL /F /IM chrome.exe')
    except:
        pass

def killVlc():
    try:
        os.system('TASKKILL /F /IM vlc.exe')
    except:
        pass

def coldWar():
    coldwarpath = "E:\COLD WAR\Call of Duty Black Ops Cold War\Black Ops Cold War Launcher.exe"
    try:
        subprocess.Popen(coldwarpath)
    except:
        pass



''' Any polygon with number of sides as n, sum of interior angles = (n-2) * 180degrees, each angle = (n-2) * 180degrees / n '''
#d: turtle
class Polygon:
    def __init__(self, sides, name, size = 100, color="purple", Line_thickness=7): #we can also add size of turtle here as a paramerter, and so on, till n (default setting is also an option, exibit A)
        self.name = name
        self.sides = sides
        self.size = size
        self.color = color
        self.Line_thickness = Line_thickness
        self.interior_angles = (self.sides-2)*180
        self.angle = self.interior_angles/self.sides
    def draw(self):
        turtle.pensize(self.Line_thickness)
        turtle.color(self.color)
        for i in range(self.sides):
            turtle.forward(self.size)
            turtle.right(180-self.angle)
        turtle.done()

#d: math
square = Polygon(4, "Square")
pentagon = Polygon(5, "Pentagon")
hexagon = Polygon(6, "Hexagon")
# print(square.sides)
# print(square.name)

# square.draw()
# hexagon.draw()

def volumeOfSphere(r):
    '''Returns the volume of a sphere with the radius r.'''
    vol = (4.0/3.0) * math.pi * r**3
    return vol

def areaOfSphere(r):
    '''Returns the area of a sphere with the radius r.'''
    area = 4 * math.pi * r**2
    return area

def areaOfCircle(r):
    '''Returns the area of a circle with the radius r.'''
    area = math.pi * r**2
    return area

#----------------------------------------------------------------------
#----------------------------------------------------------------------

# CAUTION: only works on windows.
'''gets saved passwords: NETSH'''
def wifi_password():
    '''only works on windows'''
    print("Caution: this method only works on windows")
    import subprocess
    import re
    try:
        command_output = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output = True).stdout.decode()
        profile_names = (re.findall("All User Profile     : (.*)\r", command_output))
        wifi_list = []
        if len(profile_names) != 0:
            for name in profile_names:
                wifi_profile = {}
                profile_info = subprocess.run(["netsh", "wlan", "show", "profile", name], capture_output = True).stdout.decode()
                if re.search("Security key           : Absent", profile_info):
                    continue
                else:
                    wifi_profile["ssid"] = name
                    profile_info_pass = subprocess.run(["netsh", "wlan", "show", "profile", name, "key=clear"], capture_output = True).stdout.decode()
                    password = re.search("Key Content            : (.*)\r", profile_info_pass)
                    if password == None:
                        wifi_profile["password"] = None
                    else:
                        wifi_profile["password"] = password[1]
                    wifi_list.append(wifi_profile)
        for x in range(len(wifi_list)):
            print(wifi_list[x])
    except:
        print("Error: this wasn't supposed to happen.")

#----------------------------------------------------------------------
#----------------------------------------------------------------------

'''moves servo connected with arduino using pyfirmata'''
'''CURRENTLY SETUP TO MOVE BACK AND FORTH UNTIL KEYBOARD INTERRUPTED'''
# required (port, pin number, angle)
#example: move_servo("COM4", 9, 90)
from pyfirmata import Arduino, SERVO
from time import sleep

class HandServo:
    def __init__(self, port, pin, angle):
        self.port = port
        self.pin = pin
        self.angle = angle
        self.board = Arduino(port)
        self.board.digital[pin].mode = SERVO
    def rotate(self, angle):
        self.board.digital[self.pin].write(angle)
        sleep(0.015) # this sleep time is required to keep the servo from overloading
    def back_and_forth(self):   # angle = parameter given.
        try:
            while True:
                for i in range(0, self.angle):
                    self.rotate(i)
                for i in range(self.angle, 1, -1):
                    self.rotate(i)
        except KeyboardInterrupt:
            print("keyboard interrupted")
            self.board.digital[self.pin].write(0)
    def new_angle(self, x=int): # works same as rotate just different sleep time to change speed.
        self.board.digital[self.pin].write(x)
        sleep(0.010)
    def one(self):
        self.board.digital[self.pin].write(180)
        sleep(0.010)
    def zero(self):
        self.board.digital[self.pin].write(0)
        sleep(0.010)

# test_finger = HandServo("COM4", 9, 180)
# test_finger.zero()
# test_finger.rotate(180)

#----------------------------------------------------------------------
#----------------------------------------------------------------------


#----------------------------------------------------------------------
#----------------------------------------------------------------------

'''find current location from ip and return the city name'''
def get_city():
    import requests
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        try:
            import os
            os.system("pip install bs4")
        except Exception as e:
            print(e)
    try:
        from urllib.request import urlopen
    except ImportError:
        try:
            import os
            os.system("pip install urllib")
        except Exception as e:
            print(e)
    response = urlopen('http://ip.42.pl/raw').read()
    ip = response.decode('utf-8')
    url = 'http://ip-api.com/json/' + ip
    response = requests.get(url)
    data = response.json()
    return data['city']

#----------------------------------------------------------------------
#----------------------------------------------------------------------









#----------------------------------------------------------------------
#----------------------------------------------------------------------
##########################  CREEPER  ##################################
#----------------------------------------------------------------------
#----------------------------------------------------------------------

#Creeper: Collets audio data from source for further machine learning processes.
#Outputs a .wav file in default directory.

class Creeper:
    def __init__(self, args):
        self.chunk = 1024
        self.FORMAT = pyaudio.paInt16
        self.channels = 1
        self.sample_rate = args.sample_rate
        self.record_seconds = args.seconds
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        output=True,
                        frames_per_buffer=self.chunk)
    def save_audio(self, frames):
        counter = 0
        naam = "audio{}.wav"
        while os.path.isfile(naam.format(counter)):
            counter += 1
        naam = naam.format(counter)
        print(f"Saving file in default directory named: {naam}")
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        # implemented to save a file called audio followed by a number in default directory.
        # open the file in 'write bytes' mode
        wf = wave.open(naam, "wb")
        # set the channels
        wf.setnchannels(self.channels)
        # set the sample format
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        # set the sample rate
        wf.setframerate(self.sample_rate)
        # write the frames as bytes
        wf.writeframes(b"".join(frames))
        # close the file
        wf.close()
        print('Saved')

def still_creeping(args):
    creeper = Creeper(args)
    frames = []
    print('Creeper is active')
    print('PRESS (crtl + c) to STOP')
    try:
        while True:
            if creeper.record_seconds == None:  # record until keyboard interupt
                data = creeper.stream.read(creeper.chunk)
                frames.append(data)
            else:
                for i in range(int((creeper.sample_rate/creeper.chunk) * creeper.record_seconds)):
                    data = creeper.stream.read(creeper.chunk)
                    frames.append(data)
                raise Exception('done recording')
    except KeyboardInterrupt:
        print('Stopped')
    except Exception as e:
        print(str(e))
    creeper.save_audio(frames)

def creeper():
    parser = argparse.ArgumentParser(description='''creeper backgroung audio collector''')
    parser.add_argument('--sample_rate', type=int, default=8000, help='the sample_rate to record at')
    parser.add_argument('--seconds', type=int, default=None, help='if set to None, then will record forever until keyboard interrupt')
    args = parser.parse_args()
    still_creeping(args)






#-------------------------------------------------------------------
# THESE ARE BASIC PLUG AND PLAY FUNCTIONS WHICH CAN BE USED ANYWHERE IF REQUIRED DEPENDENCIES ARE TRUE
#-------------------------------------------------------------------

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#1
#d: pyttsx3
#string to voice
def bol(audio):
    t = tts.init()
    rate = t.getProperty('rate')
    t.setProperty('rate', '125')
    volume = t.getProperty('volume')
    t.setProperty('volume', 1)
    voices = t.getProperty('voices')
    t.setProperty('voice', voices[1].id)
    t.say(audio)
    t.runAndWait()

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#2
#d: sys, webbrowser
# open default webbbrowser
def openLinkD(x=""):
    webbrowser.open_new_tab(linksD[x])

def openLink(x=""):
    webbrowser.open_new_tab(x)

'''open command prompt in new window'''
def open_cmd():
    try:
        os.startfile("C:\Windows\system32\cmd.exe")
    except:
        print("Error: Command Prompt not found")

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#3 
# Internet speed test
#d: speedtest-cli

def speedTest():
    test = speedtest.Speedtest()
    print("Looking for servers")
    test.get_servers()
    print("Getting closest server details")
    best = test.get_best_server()
    print(f"Located in {best['name']}, {best['country']}, \n")
    download_result = test.download()
    upload_result = test.upload()
    ping_result = test.results.ping
    print(f"Download speed: {download_result/1024/1024 : .2f} Mbit/second")
    print(f"Upload speed: {upload_result/1024/1024 : .2f} Mbit/second")
    print(f"Latency: {ping_result : .2f}ms")


#-------------------------------------------------------------------
#-------------------------------------------------------------------
#4
#d: os.system('pip install pynput')
# control keyboard and mouse using python
# it also supports keyboard and mouse monitoring 
# check pynput documnetation on pypi
# from pynput.keyboard import Key, Controller
# from pynput.mouse import Button, Controller
def botType(x=""):
    keyboard = pynput.keyboard.Controller()
    #sleep time delay; change it according to the task requirement
    time.sleep(3)
    keyboard.type(x)

def botGetMousePosition():
    mouse = pynput.mouse.Controller()
    print('The current cursor position is {0}'.format(mouse.position))

def botGotoMousePosition(x=0, y=0):
    mouse = pynput.mouse.Controller()
    mouse.position = (x,y)

def botLeftClick():
    mouse = pynput.mouse.Controller()
    button = pynput.mouse.Button
    mouse.press(button.left)
    mouse.release(button.left)
    #right click should work the same way saying right

def botCloseApp(): #implemented to close a full screen windows app by mouse click
    mouse = pynput.mouse.Controller()
    mouse.position = (1889, 19)
    button = pynput.mouse.Button
    mouse.press(button.left)
    mouse.release(button.left)

def botMinimizeApp(): #implemented to close a full screen windows app by mouse click
    mouse = pynput.mouse.Controller()
    mouse.position = (1814, 19)
    button = pynput.mouse.Button
    mouse.press(button.left)
    mouse.release(button.left)

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#5
# GENERIC BOT FUNCTIONS
# DATETIME MASTER
# Guido_Van_Rossum = datetime.date(1956, 1, 31)
#d: os.system('pip install datetime)
bot_days_dict = {'0':'Monday',
        '1':'Tuesday',
        '2':'Wednesday',
        '3':'Thursday',
        '4':'Friday',
        '5':'Saturday',
        '6':'Sunday'}

bot_month_dict = {'1':'Janauary',
		'2':'February',
		'3':'March',
		'4':'April',
		'5':'May',
		'6':'June',
		'7':'July',
		'8':'August',
		'9':'September',
		'10':'October',
		'11':'November',
		'12':'December'}

def botDate():
    today = date.today()
    weekday = str(today.weekday())
    day = str(today.day)
    month = str(today.month)
    year = str(today.year)
    print(f"Today is {bot_days_dict[weekday]}, {day} {bot_month_dict[month]}, {year}")
    bol(f"Today is {bot_days_dict[weekday]}, {day}, {bot_month_dict[month]}, {year}")

def botTime():
    current_time = datetime.now()
    time_24f = current_time.strftime('%H:%M')
    time_12f = current_time.strftime('%I:%M %p')
    time = str(time_12f)
    print(time)
    bol(f"Current time is {time}")

def Time():
    current_time = datetime.now()
    time_12f = current_time.strftime('%I:%M %p')
    time = str(time_12f)
    return time

def botGreet():
    hour_of_the_day = datetime.now().hour
    if hour_of_the_day>=0 and hour_of_the_day<12:
        print("Good Morning")
        bol("GOOD Morning")
    elif hour_of_the_day>=12 and hour_of_the_day<18:
        print("Good Afternoon")
        bol("Good Afternoon")
    else:
        print("Good Evening")
        bol('Good Evening')

#-------------------------------------------------------------------
#-------------------------------------------------------------------
#6
#d: requests
# REQUIRES DOWNLOAD LINK INPUT as a string
def linkDownload(x=""):
    #extention_hack = x.split(".")[-1]
    naam = ("DOWNLOADED"+str(rNG())+"."+x.split(".")[-1])
    with requests.get(x, stream=True) as r:
        print("Grabbing")
        with open(naam, 'wb')as f:
            print("Writing")
            for purja in r.iter_content(chunk_size=(1024*8)):
                f.write(purja)
    f.close()
    print("Written!")

#-------------------------------------------------------------------
#-------------------------------------------------------------------

#d: pyautogui
# os.system('pip install pyautogui)
def showDesktop():
    try:
        pyautogui.hotkey('winleft', 'd')
    except:
        try:
            pyautogui.keyDown('winleft')
            pyautogui.press('d')
            pyautogui.keyUp('winleft')
        except:
            pass




#-------------------------------------------------------------------
#-------------------------------------------------------------------
################## OPEN CV FUNCTIONS ###################
#d:         os.system('pip install opencv-python') 
###########################################################

#----------------------------------------------------------------------
#  cv2 IMAGE RELATED FUNTIONS
#----------------------------------------------------------------------
# REQUIRES NUMPY
kernel = np.ones((5,5),np.uint8)
numpyImage = np.zeros((512,512,3),np.uint8)

def imageBlack():
    cv2.imshow("BLACK", numpyImage)
    cv2.waitKey(0)

def imageRead(x=""):
    imageReader = cv2.imread(x)
    cv2.imshow("Image Reader", imageReader)
    cv2.waitKey(0)

# SOURCE = x AND DEFAULT SCALE IS SET TO 50
# CHANGE IT BY PASSING INT VALUE ON A SCALE OF 1 TO 100
def imageResize(x="", scale=50):
    imageReader = cv2.imread(x, cv2.IMREAD_UNCHANGED)
    print("Original Dimentions:", imageReader.shape)
    scale_percent = scale
    width = int(imageReader.shape[1] * scale_percent / 100)
    height = int(imageReader.shape[0] * scale_percent / 100)
    newShape = (width, height)
    reSizer = cv2.resize(imageReader, newShape, interpolation=cv2.INTER_AREA)
    print("Resized dimentions:", reSizer.shape)
    fileName = str(fileSave(".jpg"))
    cv2.imwrite(fileName, reSizer)
    print(f"Saved in default directory as: {fileName}")
    cv2.imshow("Resized Image", reSizer)
    cv2.waitKey(0)
    cv2.destroyAllWindows

def imageGray(x=""):
    imageReader = cv2.imread(x)
    grayedImage = cv2.cvtColor(imageReader, cv2.COLOR_BGR2GRAY)
    cv2.imshow("GREY IMAGE", grayedImage)
    cv2.waitKey(0)

def imageBlur(x=""):
    imageReader = cv2.imread(x)
    # blur vale takes a kernel value which is used 7,7 below; 0 is the sigma x
    # it has to be odd number
    blurredImage = cv2.GaussianBlur(imageReader,(7,7),0)
    cv2.imshow("Blurred IMAGE", blurredImage)
    cv2.waitKey(0)

#Canny Edge detector
def imageEdgeDetect(x="", y=150, z=200):
    imageReader = cv2.imread(x)
    # 100,100 is the threshhold
    edgeCanny = cv2.Canny(imageReader, y, z)
    # iteration changes thickness
    imageDialation = cv2.dilate(edgeCanny, kernel, iterations=1)
    imageErosion = cv2.erode(imageReader, kernel, iterations=1)
    diaEro = cv2.erode(edgeCanny, kernel, iterations=1)
    cv2.imshow("Canny Edge Detector", edgeCanny)
    cv2.imshow("Dialation Erosion", diaEro)
    cv2.imshow("Dialated even more", imageDialation)
    cv2.imshow("Eroded Image", imageErosion)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#----------------------------------------------------------------------
#   cv2 VIDEO RELATED FUNCTIONS
#----------------------------------------------------------------------

def videoRead(x=""):
    watcher = cv2.VideoCapture(x)
    watching = True
    while watching:
        guard, frame = watcher.read()
        cv2.imshow("Video Reader", frame)
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            break
    watching = False
    cv2.destroyAllWindows()

#----------------------------------------------------------------------
#----------------------------------------------------------------------

##################### HAND DETECTOR #######################
#d:         os.system('pip install mediapipe') 
#d:         os.system('pip install opencv-python') 
###########################################################

#----------------------------------------------------------------------
#----------------------------------------------------------------------
class HandDetector:
    """
    Finds Hands using the mediapipe library. Exports the landmarks
    in pixel format. Adds extra functionalities like finding how
    many fingers are up or the distance between two fingers. Also
    provides bounding box info of the hand found.
    """
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, minTrackCon=0.5):
        """
        :param mode: In static mode, detection is done on each image: slower
        :param maxHands: Maximum number of hands to detect
        :param detectionCon: Minimum Detection Confidence Threshold
        :param minTrackCon: Minimum Tracking Confidence Threshold
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,
                                        self.detectionCon, self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []
    def findHands(self, img, draw=True):
        """
        Finds hands in a BGR image.
        :param img: Image to find the hands in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                            self.mpHands.HAND_CONNECTIONS)
        return img
    def findPosition(self, img, handNo=0, draw=True):
        """
        Finds landmarks of a single hand and puts them in a list
        in pixel format. Also finds the bounding box around the hand.
        :param img: main image to find hand in
        :param handNo: hand id if more than one hand detected
        :param draw: Flag to draw the output on the image.
        :return: list of landmarks in pixel format; bounding box
        """
        xList = []
        yList = []
        bbox = []
        bboxInfo =[]
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                px, py = int(lm.x * w), int(lm.y * h)
                xList.append(px)
                yList.append(py)
                self.lmList.append([px, py])
                if draw:
                    cv2.circle(img, (px, py), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            boxW, boxH = xmax - xmin, ymax - ymin
            bbox = xmin, ymin, boxW, boxH
            cx, cy = bbox[0] + (bbox[2] // 2), \
                     bbox[1] + (bbox[3] // 2)
            bboxInfo = {"id": id, "bbox": bbox,"center": (cx, cy)}
            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                            (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                            (0, 255, 0), 2)
        return self.lmList, bboxInfo
    def fingersUp(self):
        """
        Finds how many fingers are open and returns in a list.
        Considers left and right hands separately
        :return: List of which fingers are up
        """
        if self.results.multi_hand_landmarks:
            myHandType = self.handType()
            fingers = []
            # Thumb
            if myHandType == "Right":
                if self.lmList[self.tipIds[0]][0] > self.lmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                if self.lmList[self.tipIds[0]][0] < self.lmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            # 4 Fingers
            for id in range(1, 5):
                if self.lmList[self.tipIds[id]][1] < self.lmList[self.tipIds[id] - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers
    def findDistance(self, p1, p2, img, draw=True):
        """
        Find the distance between two landmarks based on their
        index numbers.
        :param p1: Point1 - Index of Landmark 1.
        :param p2: Point2 - Index of Landmark 2.
        :param img: Image to draw on.
        :param draw: Flag to draw the output on the image.
        :return: Distance between the points
                Image with output drawn
                Line information
        """
        if self.results.multi_hand_landmarks:
            x1, y1 = self.lmList[p1][0], self.lmList[p1][1]
            x2, y2 = self.lmList[p2][0], self.lmList[p2][1]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            if draw:
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            length = math.hypot(x2 - x1, y2 - y1)
            return length, img, [x1, y1, x2, y2, cx, cy]
    def handType(self):
        """
        Checks if the hand is left or right
        :return: "Right" or "Left"
        """
        if self.results.multi_hand_landmarks:
            if self.lmList[17][0] < self.lmList[5][0]:
                return "Right"
            else:
                return "Left"


def detectHand(x=""):
    # 'x' is the source/takes source as input.
    watcher = cv2.VideoCapture(x)
    detector = HandDetector(maxHands=1, detectionCon=0.7)
    watching = True
    while True:
        success, frame = watcher.read()
        handerson = detector.findHands(frame)
        lmList, bbox = detector.findPosition(handerson)
        cv2.imshow("M: Hand Detector", handerson)
        if cv2.waitKey(1) & 0xFF ==ord('q'):
            break
    watching = False
    cv2.destroyAllWindows()


#----------------------------------------------------------------------
#----------------------------------------------------------------------
##########################  ZOE  ######################################
#----------------------------------------------------------------------
#----------------------------------------------------------------------

# pip install meena (if else VI named Zoe)
def audioToText():
    listener = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        listener.adjust_for_ambient_noise(source, duration=0.2)
        listen = listener.listen(source)
        try:
            data = listener.recognize_google(listen)
            print(f"#Zoe: I think you said:  {data}")
        except  speech_recognition.UnknownValueError:
            listener = speech_recognition.Recognizer()
            return "None"
        return data

#-------------------------------------------------------------------
#-------------------------------------------------------------------

def playMusic(x=""):# x = music directory path
    song = os.listdir(x)
    n = rNG(0, len(song))
    print(f"Here are all the found file:\n{song}")
    os.startfile(os.path.join(x,song[n]))

#-------------------------------------------------------------------
#-------------------------------------------------------------------

def pyPI():
    info = """
    It's pretty easy actualy,
    make a basefolder, name does not matter,
    in this folder name another folder, name of that folder is name of the repo,
    in that folder name __init__.py file with import statement linked to the code,
    and also the code file,
    outside this folder in the basefolder make licence, readme, and setup.py file,
    once everything is done, in CMD, run,
    for exact code check info on the screen\n
    change directory to the base folder
    you'll need to install pip, wheel, twine and setuptools,
    once all that i sdone, run the following command\n
    python setup.py bdist_wheel
    python setup.py sdist bdist_wheel,
    twine upload dist\*,
    here you'll need your username and password,
    once all this is done correctly, the upload should have been done.
    """
    print(info)
    bol(info)


#-------------------------------------------------------------------
#-------------------------------------------------------------------



#d: import os
#d: import platform
# this will shutdown the computer, default time is set to 10 seconds
# can be changed by passing int value inside the () while executing
def Shutdown(shutdown_time: int = 10):#default set to 10 seconds
    print(f"Shuttin down system in: {shutdown_time} seconds")
    """For Windows, time should be given in seconds
        For MacOS and Linux based distributions, time should be given in minutes"""
    if "window" in OSname.lower():
        cont = "shutdown -s -t %s" % shutdown_time
        os.system(cont)
    elif "linux" in OSname.lower():
        cont = "shutdown -h %s" % shutdown_time
        os.system(cont)
    elif "darwin" in OSname.lower():
        cont = "shutdown -h -t %s" % shutdown_time
        os.system(cont)
    else:
        raise Warning("This function is for Windows, Mac and Linux users only, can't execute on %s" % OSname)


#----------------------------------------------------------------------
#----------------------------------------------------------------------
#same dependencies as above: os and platform
#this will abort shutdowm

def aShutdown():
    """Will cancel the scheduled shutdown"""
    if "window" in OSname.lower():
        cont = "shutdown /a"
        os.system(cont)
        print("Shutdown has been Cancelled!")
    elif "linux" in OSname.lower():
        cont = "shutdown -c"
        os.system(cont)
        print("Shutdown has been Cancelled!")
    elif "darwin" in OSname.lower():
        cont = "killall shutdown"
        os.system(cont)
        print("Shutdown has been Cancelled!")




#----------------------------------------------------------------------
#----------------------------------------------------------------------
#it should shutdown the system immediately.
def KILLALL(shutdown_time: int = 0):
    """For Windows, time should be given in seconds
        For MacOS and Linux based distributions, time should be given in minutes"""
    if "window" in OSname.lower():
        cont = "shutdown -s -t %s" % shutdown_time
        os.system(cont)
    elif "linux" in OSname.lower():
        cont = "shutdown -h %s" % shutdown_time
        os.system(cont)
    elif "darwin" in OSname.lower():
        cont = "shutdown -h -t %s" % shutdown_time
        os.system(cont)
    else:
        raise Warning("This function is for Windows, Mac and Linux users only, can't execute on %s" % OSname)

#----------------------------------------------------------------------
#----------------------------------------------------------------------




#----------------------------------------------------------------------
#----------------------------------------------------------------------
######################## HOR DASS AAMB BHALDI? ########################
#----------------------------------------------------------------------
#----------------------------------------------------------------------


############# ALL FUNCTION LISTED THROUGH FUNCTION HELPER FUNCTIONS ###############

def usage():
    print(fpfill)
    print("     All functions are listed below, use as you may.")
    print(fpfill)
    print('\n')
    counter = 1
    for key in functions_dict:
        print(counter, ":", key, "::", functions_dict[key])
        print("\n")
        counter += 1

def linksList():
    print(fpfill)
    print("KEY : ASSIGNED LINK FOR TESTING")
    print(fpfill)
    print('\n')
    counter = 1
    for key in linksD:
        print(key, ":", linksD[key])

def botSkills():
    print(fpfill)
    print("Current bot skills are listed below:")
    print(fpfill)
    print('\n')
    counter = 1
    for key in botSkillsD:
        print(counter, ":", key, "::", botSkillsD[key])
        print("\n")
        counter += 1

def bot():
    botGreet()
    botDate()
    botTime()
    bol("I am listing all the available 'FUNCTIONS' down below, feel free to scrool up")
    usage()
    botSkills()
    botGetMousePosition()
    linksList()
    bol('bye now')


if __name__ == '__main__':
    # bot()
    print("'?'")

#----------------------------------------------------------------------
#----------------------------------------------------------------------
######################## HOR DASS AAMB BHALDI? ########################
#----------------------------------------------------------------------
#----------------------------------------------------------------------

