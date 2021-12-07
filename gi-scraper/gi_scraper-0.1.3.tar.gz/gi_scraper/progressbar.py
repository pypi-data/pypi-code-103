import sys
import time

class ProgressBar:
    def __init__(self, total=100, message=''):
        self.start = time.time()
        self.total = int(total)
        self.message = message
    
    def ProgressBar(self, current):
        current = int(current)
        if current > self.total:
            current, self.total = self.total, current
        percent = int((current/self.total) * 100)
        val = int(percent / 4)
        if len(self.message) != 0:
            sys.stdout.write("\r" + self.message + " ... [")
        else:
            sys.stdout.write("\r[")
        for i in range(val):
            sys.stdout.write("|")
        for i in range(25 - val):
            sys.stdout.write(" ")
        sys.stdout.write("] " + str(percent) + "%\r")
    
    def __del__(self):
        sys.stdout.flush()
        print("\n Completed in... " + str(round(time.time() - self.start, 2)) + "s")
