
# dependencies:





from urllib.parse import _NetlocResultMixinBase
import pyttsx3 # text to speech
import random # random.randint(1, 10)
import os # os.system 
import pynput # keyboard and mouse utility
import time
from datetime import datetime
from datetime import date
import pyautogui # mouse and keyboard utility
import speech_recognition  # pip install SpeechRecognition (working currently py -3.9)
import webbrowser as webb # webbrowser.open("https://www.google.com")
import wikipedia # pip install wikipedia

class XXX:
    def __init__(self):
        self.days = {'0':'Monday',
        '1':'Tuesday',
        '2':'Wednesday',
        '3':'Thursday',
        '4':'Friday',
        '5':'Saturday',
        '6':'Sunday'}
        self.months = {'1':'Janauary',
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
        self.task = pyttsx3.init()
        rate = self.task.getProperty('rate')
        self.task.setProperty('rate', 150)
        volume = self.task.getProperty('volume')
        self.task.setProperty('volume', 1)
        voices = self.task.getProperty('voices')
        self.task.setProperty('voice', voices[1].id)
    def say(self, audio):
        self.task.say(audio)
        self.task.runAndWait()
    def randomNumber(self):
        return random.randint(0000, 9999)
    def execute(self, path):
        os.startfile(path)
    def repeatAfterMe(self):
        self.task.say(input("Enter what to say: "))
        self.task.runAndWait()
    def type(self, text):
        x = pynput.keyboard.Controller()
        time.sleep(3)
        x.type(text)
    def mousePosition(self):
        x = pynput.mouse.Controller()
        return x.position
    def goToPosition(self, x=0, y=0):
        x = pynput.mouse.Controller()
        x.position = (x, y)
    def leftClick(self):
        x = pynput.mouse.Controller()
        y = pynput.mouse.Button
        x.press(y.left)
        x.release(y.left)
    def rightClick(self):
        x = pynput.mouse.Controller()
        y = pynput.mouse.Button
        x.press(y.right)
        x.release(y.right)
    def time(self):
        x = datetime.now()
        x24 = x.strftime('%H:%M')
        x12 = x.strftime('%I:%M %p')
        time = str(x12)
        return time
    def date(self):
        today = date.today()
        weekday = str(today.weekday())
        day = str(today.day)
        month = str(today.month)
        year = str(today.year)
        x= (f"Today is: {self.days[weekday]}, {day} {self.months[month]}, {year}.")
        return x
    def greet(self):
        x = datetime.now().hour
        if x >=0 and x < 12:
            return "Good Morning"
        elif x >=12 and x < 18:
            return "Good Afternoon"
        else:
            return "Good Evening"
    def showDesktop(self):
        try:
            pyautogui.hotkey('winleft', 'd')
        except:
            try:
                pyautogui.keyDown('winleft')
                pyautogui.press('d')
                pyautogui.keyUp('winleft')
            except:
                pass
    def listen(self):
        x = speech_recognition.Recognizer()
        with speech_recognition.Microphone() as source:
            x.adjust_for_ambient_noise(source, duration=0.2)
            y = x.listen(source)
            try:
                r = x.recognize_google(y)
                print(f"#ZOE: #I heard: {r}")
            except speech_recognition.UnknownValueError:
                x = speech_recognition.Recognizer()
                return "None"
            return r
    def pyaudioWindowInstall(self):
        os.system("pip install pipwin")
        os.system("pipwin install pyaudio")
        os.system("python -m pip install pyaudio")
    def playMusic(self, path):
        x = os.listdir(path)
        os.startfile(os.path.join(path, random.choice(x)))
    def showdown(self):
        try:
            os.system("shutdown /s /t 1")
        except:
            return "Negavite"
    def cancelShutdown(self):
        try:
            os.system("shutdown /a")
        except:
            return "Negavite"

class YYY: # search related functions
    def __init__(self):
        self.b = webb
    def open(self, url): # webbrowser open
        self.b.open(url)
    def wiki(self, text): # wikipedia search
        return wikipedia.search(text)
    def wikiSummary(self, text): # wikipedia summary
        wikipedia.set_lang("en")
        return wikipedia.summary(text, sentences=2)
    def image(self, text): # google image search
        self.b.open(f'https://www.google.com/search?q={text}&tbm=isch')
    def google(self, text): # google search
        self.b.open(f'https://www.google.com/search?q={text}')
    def youtube(self, text): # youtube search
        self.b.open(f'https://www.youtube.com/results?search_query={text}')
    def stackoverflow(self, text): # stackoverflow search
        self.b.open(f'https://stackoverflow.com/search?q={text}')
    def github(self, text): # github search
        self.b.open(f'https://github.com/search?q={text}')




