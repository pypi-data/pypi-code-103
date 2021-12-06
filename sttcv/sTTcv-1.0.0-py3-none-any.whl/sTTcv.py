import pyttsx3 as pyt
import sys
import os
import itertools
import threading
import time
from gtts import gTTS


class Convert:

	def __init__(self, path):
		self.engine = pyt.init()

		with open(path, "r") as file:
			self.file = file.read()

	def say(self):
		self.engine.say(self.file)
		self.engine.runAndWait()

	def save(self, filename):
		tts = gTTS(text = self.file, lang = "ru")
		tts.save(filename)

named = ('output.mp3')

print('Success! Results:')
Convert("input.txt").say()

os.system('cls')

print('Saving "mp3" audio file....')

done = False
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rSaving ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')

t = threading.Thread(target=animate)
t.start()

Convert("input.txt").save(named)

time.sleep(3)
done = True
time.sleep(3)