import os
from time import perf_counter
from time import sleep
from turtle import *

QUICKER = 0 # Add more stuff to overflow to combat issues

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
        print("Ordered Coords, X Axis, Y Axis, Time Completed, Extra Time")
        for i in data:
            start = perf_counter()
            raw = i.replace("~", "0").split()
            badge = int(raw[0])
            command = raw[1]

            coords = "Undefined"

            if command == "translate":
                coords = raw[2:]
                x = x+int(coords[0])/3
                y = y+int(coords[1])/3

                setpos(x, y)
            
            elif command == "goto":
                coords = "UNVALID COMMAND: USE TRANSLATE"

            elif command == "rotate":
                right(int(raw[2])-90)

            taken = perf_counter()-start
            full = ((((badge/1000)-(past_badge/1000))-taken)-overflow)-QUICKER

            print(f"{coords} {int(x)} {int(y)} {taken} {full}")
            if full > 0:
                sleep(full)
                overflow = 0
            else:
                overflow = full
            past_badge = badge
        
        end_fill()
        done()
            

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Terminated Simulator")
        print(e)