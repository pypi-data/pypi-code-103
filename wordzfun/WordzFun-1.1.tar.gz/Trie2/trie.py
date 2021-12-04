# from .graph import *
from graph import *
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random

# Fetch the service account key JSON file contents
credsGGL = {
  "type": "service_account",
  "project_id": "internship-takehome",
  "private_key_id": "338334a16061d9c5cb9f484a1c23b2fc6550e407",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCo3+9lo2BbxH5w\noGe6zXnc14A2EZoPr9gSbynA5sLBwbbVyE99Bh7CmowvmVV+X3f0QJ5tI7ue81Lv\nvN4Oo/fUCBTg561fyvxQQpzc9eTT56yrCfeiyfX2Ve/zaAlkHIat0NOny4Hg90XP\nKL+xtSLOGb7HvmsApVJ7Xe8UAuCBi/YcD5k/eaeWR1A22crzXN9LCAhVJEazWxHM\nNTKM1r7x+KZpK5olpUCPtKxxkGH7DZ5/TMehHPgB3vBAiMDULnH4lOMHIm2rsYLk\nlC7gX3yF1t7e7FFt1TT6QkIoEBEGfMJ2hXJ56NOaKPHdMVoOG+W4S4MBcGALGDEK\nubldkgXNAgMBAAECggEAILYDwq3DT/M/RKSlgxcjCEaL9K0zKN+4XFXBAjcQuYRC\n3KUo1IBXe/2AswWh/FEUxLCxn1VhFdhvE7YDU1Wqfx0zoh7uQ9RnTEqi5OASe4Nw\nPE85cwRoytb5nC3mR8iIw+lj3ig6168+C/MKMqtx+vccr8cwJddgIzpeQYOPJjh7\nrHMIReM08zbFHzuMq4k8HFzCdIlrlIbjRpEz4USUT9xKeSxaRucdNyvdT3akHP3h\nXMNjsb1KC7LPRwtyyyMXH4o38BcR1XgDxjpT/BS5gx8H4UEobCRiAh+Q1IL1LjdX\n7LSOXik6NZdv8yCKvdiWPcVoKnf2Y73DYSxvywUSVwKBgQDm70sRzISm11byl2/C\n7UOlU+nDhOCbhfaHytgyUxzhp69G8GU0NEG1pVZ38RcnmJlFgCN+TkPKCLNdvosi\nUkj9srAoobCsSP4JWzPM1nlZfoR2LzGLRcwYVzPpzRQ3hnP530kSB63Z4xImP/Ae\n0xxgXCwITdYpU6C+uczcKIFpLwKBgQC7NEFafXbLwr7zo52JrkbPJyq3DJWANEUi\nWhXBNOg5lQKsbUDmHT4SSRjfvylEeaAmz2ml0s2mGoxXIZyfeUHmpKCgk8lCFeau\nlDa5sWUzx52we4S8MC/JofcvaAaIqQ1JsaJBRmMZR2pp6vIAPx2RHAq1mXl3d119\nfU4BYufJwwKBgC4gKZxafzxb0pAN01LZ1SMWiaB1z+8AaOdiiqAynZgsyAOhTHWK\n4n0HkyfNzdQo1KRfHbfCpiOabUkSH/Qw/0c9A5Z6BTHEOolf4A7P39kSPh7k+j5Z\nKJTMBiByx9D3V/7WrF+fjQfyJNPi/XEKtaZBgsH92gLTI041CkgHByIdAoGAJZaV\ndLzyaHFe8/6rOCTlFN0RZ5XAQvC73Oznp1afNkikM8jwGgRPHU7ODscMWzJspL5K\nwT/1iN+VxDz8fMzVHaF6myNxarKJEg6yelCTOHVhRTlX6o1mWv8JadxiS3heMajY\nInEmnsHHLSM+miwSHLvbrqD1UbaG8BaD3iVk0w8CgYBQqiQ6BccFWUz3wr6WL4Ku\nOz9v+OqDSekiRPNbQ2qw46TA1nZzZL+AoCq++ObVFCMsf7K4tfhpd0G1TjYs91Lu\nxqDGkYzLZGjgGwAMRXTOOLAMNvtbue4bYW6wun1n2Q5R1l7yqWFdYNUmEDHOFa0B\nRfHdzB4bAjIb6rXM1McRdQ==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-bcor9@internship-takehome.iam.gserviceaccount.com",
  "client_id": "103637803773669156716",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-bcor9%40internship-takehome.iam.gserviceaccount.com"
}

cred = credentials.Certificate(credsGGL)
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
        file = open('./Trie2/input.txt', 'w')
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
