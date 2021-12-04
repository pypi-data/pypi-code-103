from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from .trie import *
from PyDictionary import PyDictionary
import time

from translate import Translator

dictionary=PyDictionary()
t = Trie()

from examples import custom_style_2
from pyfiglet import Figlet

from nltk.corpus import wordnet

def main_prompt():
    questions = [
        {
            'type': 'list',
            'name': 'Choices',
            'message': 'What do you want to do?',
            'choices': ['Insert', 'Search', 'Suggestions', 'Show all words','Display the trie', 'Generate a random sentence', 'Generate random words', 'Exit']
        }
    ]

    answers = prompt(questions, style=custom_style_2)
    return answers


def main():

    f = Figlet(font="banner3-D")
    print(f.renderText("Sabad's Trie"))
    
    time.sleep(5)
    
    answers = main_prompt()

    try:
        while(answers['Choices']!="Exit"):
            if(answers['Choices'] == "Insert"):
                questions = [
                    {
                        'type': 'input',
                        'name': 'word',
                        'message': 'What word would you like to insert?'
                    }
                ]
                answers = prompt(questions)
                t.insert(answers['word'])
            
            elif(answers['Choices'] == "Search"):
                questions = [
                    {
                        'type': 'input',
                        'name': 'word',
                        'message': 'What word would you like to search for?'
                    }
                ]
                answers = prompt(questions)
                found = t.search(answers['word'])
                print(found)
                time.sleep(2)
                
                if(found == "Found"):

                    questions2 = [
                        {
                            'type': 'list',
                            'name': 'choice',
                            'message': 'What  do you want to do now?',
                            'choices': ['Get Definition of Word', 'Get Synonym of Word', 'Get Antonym of Word', 'Translate Word', 'Back']
                        }
                    ]
                    answers2 = prompt(questions2)
                    syns = wordnet.synsets(answers['word'])
                    
                    if(answers2['choice'] == "Get Definition of Word"):
                        try:
                            print(syns[0].definition())
                        except IndexError:
                            print("Definition of Word not found")

                    elif(answers2['choice'] == "Get Synonym of Word"):
                        if(syns != []):
                            for syn in syns:
                                for lm in syn.lemmas():
                                    print(lm.name())
                        else:
                            print("Synonym of Word not found")
                    
                    elif(answers2['choice'] == "Get Antonym of Word"):
                        words = []
                        for syn in syns:
                            for lm in syn.lemmas():
                                if lm.antonyms():
                                    words.append(lm.antonyms()[0].name())
                        
                        if(words != []):
                            for i in words:
                                print(i)
                        else:
                            print("Antonym of word not found")

                    elif(answers2['choice']=="Translate Word"): 
                        questions3 = [
                            {
                                'type': 'input',
                                'name': 'word',
                                'message': 'Enter language code for translation'
                            }
                        ]
                        answers3 = prompt(questions3)
                        translator= Translator(to_lang=answers3['word'])

                        translation = translator.translate(answers['word'])
                        if("INVALID TARGET LANGUAGE" in translation):
                            print("Invalid Translation code")
                        else:    
                            print(translation)
            
            elif(answers['Choices'] == "Suggestions"):
                questions = [
                    {
                        'type': 'input',
                        'name': 'word',
                        'message': 'Please enter the prompt you would like to get suggestions for'
                    }
                ]
                answers = prompt(questions)
                t.predict(answers['word'])

            elif(answers['Choices'] == "Show all words"):
                time.sleep(2)
                t.showAllWords()
            
            elif(answers['Choices'] == "Display the trie"):
                time.sleep(2)
                t.display()

            elif (answers['Choices'] == "Generate a random sentence"):
                time.sleep(2)
                t.randomSentence()

            elif (answers['Choices'] == "Generate random words"):
                time.sleep(2)
                t.randomWord()
            
            time.sleep(2)
            answers=main_prompt()

    except Exception:
        print("An error occurred")
        exit("Thanks for using my trie!")
        
    exit("Thanks for using my trie!")

main()