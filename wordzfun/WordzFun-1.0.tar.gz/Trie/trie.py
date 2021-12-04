from .graph import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random

# Fetch the service account key JSON file contents
cred = credentials.Certificate(
    './Trie/internship-takehome-firebase-adminsdk-bcor9-338334a160.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://internship-takehome-default-rtdb.firebaseio.com/'
})

class TrieNode:
    # Trie Node

    def __init__(self, char):
        #character of the node
        self.char = char

        # end of word
        self.last = False

        # counter of no. of timees a word is inserted
        self.counter = 0

        # dictionary of trie
        self.children = {}


class Trie(object):
    # Trie Object
    def __init__(self):
        self.root = TrieNode("")
        
        self.word_list = []
        # list of words in firebase
        self.words = []
        ref = db.reference("/")
        for i in ref.get().values():
            self.words.append(i)
        
        self.createTrie()
        
    def createTrie(self):
        # form the trie everytime you run code
        for word in self.words:
            self.insert(word, True)

    def insert(self, word, trieForm=False):
        word = word.lower()
        
        ref = db.reference("/")
        data = ref.get()
        exists = False
        for i in data.values():
            if(i==word):
                if(trieForm == False):
                    print("Word Already Exists!")
                exists = True

        if(exists==False):
            ref.push(word)
            print("Inserted!")
            self.words.append(word)

        node = self.root
        # Loop through each character in the word
        # Check if there is no child containing the character, create a new child for the current node
        for char in word:
            if char in node.children:
                node = node.children[char]
            else:
                # If a character is not found,
                # create a new node in the trie
                new_node = TrieNode(char)
                node.children[char] = new_node
                node = new_node

        # Mark the end of a word
        node.last = True

        # Increment the counter to indicate that we see this word once more
        node.counter += 1

    def search(self, key):
        key = key.lower()
        node = self.root
        found = True
        copy=key
        word=''
        while(len(key)>0):
            word=word+key[0]
            try:
                node=node.children[key[0]]
                key=key[1:]
            except:
                break

        if word==copy:
            return "Found"
        else:
            return "Not found"

    def showAllWords(self):
        self.words = []
        ref = db.reference("/")
        for i in ref.get().values():
            self.words.append(i)
        for j in self.words:
            print(j)

    def suggest(self,current,pred_word):
        if current.last:
            self.word_list.append(pred_word)
        
        for key,values in current.children.items():
            self.suggest(values,pred_word+key)

    def predict(self,word):
        word = word.lower()
        current = self.root
        present = False
        pred_word = ''

        for i in list(word):
            if not current.children.get(i):
                present=True
                break

            pred_word=pred_word+i
            current=current.children[i]
        
        if present:
            print("Not found")
            return 0
        elif current.last and not current.children:
            return -1
        
        self.suggest(current,pred_word)

        for i in self.word_list:
            print(i)

    def display(self):
        file = open('./Trie/input.txt', 'w')
        for i in self.words:
            file.write(i+"\n")
        file.close()
        trie()
        print("Search for `output.pdf` to find the visual representation of the trie.")

    def randomSentence(self):
        sentence = ""
        num = random.randint(2, len(self.words)-1)
        for i in range(num):
            n = random.randint(0, len(self.words)-1)
            sentence = sentence + " " + self.words[n]
        print(sentence)
    
    def randomWord(self):
        for x in range(15):
            words = []
            newWord = ""
            for i in range(2):
                num = random.randint(0, len(self.words)-1)
                words.append(self.words[num])
                for j in words:
                    
                    lengthOfWord = len(j)
                    randomNo = random.randint(0, lengthOfWord-1)

                    for m in range(randomNo):
                        n = random.randint(0, lengthOfWord-1)
                        newWord = newWord + j[n]
            print(newWord)
