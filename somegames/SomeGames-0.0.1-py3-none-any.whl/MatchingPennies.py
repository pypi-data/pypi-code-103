import numpy as np
import time

class _FirstGame:
    
    def __init__(self):
        self._choice_scheme = {0:'head', 1:'tail'}
        self._house_score = 0
        self._player_score = 0
        self._player_choice = ''
        self._coin_toss = ''
        
    def play_game(self):
        print(self._get_instructions())
        while True:
            self._play_round()
            if self._play_again() == 'n':
                break
            print("\n")
        self._ending_prompt()
        
    def _get_instructions(self):
        return "Game Rules: \nChoose either head or tail. \
If your choice accurately predicts the coin toss, you win. If not, you lose.\n"
        
    def _play_round(self):
        self._get_outcomes()
        self._determine_winner()
    
    def _get_input(self):
        self._player_choice = str(input("      Your choice: ")).lower()
        # looping until a valid input is entered
        while self._player_choice not in self._choice_scheme.values():
            self._player_choice = str(input("Enter a valid input: ")).lower()
    
    def _play_again(self):
        ans = str(input("Play again? (Y/N)")).lower()
        while ans not in ['n','y']:
            ans = str(input("Play again? (Y/N)")).lower()
        return ans

    def _get_outcomes(self):
        self._get_input()
        self._coin_toss = self._choice_scheme[np.random.randint(2)]

        print("      Your choice:", self._player_choice)
        print("Coin toss outcome:", end='\r')
        time.sleep(1)
        print("Coin toss outcome:", self._coin_toss)

    def _determine_winner(self):
        if self._player_choice == self._coin_toss:
            self._player_score += 1
        else:
            self._house_score += 1
        print("Score card:")
        print('You {}-{} House'.format(self._player_score, self._house_score))
        
    def _ending_prompt(self):
        print("\n")
        if self._house_score < self._player_score:
            print("<== You win ==>")
        elif self._house_score > self._player_score:
            print("\n<== House wins ==>")
        else:
            print("Game is Tied")
        print("Thanks for playing")

            
            
            
class _SecondGame(_FirstGame):
    def __init__(self):
        super().__init__()
        
    def _get_instructions(self):
        return super().get_instructions() + "For the first round, the winner wins $1 and the loser loses $1. \
For each additional round you play, you either you can double your current bank or make it zero."
        
    def _running_winnings(self):
        return abs(self._player_score) if self._player_score != 0 else 1
        
    def _determine_winner(self):
        val = self._running_winnings()
        if self._player_choice == self._coin_toss:
            self._player_score += val
            self._house_score -= val
        else:
            self._house_score += val
            self._player_score -= val
        sign = '-' if self._player_score < 0 else ''
        print('Your bank: {}${}'.format(sign, abs(self._player_score)))

    def _ending_prompt(self):
        print("\n")
        if self._house_score < self._player_score:
            print("<== You win ${} ==>".format(self._player_score))
        elif self._house_score > self._player_score:
            print("\n<== You lose ${} ==>".format(abs(self._player_score)))
        else:
            print("Game is Tied")
        print("Thanks for playing")
        
        
class _ThirdGame(_SecondGame):
    def __init__(self):
        self._round = 0
        super().__init__()
        
    def _get_instructions(self):        
        return _FirstGame._get_instructions(self) + "For each round, you can potential winnings on the table is doubled."
        
    def _running_winnings(self):
        return 2**self._round
        
    def _play_round(self):
        super().play_round()
        self._round +=1



def MatchingPennies():
    _FirstGame().play_game()
    
def MPwithInstantForgiveness():
    _SecondGame().play_game()
    
def MPwithExponentialWinnings():
    _ThirdGame().play_game()
