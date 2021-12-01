# -*- coding:utf-8  -*-

WORD = {
    'a' : [
        'a',
        'ability',
        'able',
        'about',
        'above',
        'abroad',
        'absolutely',
        'accept',
        'acceptable',
        'accident',
        'according to',
        'account',
        'accuse',
        'achieve',
        'acid',
        'across',
        'act',
        'action',
        'active',
        'activity',
        'actor',
        'actress',
        'actual',
        'actually',
        'ad',
        'add',
        'address',
        'admire',
        'admit',
        'adult',
        'advantage',
        'adventure',
        'advertisement',
        'advice',
        'advise',
        'affect',
        'afford',
        'afraid',
        'after',
        'afternoon',
        'afterwards',
        'again',
        'against',
        'age',
        'aged',
        'ago',
        'agree',
        'agreement',
        'ahead',
        'aim',
        'air',
        'aircraft',
        'airport',
        'alcohol',
        'alcoholic',
        'alive',
        'all',
        'allow',
        'all right',
        'almost',
        'alone',
        'along',
        'alphabet',
        'already',
        'also',
        'although',
        'always',
        'among',
        'amount',
        'amuse',
        'amusing',
        'an',
        'ancient',
        'anger',
        'angle',
        'angry',
        'animal',
        'announce',
        'annoy',
        'annoyed',
        'annoying',
        'another',
        'answer',
        'any',
        'anybody',
        'anyone',
        'anything',
        'anyway',
        'apart',
        'apartment',
        'appear',
        'appearance',
        'apple',
        'application',
        'apply',
        'appropriate',
        'approval',
        'approve',
        'April',
        'area',
        'argue',
        'argument',
        'arm',
        'army',
        'around',
        'arrange',
        'arrangement',
        'arrest',
        'arrive',
        'arrow',
        'art',
        'article',
        'artificial',
        'artist',
        'artistic',
        'as',
        'ashamed',
        'ask',
        'asleep',
        'at',
        'atmosphere',
        'attack',
        'attention',
        'attract',
        'attractive',
        'August',
        'aunt',
        'autumn',
        'available',
        'avoid',
        'awake',
        'aware',
        'away',
        'awesome',
        'awful',
        'axe'
        ],
    'b' : [
        'baby',
        'back',
        'backwards',
        'bad',
        'badly',
        'badminton',
        'bad-tempered',
        'bag',
        'bake',
        'balance',
        'ball',
        'balloon',
        'band',
        'bank',
        'bar',
        'base',
        'baseball',
        'basic',
        'basis',
        'basket',
        'basketball',
        'bat',
        'bath',
        'bathroom',
        'be',
        'beach',
        'bear',
        'beard',
        'beat',
        'beautiful',
        'beauty',
        'become',
        'bed',
        'bedroom',
        'bee',
        'beef',
        'been',
        'beer',
        'before',
        'begin',
        'beginning',
        'behave',
        'behaviour',
        'behind',
        'belief',
        'believe',
        'bell',
        'belong',
        'below',
        'belt',
        'bend',
        'beneath',
        'benefit',
        'best',
        'bet',
        'better',
        'between',
        'beyond',
        'bicycle',
        'big',
        'bill',
        'billion',
        'bin',
        'bind',
        'biology',
        'bird',
        'birth',
        'birthday',
        'biscuit',
        'bit',
        'bite',
        'bitter',
        'black',
        'blame',
        'block',
        'blood',
        'blow',
        'blue',
        'board',
        'boat',
        'body',
        'boil',
        'bold',
        'bomb',
        'bone',
        'book',
        'boot',
        'border',
        'bored',
        'boring',
        'born',
        'both',
        'bottle',
        'bottom',
        'bow',
        'bowl',
        'box',
        'boy',
        'bra',
        'brain',
        'branch',
        'brave',
        'bread',
        'break',
        'breakfast',
        'breast',
        'breath',
        'breathe',
        'brick',
        'brief',
        'bright',
        'bring',
        'broken',
        'brother',
        'brown',
        'brush',
        'bubble',
        'build',
        'building',
        'bullet',
        'burn'
        ]
    }

def get():
    return WORD

import sys
if sys.version_info[0] == 2:
    import tkFileDialog as tk
elif sys.version_info[0] == 3 and sys.version_info[1] < 4:
    import filedialog as tk
elif sys.version_info[0] == 3 and sys.version_info[1] >= 4:
    import tkinter.filedialog as tk
else:
    raise SystemExit('This Python version is not supported by the current version of Python-Extension.')
import pickle
#try:
#    import pyextension.word_bank.word_bank_value as WORDBANK
#except:
#    import word_bank_value as WORDBANK

def install(location, obj):
    file = open(location, 'wb')
    pickle.dump(obj, file)
    file.close()

import os

def uninstall(location):
    os.remove(location)

try:
    open('word bank.dat', 'rb')
except OSError:
    install('word bank.dat', WORD)

class Word():
    def __init__(self, location=None):
        if location == None:
            location = 'word bank.dat'
        self.location = location
        file = open(location, 'rb')
        self.dic = pickle.load(file)
        file.close()
    def search(self, key):
        try:
            return self.dic[key]
        except KeyError:
            result = []
            for x in self.dic[key[0]]:
                if key in x:
                    result.append(x)
            return result
    def get(self):
        return self.dic
    def insert(self, key, item=[], save=False):
        for x in item:
            self.dic[key] = self.dic[key].append(x)
        if save == True:
            file = open(self.location, 'wb')
            pickle.dump(self.dic, file)
            file.close()
        return self.dic
    def change(self, key, item, save=False):
        if type(item) == type([]):
            self.dic[key] = item
        else:
            raise TypeError('Argument \'item\' must be list type')
        if save == True:
            file = open(self.location, 'wb')
            pickle.dump(self.dic, file)
            file.close()
        return self.dic
    def delete(self, key, item, save=False):
        if type(item) == type(1):
            del self.dic[key][item]
        elif type(item) == type(''):
            times = 0
            try:
                while True:
                    if self.dic[key][times] == item:
                        del self.dic[key][times]
                        break
                    times += 1
            except IndexError:
                raise ValueError('No item \'%s\' in word bank.dat[%s]' % (item, key))
            return dic
        elif type(item) == type([]):
            for x in item:
                if type(x) == type(0):
                    del self.dic[key][x]
                elif type(x) == type(''):
                    times = 0
                    try:
                        while True:
                            if self.dic[key][times] == x:
                                del self.dic[key][times]
                                break
                            times += 1
                    except IndexError:
                        raise ValueError('No item \'%s\' in word bank.dat[%s]' % (x, key))
        else:
            raise TypeError('type \'item\' must be string or int')
        # Delete
        if save == True:
            file = open(self.location, 'wb')
            pickle.dump(self.dic, file)
            file.close()
        return self.dic
    def save(self):
        file = open(self.location, 'wb')
        pickle.dump(self.dic, file)
        file.close()
    def saveas(self, location=None):
        if location[-4] + location[-3] + location[-2] + location[-1] != '.dat':
            location = location + '.dat'
            return 'Warning : Your location is not a dat file, we turned it to a dat file, please check the file if it not the shape you want.'
        try:
            file = open(location, 'wb')
            pickle.dump(self.dic, file)
            file.close()
        except OSError:
            pass
