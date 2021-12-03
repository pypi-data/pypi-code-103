
# Creating a class for playing Tic Tac Toe

class Board:
    """Creating a tic toc toe Board"""
    def __init__(self):
        """Building 9 boxes for palcing X and O to play the game """
        self.boxes = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
    def show(self):
        """Dispalying the board"""
        print("%s | %s | %s" %(self.boxes[1],self.boxes[2],self.boxes[3]))
        print("----------")
        print("%s | %s | %s" %(self.boxes[4],self.boxes[5],self.boxes[6]))
        print("----------")
        print("%s | %s | %s" %(self.boxes[7],self.boxes[8],self.boxes[9]))

    def update_box(self,Position,Player):
        if self.boxes[Position] == " ":
            self.boxes[Position] = Player

    def Check_game_going(self):
        
        ##Check_rows
        row1 = self.boxes[1]==self.boxes[2]==self.boxes[3] != " "
        row2 = self.boxes[4]==self.boxes[5]==self.boxes[6] != " "
        row3 = self.boxes[7]==self.boxes[8]==self.boxes[9] != " "
        ##Check_cloumns
        col1 = self.boxes[1]==self.boxes[4]==self.boxes[7] != " "
        col2 = self.boxes[2]==self.boxes[5]==self.boxes[8] != " "
        col3 = self.boxes[3]==self.boxes[6]==self.boxes[9] != " "
        ##Check_Diagonals
        dia1 = self.boxes[1]==self.boxes[5]==self.boxes[9] != " "
        dia2 = self.boxes[3]==self.boxes[5]==self.boxes[7] != " "
        # Check who is winner
        if row1 or row2 or row3:
            if row1:
                self.who_is_winner(self.boxes[1])
            if row2:
                self.who_is_winner(self.boxes[5])
                
            if row3:
                self.who_is_winner(self.boxes[8])
                
            game_going = False  
            return game_going

        if col1 or col2 or col3:
            if col1:
                self.who_is_winner(self.boxes[4]) 
            
            if col2:
                self.who_is_winner(self.boxes[2]) 
                        
            if col3:
                self.who_is_winner(self.boxes[3]) 
                

            game_going = False    
            return game_going

        if dia1 or dia2:
            if dia1:
                self.who_is_winner(self.boxes[9])
                
            if dia2:
                self.who_is_winner(self.boxes[7])  

            game_going = False
            return game_going
        
    def who_is_winner(self,Player):
        if Player=="X":
            print("Player 1 is winner")
        else:
            print("Player 2 is winner")
            
    def play_again(self):
        play = input("Would you like to play again?(Y/N):")
        play = str(play)
        if play == "Y":
            return True
            
 
    def reset(self):
        self.boxes = [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
        
    
    def is_tie(self):
        full_box = 0
        for box in self.boxes:
            if box!=" ":
                full_box+= 1
        if full_box==9:
            return True
        else:
            return False
    
   