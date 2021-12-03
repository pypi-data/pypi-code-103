import os
os.system("clear")
from Board_org import Board


#### Global Variables

game_going = True

Winner = None
Player1 = "X"
Player2 = "O"

Full_game = Board() 

def Header():
    print("Tic Tac Toe Game:")

def refresh():
    os.system("clear")
    Header()
    Full_game.show()

while game_going:
        refresh()
        pos = input("Player1: Choose from 1 to 9:")
        pos = int(pos)
        Full_game.update_box(pos,"X")
        refresh()
        if Full_game.Check_game_going() == False: 
            if Full_game.play_again() == True:
                Full_game.reset()
                continue
            else:
                break
                
        if Full_game.is_tie()== True:
            print("\n Game is Tie.\n")
            if Full_game.play_again() == True:
                Full_game.reset()
                continue
            else:
                break
           
        pos = input("Player2: Choose from 1 to 9:")
        pos = int(pos)
        Full_game.update_box(pos,"O")
        refresh()
        if Full_game.Check_game_going() == False: 
            if Full_game.play_again() == True:
                Full_game.reset()
                continue
            else:
                break
                
        if Full_game.is_tie()== True:
            print("\n Game is Tie.\n")
            if Full_game.play_again() == True:
                Full_game.reset()
                continue
            else:
                break
        
print("Game is over")    


