# -*- coding: utf-8  -*-

dic = ''

def set_dictionary(dic_type='normal', extra_arg=None):
    global dic
    if dic_type == 'normal':
        dic = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890`~!@#$%^&*()-=_+|;:\'\",./?<>[]{} \n'
    elif dic_type == 'code':
        import __init__
        import unicode
        __init__.clear()
        for x in unicode.listcode(extra_arg):
            dic += x
    elif dic_type == 'else':
        dic = extra_arg
    else:
        raise KeyError('%s type not found' % dic_type)

def get_dictionary():
    return dic

set_dictionary()

class Encrypt():
    def __init__(self, original, undo=True):
        self.original = original
        self.ciphertext = original
        self.isundo = undo
        if self.isundo == True:
            self.done = [self.original]
    def get(self):
        return self.ciphertext
    def undo(self):
        if self.isundo == True:
            try:
                self.ciphertext = self.done[-2]
                del self.done[-2]
                if self.isundo == True:
                    self.done.append(self.ciphertext)
            except IndexError:
                pass
    def reset(self):
        self.ciphertext = self.original
        if self.isundo == True:
            self.done.append(self.ciphertext)
    def set(self, value):
        self.ciphertext = value
        if self.isundo == True:
            self.done.append(self.ciphertext)
    def reverse(self):
        self.ciphertext = self.ciphertext[::-1]
        if self.isundo == True:
            self.done.append(self.ciphertext)
    def caesar_cipher(self, key, dic=dic):
        result = ''
        for x in self.ciphertext:
            index = dic.find(x)
            if index == -1:
                result += x
            else:
                index += key
                index %= len(dic)
                result += dic[index]
        self.ciphertext = result
        if self.isundo == True:
            self.done.append(self.ciphertext)
    def caesar(self, key, dic=dic) -> 'Caesar Cipher':
        self.caesar_cipher(key, dic)
    def vigenere_cipher(self, key, dic=dic):
        result = ''
        keys = []
        for x in key:
            if dic.find(x) != -1:
                keys.append(dic.find(x))
            else:
                raise KeyError('Key \'%s\' not found' % x)
        key_index = 0
        for x in self.ciphertext:
            index = dic.find(x)
            if index == -1:
                result += x
            else:
                index += keys[key_index]
                index %= len(dic)
                result += dic[index]
            key_index += 1
            key_index %= len(keys)
        self.ciphertext = result
        if self.isundo == True:
            self.done.append(self.ciphertext)
    def vigenere(self, key, dic=dic) -> 'Vigenere Cipher encrypt':
        self.vigenere_cipher(key, dic)
    def method(self, key, dic=dic):
        pass

class Decrypt():
    def __init__(self, ciphertext, undo=True):
        self.ciphertext = ciphertext
        self.original = ciphertext
        self.isundo = undo
        if self.isundo == True:
            self.done = [self.ciphertext]
    def get(self):
        return self.original
    def undo(self):
        if self.isundo == True:
            try:
                self.original = self.done[-2]
                del self.done[-2]
                if self.isundo == True:
                    self.done.append(self.original)
            except IndexError:
                pass
    def reset(self):
        self.original = self.ciphertext
        if self.isundo == True:
            self.done.append(self.original)
    def set(self, value):
        self.original = value
        if self.isundo == True:
            self.done.append(self.original)
    def reverse(self):
        self.original = self.original[::-1]
        if self.isundo == True:
            self.done.append(self.original)
    def caesar_cipher(self, key, dic=dic):
        result = ''
        for x in self.original:
            index = dic.find(x)
            if index == -1:
                result += x
            else:
                index -= key
                index %= len(dic)
                result += dic[index]
        self.original = result
        if self.isundo == True:
            self.done.append(self.original)
    def caesar(self, key, dic=dic) -> 'Caesar Cipher decrypt':
        self.caesar_cipher(key, dic)
    def vigenere_cipher(self, key, dic=dic):
        result = ''
        keys = []
        for x in key:
            if dic.find(x) != -1:
                keys.append(dic.find(x))
            else:
                raise KeyError('Key \'%s\' not found' % x)
        key_index = 0
        for x in self.original:
            index = dic.find(x)
            if index == -1:
                result += x
            else:
                index -= keys[key_index]
                index %= len(dic)
                result += dic[index]
            key_index += 1
            key_index %= len(keys)
        self.original = result
        if self.isundo == True:
            self.done.append(self.original)
    def vigenere(self, key, dic=dic) -> 'Vigenere Cipher decrypt':
        self.vigenere_cipher(key, dic)
