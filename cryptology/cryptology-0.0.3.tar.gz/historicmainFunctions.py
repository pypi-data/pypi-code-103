# -*- coding: utf-8 -*-
"""
Created on Sun Oct  4 15:42:46 2020

@author: 44752
"""

# add in about spaces for them all

def atbash_decrypt(cipher_text):
    
    """ 
    This is a function which decrypts atbash 
    The function takes an argument of the cipher text and 
    returns the plain text
    """
    
    # ensures that the cipher_text is a string
    if type(cipher_text) != str:
        raise TypeError("cipher_text must be type string")
    
    # list which defines the alphabet
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","J","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z"]
    
    # empty list which will be used to store the plain text
    decrypt = []                              
    
    # for loops through all letter of cipher and decrypts 
    # checks that it is a capital A-Z
    # gets the position in the alphabet A-Z - 0-25
    # gets corresponding letter using atbash
    for i in range(len(cipher_text)):   
        
        letter = cipher_text[i]
        
        # checks that each element is a capital letter
        if letter not in alphabet and letter != " ":
            raise TypeError("letter must be capital between A-Z", letter)
        
        # if isn't a space decrypt
        if letter != " ":
            alpha_position = alphabet.index(letter) 
            new_position = (-alpha_position  % 25) + 1        
            new_letter = alphabet[new_position - 1]   
            decrypt.append(new_letter)            
        else:
            decrypt.append(" ")
            
    # plain text to be outputted
    plain_text = "".join(decrypt)
    
    return(plain_text)
    
def atbash_encrypt(plain_text):
    
    """ 
    This is a function which encrypts atbash 
    The function takes an argument of the plain text and 
    returns the cipher text
    """
    
    # ensures that the cipher_text is a string
    if type(plain_text) != str:
        raise TypeError("plain_text must be type string")
    
    # list which defines the alphabet
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","J","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z"]
    
    # empty list which will be used to store the plain text
    decrypt = []                              
    
    # for loops through all letter of cipher and decrypts 
    # checks that it is a capital A-Z
    # gets the position in the alphabet A-Z - 0-25
    # gets corresponding letter using atbash
    for i in range(len(plain_text)):   
        
        letter = plain_text[i]
        
        # checks that each element is a capital letter
        if letter not in alphabet and letter != " ":
            raise TypeError("letter must be capital between A-Z", letter)
        
        # if isn't a space decrypt
        if letter != " ":
            alpha_position = alphabet.index(letter) 
            new_position = (-alpha_position  % 25) + 1        
            new_letter = alphabet[new_position - 1]   
            decrypt.append(new_letter)            
        else:
            decrypt.append(" ")
            
    # plain text to be outputted
    cipher_text = "".join(decrypt)
    
    return(cipher_text)


def ceaser_decrpyt(cipher_text, shift):
    
    """
    This is a function which decrypts a Ceaser cipher
    Takes arguments of the cipher text and the shift wanting to be applied
    """
    
    # ensures cipher_text is a string type
    if type(cipher_text) != str:
        raise TypeError("cipher_text must be type string")
    
    # ensures shift is an integer
    if type(shift) != int:
        raise TypeError("shift must be type int")
        
    # list which defines the alphabet
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","J","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z"]
    
    # empty list which will be used to store the plain text
    decrypt = []                                   
    
    # for loops through all letter of cipher and decrypts 
    # checks that it is a capital A-Z
    # gets the position in the alphabet A-Z - 0-25
    # gets corresponding letter using atbash
    for i in range(len(cipher_text)): 
           
        letter = cipher_text[i]
        
         # checks that each element is a capital letter
        if letter not in alphabet and letter != " ":
            raise TypeError("letter must be capital between A-Z", letter)
        
        # if it isn't a space decryprt
        if letter != " ":
            alpha_position = alphabet.index(letter)       
            
            # shifting the letters with ceaser
            if alpha_position - shift >  0 :                    
                new_letter = alphabet[alpha_position - shift]
                decrypt.append(new_letter)        
            else: 
                new_letter = alphabet[alpha_position % 25- shift]      
                decrypt.append(new_letter)  
        else:
            decrypt.append(" ")
        
        # add to plain text
        plain_text = "".join(decrypt)
    
    return(plain_text)

def ceaser_encrpyt(plain_text, shift):
    
    """
    This is a function which encrypts a Ceaser cipher
    Takes arguments of the plain and the shift wanting to be applied
    """
    
    # ensures cipher_text is a string type
    if type(plain_text) != str:
        raise TypeError("plain_text must be type string")
    
    # ensures shift is an integer
    if type(shift) != int:
        raise TypeError("shift must be type int")
        
    shift = 26 - shift
        
    # list which defines the alphabet
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","J","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z"]
    
    # empty list which will be used to store the plain text
    decrypt = []                                   
    
    # for loops through all letter of cipher and decrypts 
    # checks that it is a capital A-Z
    # gets the position in the alphabet A-Z - 0-25
    # gets corresponding letter using atbash
    for i in range(len(plain_text)): 
           
        letter = plain_text[i]
        
         # checks that each element is a capital letter
        if letter not in alphabet and letter != " ":
            raise TypeError("letter must be capital between A-Z", letter)
        
        # if it isn't a space decryprt
        if letter != " ":
            alpha_position = alphabet.index(letter)       
            
            # shifting the letters with ceaser
            if alpha_position - shift >  0 :                    
                new_letter = alphabet[alpha_position - shift]
                decrypt.append(new_letter)        
            else: 
                new_letter = alphabet[alpha_position % 25- shift]      
                decrypt.append(new_letter)  
        else:
            decrypt.append(" ")
        
        # add to cipher text
        cipher_text = "".join(decrypt)
    
    return(cipher_text)


def scytale_decrypt(cipher_text, band):
    
    """
    This is a function which decrypts a scytale cipher
    Takes arguments of the cipher_text and band
    Band is how many letters in the row of your scytale
    """
      # ensures cipher_text is a string type
    if type(cipher_text) != str:
        raise TypeError("cipher_text must be type string")
    
    # ensures band is an integer 
    if type(band) != int:
        raise TypeError("band must be type int")
    
    # list of letters and dictionary
    list_of_text =  list(cipher_text.strip())
    d = {}
    start = 0

    
   # adding _'s into the list that are extra that will go at the end of plain text
    if len(list_of_text) % band != 0:
        val_0 = int(len(list_of_text)/band) + 1
        which_col = (len(list_of_text) % band)
       
        for num in range(which_col+1, band+1):
            insert = num * val_0-1
            list_of_text.insert(insert, '_')
            
    val = int(len(list_of_text)/band)
    
    # codes the list into a dictionary 
    for x in range(0, val):
        if len(list_of_text[start::val]) == band:  
            d["row{0}".format(x)] = list_of_text[start::val]
            start = start + 1
        else:
            break
    
    # transforming dictionary to readable letters
    dic_list = list(d.values())
    joint_list = [j for i in dic_list for j in i]
    joint_list [:] = (value for value in joint_list  if value != "_")
    plain_text = "".join(joint_list)
        
    return(plain_text)


def scytale_encrypt(plain_text, band):
   
    """
    This is a function which encryps a scytale cipher
    Takes arguments of the plain_text and band
    Band is how many letters in the row of your scytale
    """
    
     # ensures plain_text is a string type
    if type(plain_text) != str:
        raise TypeError("plain_text must be type string")
    
    # ensures band is an integer 
    if type(band) != int:
        raise TypeError("band must be type int")
        
        
    # list of letters and dictionary
    list_of_text =  list(plain_text.strip())
    d = {}
    val = int(len(list_of_text)/band)
    
    
    # adding "_" to the end
    if len(list_of_text) % band != 0:
        remainder = band - len(list_of_text) % band
        list_of_ = ["_"] * remainder
        list_of_text = list_of_text + list_of_

    
    # to iterate through in different chunks
    start = 0
    end = band 
    
    # asigning each row to the dictionary
    for x in range(0, val+1):
        d["row{0}".format(x)] = list_of_text[start:end]
        start = start + band 
        end = end + band 
    
    # converts dict to list and creates new cipher_text list
    dic_list = list(d.values())
    cipher_text = []
    
    # append values from dict to create cipher text
    for j in range(band):
        for i in range(val+1):
            cipher_text.append(dic_list[i][j])
            
    # get rid of "_" and convert list to string
    cipher_text[:] = (value for value in cipher_text if value != "_")
    cipher_text = "".join(cipher_text)
    
    return(cipher_text)


# next is vigenre decrypt

def vigenre_decrpyt(cipher_text, keyword):
    
    """
    This is a function which decrypts a vigenere cipher
    Takes arguments of the cipher_text and keyword
    """
    
    # ensures cipher_text is a string type
    if type(cipher_text) != str:
        raise TypeError("cipher_text must be type string")
    
    # ensures keyword is an integer 
    if type(keyword) != str:
        raise TypeError("keyword must be type string")
        
    # list which defines the alphabet
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","J","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z"]
    
    def order_alpha(letter):
    
        """
        This is a function which takes a letter in the alphabet
        Then creates a list starting with this letter, wrapping round the 
        alphabet
        """
        pos = alphabet.index(letter)
    
        new_alpha =  alphabet[pos:26] + alphabet[0:pos] 
    
        return(new_alpha)
    
    # this defines my col and rows for the vigenere decoder    
    col_dict = {}
    row_dict = {}
    plain_text = []
    for x in alphabet: 
        col_dict["col{0}".format(x)] = order_alpha(x)
        row_dict["row{0}".format(x)] = order_alpha(x)
      
    # makes cipher text and keyword into a list
    list_of_text =  list(cipher_text.strip())
    list_of_keyword =  list(keyword.strip())
    keyword_iterator = 0
    cipher_text_iterator = 0
    
    # so going through each letter, looking at the corresponding keyword
    # then by analysing the vigenere square, outputting the correct letter
    for cipher_text_iterator in range(len(list_of_text)):
        
        if keyword_iterator == len(list_of_keyword):
            keyword_iterator = 0
            
            # error checking to check it is one of the alphabet
            if list_of_keyword[keyword_iterator] not in alphabet:
                raise TypeError("keyword must be a capital letter")
            else:
                row = row_dict["row"+list_of_keyword[keyword_iterator]]
                keyword_iterator = keyword_iterator + 1
        else:
            if list_of_keyword[keyword_iterator] not in alphabet:
                raise TypeError("keyword must be a capital letter")
            else:
                row = row_dict["row"+list_of_keyword[keyword_iterator]]
                keyword_iterator = keyword_iterator + 1
        
        if list_of_text[cipher_text_iterator] not in alphabet:
            raise TypeError("cipher text must be a capital letter")
        else:
            which_col = row.index(list_of_text[cipher_text_iterator])
        col_name = alphabet[which_col]
        plain_text.append(col_name)
    
    # join all the letters together
    plain_text = "".join(plain_text)
    
    return(plain_text)
    
    
def vigenre_encrpyt(plain_text, keyword):
    
    """
    This is a function which encrypts using a vigenere cipher
    Takes arguments of the plain_text and keyword
    """
    
    # ensures cipher_text is a string type
    if type(plain_text) != str:
        raise TypeError("cipher_text must be type string")
    
    # ensures keyword is an integer 
    if type(keyword) != str:
        raise TypeError("keyword must be type string")
        
    # list which defines the alphabet
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","J","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z"]
    
    def order_alpha(letter):
    
        """
        This is a function which takes a letter in the alphabet
        Then creates a list starting with this letter, wrapping round the 
        alphabet
        """
        pos = alphabet.index(letter)
    
        new_alpha =  alphabet[pos:26] + alphabet[0:pos] 
    
        return(new_alpha)
    
    # this defines my col and rows for the vigenere decoder    
    col_dict = {}
    row_dict = {}
    cipher_text = []
    for x in alphabet: 
        col_dict["col{0}".format(x)] = order_alpha(x)
        row_dict["row{0}".format(x)] = order_alpha(x)
      
    # makes plain text and keyword into a list 
    # with iterator integers to iterate through text / keyword
    list_of_text =  list(plain_text.strip())
    list_of_keyword =  list(keyword.strip())
    keyword_iterator = 0
    plain_text_iterator = 0
    
    # so going through each letter, looking at the corresponding keyword
    # then by analysing the vigenere square, outputting the correct letter
    # checks if the keyword needs to be wrapped round again
    for plain_text_iterator in range(len(list_of_text)):
        
        if keyword_iterator == len(list_of_keyword):
            
            keyword_iterator = 0
            
            # error checking to check it is one of the alphabet
            if list_of_keyword[keyword_iterator] not in alphabet:
                raise TypeError("keyword must be a capital letter")
            else:
                col = alphabet.index(keyword[keyword_iterator])
                keyword_iterator = keyword_iterator + 1
        else:
            if list_of_keyword[keyword_iterator] not in alphabet:
                raise TypeError("keyword must be a capital letter")
            else:
                col = alphabet.index(keyword[keyword_iterator])
                keyword_iterator = keyword_iterator + 1
        
        if list_of_text[plain_text_iterator] not in alphabet:
            raise TypeError("plain text must be a capital letter")
        else:
            plain_text_letter = list_of_text[plain_text_iterator]
            row = row_dict["row"+plain_text_letter]
            cipher_text_letter = row[col]
            cipher_text.append(cipher_text_letter )
    
    #join all the letters together
    cipher_text = "".join(cipher_text)
    
    return(cipher_text)


def playfair_encrypt(plain_text, keyword):

    """
    This is a function which encrypts using a playfair cipher
    Takes arguments of the plain_text and keyword
    """
    # ensures cipher_text is a string type
    if type(plain_text) != str:
        raise TypeError("cipher_text must be type string")
    
    # ensures keyword is an integer 
    if type(keyword) != str:
        raise TypeError("keyword must be type string")
        
    # list which defines the alphabet, no J in playfair
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z"]
     
    # list of letters in keyword and plain text
    keyword_list_strip = list(keyword.strip())
    plain_text_list = list(plain_text.strip())
    
    # get rid of duplicates in keyword
    keyword_list = []
    [keyword_list.append(x) for x in keyword_list_strip if x not in keyword_list] 
    
    # setting up the playfair grid
    for letter in keyword:
        if letter in alphabet:
            alphabet.remove(letter)
    
    playfair_grid = keyword_list + alphabet
    
    # adding in X to plaintext when duplicates occur
    plain_text_list_length = len(plain_text_list)
    
    for i in range(plain_text_list_length):
        if i == 0:
            pass
        else:
            if plain_text_list[i] == plain_text_list[i-1]:
                plain_text_list.insert(i, "X")
    
    # add X at the end
    plain_text_list_length = len(plain_text_list)
    
    if plain_text_list_length % 2 !=0:
        plain_text_list.insert(plain_text_list_length, "X")
    
    # define row/cols
    row1 = [0,1,2,3,4]
    row2 = [5,6,7,8,9]
    row3 = [10,11,12,13,14]
    row4 = [15,16,17,18,19]
    row5 = [20,21,22,23,24]
    
    row1_grid = playfair_grid[0:5]
    row2_grid = playfair_grid[5:10]
    row3_grid = playfair_grid[10:15]
    row4_grid = playfair_grid[15:20]
    row5_grid = playfair_grid[20:25]
    
    print(row1_grid,row2_grid,row3_grid,row4_grid)
    
    col1 = [0,1,2,3,4]
    col2 = [5,6,7,8,9]
    col3 = [10,11,12,13,14]
    col4 = [15,16,17,18,19]
    col5 = [20,21,22,23,24]
    
    # split lists into pair
    list_pairs = []
    i = 0
    j = 1
    
    # so for all letters within my cipher text
    for x in range(len(plain_text_list)):                           
        if j < len(plain_text_list):                                
            list_pairs.append(plain_text_list[i] + plain_text_list[j]) 
            i = i + 2                                           
            j = j + 2
    
    # decide if letter in same row/col and which one
    for pair in list_pairs:
        
        first_letter = pair[0]
        second_letter = pair[1]
        
        playfair_pos_1 = playfair_grid.index(first_letter)
        playfair_pos_2 = playfair_grid.index(second_letter)
        
        #print(first_letter, playfair_pos_1,second_letter, playfair_pos_2)
        
        if playfair_pos_1 in row1 and playfair_pos_2 in row1:
            cipher_first_letter = row1_grid[playfair_pos_1 - 1]
            cipher_second_letter = row1_grid[playfair_pos_2 - 1]
      
            print("false")
        
    
    return(cipher_first_letter, cipher_second_letter)

text5 = "MUKOFLRGXLIUIHALCIBICTEIVNMZFDLCFLRLRYTPOMSYLWGFCLPTLWLOMLFRLOLBODOPUQPOPOLELBTPKOEIHUFPNGMOLXKCRLPNNQEQFRYRZUTSLUIVOQOMQLMLLFRYQYILMLZICIIQLFOFOCIFDFNHZLCFIDTHOKTKUNOSHGUGZGTPBLGCWZGMIFTNGKTPTCMNKOXDXLRNKTLBGUEXNTYRPOFRRLCLXBTKIFESHOPTNGILQFIAEHFDXLKTRGEUTGQZILRLPOFELCBREHCDERTGUYILMLZUTPLPIZOHXBPLNQYRIHCIEFSTZURNLOFEUQPOENMULEHNIAXLFQLNAMIFRFKCXLGURZPOFLLEUYOQOMEPLZLAIVILMLALSYNQRGGIGKQNOFRLENMULOBDLXXNGHZLPTVILULBZRFLEFBICODYKZMQILRKCOXBTKIFVILUIVLXGRQLCVCBGURZPOGRHTQYOQLPLUPHTLYIDKXEHARHGRFEPODLBVXLRYQNHONGGMPECTLUHTCIFLELVILUIVKTYRADZEFRRGEDVNNQVIHNGCRVRBCTKOELLBKMXCQLFEMGTLUGEPHUVCFEOMQOOINQOMIFVILNBLDXLTGCEXNTYRPODCRVRBSQCTZTBNNQGKELCLZRFLIQOFGIYITMTPZRLBMLLCFCGHLFTKEHMKUYOWCTBUKTUYILMLVLBLUGMTVRCTFLROZKIQKQRGGQOMPZLXVKHAFLSGLTILPNKOIUKTYRQORCRXUORFGQHLZGPNLCFLRGXLEGTLAPLBNHXDSQCTZTGSLBGKELLBMTVRGCXLGQHGGCUMOHNYPSHOEAOMTCARLXUQPOGZILKAOMOFLOEOHQKOGUNHOFTPTCODOPMLLOQKEZBFTPHWGLESFRHNAQLHHSKQLBGQTZLBRLOFPONGHGTPLOMKZY"
test = "ABBAOAIRHEGOIERNGONREOIHREGOIWHREGIORHGIOHHHSGHAODIHGOIR"
steph = "MEETMEATTREFFORESTSTATION"
len(steph)
z = playfair_encrypt(steph, "GLAMORGAN")
w = playfair_encrypt("NC", "GLAMORGAN")
print("hello")



# need to do the shifting across of cols
# then need to work out what to do with no rows/cols























