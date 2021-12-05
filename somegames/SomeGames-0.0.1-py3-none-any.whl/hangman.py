import numpy as np
import re


_text = """It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.

However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.

"My dear Mr. Bennet," said his lady to him one day, "have you heard that Netherfield Park is let at last?"

Mr. Bennet replied that he had not.

"But it is," returned she; "for Mrs. Long has just been here, and she told me all about it."

Mr. Bennet made no answer.

"Do you not want to know who has taken it?" cried his wife impatiently.

"YOU want to tell me, and I have no objection to hearing it."

This was invitation enough.

"Why, my dear, you must know, Mrs. Long says that Netherfield is taken by a young man of large fortune from the north of England; that he came down on Monday in a chaise and four to see the place, and was so much delighted with it, that he agreed with Mr. Morris immediately; that he is to take possession before Michaelmas, and some of his servants are to be in the house by the end of next week."

"What is his name?"

"Bingley."

"Is he married or single?"

"Oh! Single, my dear, to be sure! A single man of large fortune; four or five thousand a year. What a fine thing for our girls!"

"How so? How can it affect them?"

"My dear Mr. Bennet," replied his wife, "how can you be so tiresome! You must know that I am thinking of his marrying one of them."

"Is that his design in settling here?"

"Design! Nonsense, how can you talk so! But it is very likely that he MAY fall in love with one of them, and therefore you must visit him as soon as he comes."

"I see no occasion for that. You and the girls may go, or you may send them by themselves, which perhaps will be still better, for as you are as handsome as any of them, Mr. Bingley may like you the best of the party."

"My dear, you flatter me. I certainly HAVE had my share of beauty, but I do not pretend to be anything extraordinary now. When a woman has five grown-up daughters, she ought to give over thinking of her own beauty."

"In such cases, a woman has not often much beauty to think of."

"But, my dear, you must indeed go and see Mr. Bingley when he comes into the neighbourhood."

"It is more than I engage for, I assure you."

"But consider your daughters. Only think what an establishment it would be for one of them. Sir William and Lady Lucas are determined to go, merely on that account, for in general, you know, they visit no newcomers. Indeed you must go, for it will be impossible for US to visit him if you do not."

"You are over-scrupulous, surely. I dare say Mr. Bingley will be very glad to see you; and I will send a few lines by you to assure him of my hearty consent to his marrying whichever he chooses of the girls; though I must throw in a good word for my little Lizzy."

"I desire you will do no such thing. Lizzy is not a bit better than the others; and I am sure she is not half so handsome as Jane, nor half so good-humoured as Lydia. But you are always giving HER the preference."

"They have none of them much to recommend them," replied he; "they are all silly and ignorant like other girls; but Lizzy has something more of quickness than her sisters."

"Mr. Bennet, how CAN you abuse your own children in such a way? You take delight in vexing me. You have no compassion for my poor nerves."

"You mistake me, my dear. I have a high respect for your nerves. They are my old friends. I have heard you mention them with consideration these last twenty years at least."

Mr. Bennet was so odd a mixture of quick parts, sarcastic humour, reserve, and caprice, that the experience of three-and-twenty years had been insufficient to make his wife understand his character. HER mind was less difficult to develop. She was a woman of mean understanding, little information, and uncertain temper. When she was discontented, she fancied herself nervous. The business of her life was to get her daughters married; its solace was visiting and news."""

_pattern = re.compile('\W+')
_word_list = list(set([word.lower() for word in _pattern.sub(' ', _text).split() if (len(word)>5) and (not word.istitle())]))


_hangman_progress = [''' 
  ________
   |     \|
          |
          |
          |
          |
  =========
   ''', '''
  ________
   |     \|
   O      |
          |
          |
  =========
  ''', '''
  ________
   |     \|
   O      |
   |      |
          |
          |
  =========
   ''', '''
  ________
   |     \|
   O      |
  /|      |
          |
          |
  =========
  ''', '''
  ________
   |     \|
   O      |
  /|\     |
          |
          |
  =========
  ''', '''
  ________
   |     \|
   O      |
  /|\     |
  /       |
          |
  =========
  ''' , '''
  ________
   |     \|
   O      |
  /|\     |
  / \     |
          |
  =========
 ''']




class _Hangman:
    def __init__(self):
        self._guessing_word = np.random.choice(_word_list)
        self._letter_positions = self._get_letter_positions()
        self._hangmans_situation = 0
        self._game_progress = ["_"] * len(self._guessing_word)
        self._hanged = len(_hangman_progress)
        print("You must guess the letters of the following word by making at most 6 incorrect guesses.")
        print("""Hint: This word appears in Chapter 1 of Jane Austen's "Pride and Prejudice".""")
        
    def play_game(self):
        self._show_progress()
        while True:
            self._play_round()
            if self._game_over():
                break
        self._ending_prompt()
                    
    def _play_round(self):
        letter = self._get_letter()
        while letter in self._game_progress:
            letter = self._get_letter()
        if letter in self._letter_positions:
            self._update_progress(letter) 
        else:
            self._update_hangman()
        self._show_progress()        
    
    def _update_hangman(self):
        print(_hangman_progress[self._hangmans_situation])
        self._hangmans_situation += 1        
    
    def _update_progress(self, letter):
        for position in self._letter_positions[letter]:
            self._game_progress[position] = letter
            
    def _game_over(self):
        return not ((self._hangmans_situation < self._hanged) and ("_" in self._game_progress))
    
    def _ending_prompt(self):
        if "_" not in self._game_progress:
            print("\nCongratulations! You got the word!\n")
        else:
            print("\nThe word was:\n" + " ".join(self._guessing_word))
            print("Better luck next time.\n")
        
    def _show_progress(self):
        print(" ".join(self._game_progress))
        
    def _get_letter(self):
        ans = input("Enter a letter: ").lower()
        while ans not in "abcdefghijklmnopqrstuvwxyz":
            ans = input("Enter a letter: ").lower()
        return ans
        
    def _get_letter_positions(self):
        letter_positions = {}
        for position, letter in enumerate(self._guessing_word):
            letter_positions.setdefault(letter, []).append(position)
        return letter_positions





def HangmanGame():
    """
    A function that implements the Hangman game (https://en.wikipedia.org/wiki/Hangman_(game)).
    The aim is to guess the letters of a word by making at most 6 incorrect guesses, i.e. before 
    "the prisoner is hanged". Each word has at least 6 letters and all words come from Chapter 1 
    of Jane Austen's "Pride and Prejudice".
    
    To play:
       from hangman import HangmanGame
       HangmanGame()
       
    """
    _Hangman().play_game()




