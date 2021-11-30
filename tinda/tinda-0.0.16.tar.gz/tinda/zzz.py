import threading
import speech_recognition
from bot import *
import os

os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))


test_json = {"intents": [
        {"tag": "greetings",
        "patterns": ["hi"," greetings", "hello", "hey there", "hey", "hi there", "hiya", "how are ya", "how ya doin", "how are you", "sup", "howdy","yo", "how are things", "good day", "how's it going" ],
        "responses": ["Hi", "Greetings", "Hello", "Hey there", "Hey", "Hi there", "Hiya", "How are you?", "What can i do for you?", "How can i help?", "How you doing?", "Howdy", "Yo!"],
        "context": ["someone trying to greet, to initiate conversation or maybe no reason"]
        },
        {"tag": "goodbye",
        "patterns": ["Bye", "See you later", "Goodbye", "Nice chatting to you, bye", "Till next time"],
        "responses": ["See you!", "Have a nice day", "Bye! Come back again soon."],
        "context": ["saying bye as a parting tradition"]
        },
        {"tag": "cat",
        "patterns":["Cat", "Cat you there", "hey cat", "cat whats up"],
        "responses":["Hey Boss", "I'm here", "Hows it going?", "How can i help?", "What can i do for you?", "What's on your mind"],
        "context":["trying to access cat"]
        },
        {"tag": "time",
        "patterns":["what time is it", "what time of the day", "what time", "time of the day", "current time"],
        "responses":[],
        "context":[]
        },
        {"tag": "date",
        "patterns":["what date is it", "date today", "what date", "date if the month", "current date"],
        "responses":[],
        "context":[]
        }
        ]}



class ZOE:
    def __init__(self):
        self.name = "ZOE"
        self.age = "BINARY"
        self.bias = "not 'utf-8'"
        self.i = XXX()
        self.s = YYY()
    def creep(self):
        for i in range(3):
            print('\n')
        print("ZOE: Initiating creep protocol.")
        for i in range(2):
            print('\n')
        print(self.i.greet())
        print(self.i.date())
        print(f'The time is: {self.i.time()}')
        for i in range(3):
            print('\n')
        print("ZOE: On Standby, waiting for further instructions.")
        while True:
            x = self.i.listen().lower()
            if x == 0:
                continue
            if "zoe" in x:
                print(f"That is one of my aliases, {x}")
            if "what time" in x:
                print(f'The time is: {self.i.time()}')
                self.i.say(f'The time is: {self.i.time()}')
            if "stop" in x:
                print("ZOE: Terminating creep protocol.")
                break
            if "what date" in x:
                print(f'The date is: {self.i.date()}')
                self.i.say(f'{self.i.date()}')
            if "get mouse position" in x:
                print(self.i.mousePosition())
                self.i.say("Roger that!")
            if "left click" in x:
                self.i.leftClick()
                self.i.say("Roger that!")
            if "right click" in x:
                self.i.rightClick()
                self.i.say("pew pew!")
            if "show desktop" in x:
                self.i.showDesktop()
                self.i.say("ooosh!")
            if "open browser" in x:
                self.s.open("www.google.com")
                self.i.say("right up!")



# try:
#     from nope import nope
#     print("KEYS imported!")
# except:
#     print("Failed to locate keys")
#     print("Caution: Some functions might not work")



