import os
from time import perf_counter
from time import sleep
from turtle import *

def main():

    color('blue')
    title("Viking Instruction Simulator")

    file_path = textinput("Viking Instruction Simulator", "Enter file to run in simulator")

    if os.path.exists(file_path):
        with open(file_path) as f:
            data = f.read().splitlines()

        overflow = 0
        past_badge = 0
        x = 0
        y = 0
        for i in data:
            start = perf_counter()
            raw = i.replace("~", "0").split()
            coords = raw[2:]
            badge = int(raw[0])
            command = raw[1]

            if command == "goto":
                x = x+int(coords[0])/5
                y = y+int(coords[1])/5

            setpos(x, y)
            print(coords)

            taken = perf_counter()-start
            full = ((badge/10000)-(past_badge/10000))-taken
            if full > 0:
                sleep(full)
            past_badge = badge
        
        end_fill()
        done()
            

if __name__ == "__main__":
    main()