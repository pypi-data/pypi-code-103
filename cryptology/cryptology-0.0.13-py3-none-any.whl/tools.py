alphabet_dictionary={"A":0,"B":1,"C":2,"D":3,"E":4,"F":5,"G":6,"H":7,"I":8,
                     "J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15, "Q":16,
                     "R":17,"S":18,"T":19,"U":20 ,"V":21,"W":22,"X":23,"Y":24,
                     "Z":25,"a":0,"b":1,"c":2,"d":3,"e":4,"f":5,"g":6,"h":7,
                     "i":8,"j":9,"k":10,"l":11,"m":12,"n":13,"o":14,"p":15,
                     "q":16,"r":17,"s":18,"t":19,"u":20 ,"v":21,"w":22,"x":23,
                     "y":24,"z":25," ":" "}

alphabet={"A":0,"B":1,"C":2,"D":3,"E":4,"F":5,"G":6,"H":7,"I":8,
           "J":9,"K":10,"L":11,"M":12,"N":13,"O":14,"P":15, "Q":16,
           "R":17,"S":18,"T":19,"U":20 ,"V":21,"W":22,"X":23,"Y":24,
           "Z":25, " ":" "}

alphabet_list=["A","B","C","D","E","F","G","H","I",
           "J","K","L","M","N","O","P", "Q",
           "R","S","T","U" ,"V","W","X","Y",
           "Z"]

alphabet_list_playfair=["A","B","C","D","E","F","G","H","I",
           "K","L","M","N","O","P", "Q",
           "R","S","T","U" ,"V","W","X","Y",
           "Z"]

def type_str_error(letters:str):
    """[Raises type error if letters isn't a string]
    Args:
        letters (str): [letter being passed in]

    Raises:
        TypeError: [if letters isn't a string, raise error]
    """
    if type(letters) != str:
        raise TypeError(f"{letters} must be type string")

        
def type_int_error(shift:int):
    """[Raises type error if letters isn't a string]
    Args:
        letters (str): [letter being passed in]

    Raises:
        TypeError: [if letters isn't a string, raise error]
    """
    if type(shift) != int:
        raise TypeError(f"{shift} must be an int")


def type_alphabet_error(letters:str):
    """
    """
    alphabet = ["A","B","C","D","E","F","G","H",
                "I","J","K","L","M","N","O","P",
                "Q","R","S","T","U" ,"V","W","X",
                "Y","Z","a","b","c","d","e","f",
                "g","h","i","j","k","l","m","n",
                "o","p","q","r","s","t","u" ,"v",
                "w","x","y","z"]
    for letter in letters:
        if letter not in alphabet and letter != " ":
                raise TypeError("""Letter in CipherText must be 
                                letter between A-Z""", letter)
                            
def type_duplicate_letter_error(letters:str):
    
    if letters != "":
        if len(letters) != len(set(letters)):
            
            raise TypeError("Duplicates in permutation")
                                
    
def get_pos_alphabet(letters:str)->list:
    """gets the numerical position of letters in the alphabet,
        e.g a=0,b=1,...,z=25
    Args:
        letters (str): letters passed through

    Returns:
        list: numerical equivelent of letter
    """
    alpha_positions=[alphabet_dictionary[letter] for letter in letters]

    return alpha_positions 

def get_atbashed_pos_alphabet(numbers):
    """gets the atbashed position equivelent of letter

    Args:
        numbers ([int]): positions of the letters from the cipher text

    Returns:
        new_position: the decrypted atbash position
    """
    new_position = [(25-alpha_position) %26 for alpha_position in numbers if alpha_position!=" "] 
    
    return new_position

def get_atbashed_pos_alphabet_encrypt(numbers):
    """gets the atbashed position equivelent of letter

    Args:
        numbers ([int]): positions of the letters from the cipher text

    Returns:
        new_position: the decrypted atbash position
    """
    new_position = [-(alpha_position  +1) %26  for alpha_position in numbers if alpha_position!=" "] 
    
    return new_position

def get_key(val):
    """gets the letter from a specificed postion. e,g.
       1=a,2=b,...,z=25

    Args:
        val ([int]): alphabet position number

    Returns:
        [type]: corresponding alphabet number
    """
    for key, value in alphabet.items():
        
        if value == val:
            return key
    return "key doesn't exist"

def get_alphabet_from_pos(letter_pos):
    """applies get_key to all letters to get the alphabet from
       it's position number
    Args:
        letter_pos ([int]): alphabet position number
    Returns:
        all alphabet leters from it's poisiton number,
        this shoud be the final plain text
    """
    alpha=[get_key(letter) for letter in letter_pos]
    
    return alpha

def get_ceaser_pos(letters_pos,shift):
    """ges the ceaser decrypted position of letter

    Args:
        letters_pos ([list of ints]): list of ints which are 
        letter positions
        shift ([int]): [the value for your ceaser cipher shifted]

    Returns:
        [list]: [the ceaser decypted value with the shift applied to it]
    """

    shifted=[(letter-shift) % 26 for letter in letters_pos if letter != " "]

    return shifted

def get_ceaser_pos_decrypt(letters_pos,shift):
    """ges the ceaser encrypted position of letter

    Args:
        letters_pos ([list of ints]): list of ints which are 
        letter positions
        shift ([int]): [the value for your ceaser cipher shifted]

    Returns:
        [list]: [the ceaser encrypted value with the shift applied to it]
    """


    shifted=[(letter+shift) % 26 for letter in letters_pos if letter != " "]

    return shifted

def order_alpha(letter:str)->list:
    """
    will create a list with the letter passed through first,
    then will go through all rest of the alphabet and loops back
    E.g order_alpha("D") = ["D","E","F",...,"Z","A","B","C"]

    Parameters
    ----------
    letter : str
        DESCRIPTION.

    Returns
    -------
    list
        DESCRIPTIONs

    """
    pos = alphabet_list.index(letter)

    new_alpha =  alphabet_list[pos:26] + alphabet_list[0:pos] 

    return(new_alpha)

def vigenere_permutation(permutation):
    """creates the vigenre square top row with a permutation

    Args:
        permutation str: the permutation used to create
        the vigenre square. Can't be a duplicate

    Returns:
        list: the vigenre square top row in the form of a list
    """
    
    permutation=[char for char in permutation]
    not_in_perma=[letter for letter in alphabet_list if letter not in permutation]
    order_alpha_perm=permutation+not_in_perma
    
    return order_alpha_perm
    

def create_viginere_table(permutation):
    """Creates viginere table based on if there is a permutation ornot

    Args:
        permutation str: the permutation used to create
        the vigenre square. Can't be a duplicate. If permutation=""
        then normal A,B,C square. 

    Returns:
        table dictionary: All rows of the viginere list
    """
    
    table={}
    
    if permutation == "":
        table={letter:order_alpha(letter) for letter in alphabet_list}
    else:
        top_row=vigenere_permutation(permutation)
        for letter in alphabet_list:
            table[letter]=top_row
            top_row=top_row[1:] + top_row[:1]
        
    
    return table

def keyword_text_match_up(text, keyword):
    """repeats keyword so that it matches the text e.g
    keyword=fam, text="ABCDEFG" it will output
    keyword_repeat=["F","A","M,"F","A","M","F] &
    text_list=["A","B","C,"D","E","F","G]
    Args:
        text str: the cipher or plain text to do encryption/decryption on
        keyword str: The keyword used for encryption/decryption
    Returns:
        keyword_repeat,text_list [lists]: The text with it's keyword
        repeated so it matches the text
    """
    text_list=[char for char in text]
    text_length=len(text_list)
    
    keyword_list=[char for char in keyword]
    keyword_length=len(keyword)
    
    number_repeats=int(text_length/keyword_length)
    leftover=text_length%keyword_length
    
    keyword_repeat=keyword_list*number_repeats+keyword_list[0:leftover]
    
    return keyword_repeat,text_list
    
def viginere_get_table_decrypt(table,keyword_letter,text_letter):
    """outputs the decrypted letter based on the dictionary table,
       keyword letter and cipher text letter wanting to decrypt    

    Args:
        table ([dictionary]): dictionary of the table 
        keyword_letter ([str]): [letter from keyword]
        text_letter ([str]): [letter wanting to decnrypt]

    Returns:
        [str]: [decrypted letter]
    """
    
    row=table[keyword_letter]
    where_in_row=row.index(text_letter)
    out_letter=alphabet_list[where_in_row]
    
    return out_letter


def viginere_get_table_encrypt(table,keyword_letter,text_letter):
    """outputs the encrypted letter based on the dictionary table,
       keyword letter and plain text letter wanting to encrypt    

    Args:
        table ([dictionary]): dictionary of the table 
        keyword_letter ([str]): [letter from keyword]
        text_letter ([str]): [letter wanting to ecnrypt]

    Returns:
        [str]: [encrypted letter]
    """

    row=table[keyword_letter]
    col=alphabet_list.index(text_letter)
    out_letter=row[col]

    return out_letter

def playfair_grid_list(keyword):
    """produces the playfair grid list based on the keyword
    Args:
        keyword ([str]): [keyword used to produce playfair table]
    Returns:
        [list]: [the playfair grid as a lit]
    """
    keyword_list_strip = list(keyword.strip())
    key_word_no_dups = list(dict.fromkeys(keyword_list_strip))
    other_letter=[letter for letter in alphabet_list_playfair if letter not in key_word_no_dups]
    playfair_grid = key_word_no_dups + other_letter
    
    return playfair_grid
    
def playfair_deal_with_dups(text):
    """playfair can't deal with conseuctive letters being duplicated,
    this adds in an X between conseuctive duplciated letters

    Args:
        text ([str]): plain text to get rid of dups

    Returns:
        [message]: list of text with the X's added where there are conseuctive duplicates
    """
    message = list(text.strip())
    for i in range(1,len(message)):
       
        if message[i] == message[i-1]:
                message.insert(i, "X")

    return message

def get_play_fair_row_col(playfair_grid,letter):
    """[get which row, col a letter is within a playfair grid]

    Args:
        playfair_grid ([list]): [playfair grid]
        letter ([str]): [letter you wan the row/column for]

    Returns:
        [row, col]: [the row and column for the letter passed in
        using the playfair grid passed in]
    """
    
    pos_in_grid=playfair_grid.index(letter)
    row,col=divmod(pos_in_grid,5)
    
    return row, col

def playfair_put_into_pairs(text):
    """takes a list of strings and puts them in to pairs,
        adds extra X on the end incase where len text is odd 

    Args:
        text ([list]): [lsit of strings e.g ["A","B","C","D"]
        

    Returns:
        [list]: [that will go to ["AB","CD]]
    """
    if len(text) % 2 !=0:
        text.append("X")
    
    split = [first + second for first,second in zip(text[::2], text[1::2])]

    return split

def playfair_decrypt_row_pair(grid, pair):
    """if two letters are in the same row,
    this is the method to decrypt 

    Args:
        grid ([list]): [list of the playfair grid]
        pair ([str]): [pair of strings in form e.g "AB"]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns decrypted letters as a tuple]
    """

    pos_in_list_1=grid.index(pair[0])
    pos_in_list_2=grid.index(pair[1])

    if pos_in_list_1 % 5 !=0:
        first_decrpyted_letter=grid[(pos_in_list_1-1)]
    else:
        first_decrpyted_letter=grid[(pos_in_list_1+4)]
    if pos_in_list_2 % 5 !=0:
        second_decrpyted_letter=grid[(pos_in_list_2-1)]
    else:
        second_decrpyted_letter=grid[(pos_in_list_2+4)]

    return first_decrpyted_letter,second_decrpyted_letter

def playfair_decrypt_col_pair(grid, pair):
    """if two letters are in the same col,
    this is the method to decrypt 

    Args:
        grid ([list]): [list of the playfair grid]
        pair ([str]): [pair of strings in form e.g "AB"]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns decrypted letters as a tuple]
    """

    pos_in_list_1=grid.index(pair[0])
    pos_in_list_2=grid.index(pair[1])

    if pos_in_list_1 >4:
        first_decrpyted_letter=grid[(pos_in_list_1-5)]
    else:
        first_decrpyted_letter=grid[(pos_in_list_1+20)]
    if pos_in_list_2 >4:
        second_decrpyted_letter=grid[(pos_in_list_2-5)]
    else:
        second_decrpyted_letter=grid[(pos_in_list_2+20)]

    return first_decrpyted_letter,second_decrpyted_letter


def playfair_decrypt_rectangle(grid, x_1,y_1,x_2,y_2):
    """if two letters are in not in the same col/row,
    this is the method to decrypt 

    Args:
        grid ([list]): [playfair grid]
        x_1 ([): [first letter, row]]
        y_1 ([first letter col]): [first letter, col]]
        x_2 ([second ]): [second letter, row]]
        y_2 ([type]): [second letter, col]]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns decrypted letters as a tuple]
    """

    first_decrpyted_letter=grid[(x_1*5+y_2)]
    second_decrpyted_letter=grid[(x_2*5+y_1)]

    return first_decrpyted_letter,second_decrpyted_letter


def playfair_decrypt_pair(playfair_list, pair):
    """Takes the playfair grid and a pair, calculates which method
    of decryption it should use (row, col, rectangle, then proceeds
    to do this decryption)

    Args:
        playfair_list ([list]): [playfair grid]
        pair ([str]): [pair you want to decrypt i.e "AB"]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns decrypted letters as a tuple]
    """
    (l1_row,l1_col)=get_play_fair_row_col(playfair_grid=playfair_list,
                                                    letter=pair[0])

    (l2_row,l2_col)=get_play_fair_row_col(playfair_grid=playfair_list,
                                                    letter=pair[1])
    if l1_row==l2_row:
        (first_decrpyted_letter, 
        second_decrpyted_letter)=playfair_decrypt_row_pair(grid=playfair_list, pair=pair)
    elif l1_col==l2_col:
        (first_decrpyted_letter, 
        second_decrpyted_letter)=playfair_decrypt_col_pair(grid=playfair_list, pair=pair)
    else:
        (first_decrpyted_letter, 
        second_decrpyted_letter)=playfair_decrypt_rectangle(grid=playfair_list, 
                                                            x_1=l1_row,
                                                            y_1=l1_col,
                                                            x_2=l2_row,
                                                            y_2=l2_col)

    return first_decrpyted_letter, second_decrpyted_letter

def playfair_encrypt_row_pair(grid, pair):
    """if two letters are in the same row,
    this is the method to decrypt 

    Args:
        grid ([list]): [list of the playfair grid]
        pair ([str]): [pair of strings in form e.g "AB"]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns encrypted letters as a tuple]
    """

    pos_in_list_1=grid.index(pair[0])
    pos_in_list_2=grid.index(pair[1])

    end_of_row=[4,9,14,19,24]

    if (pos_in_list_1 not in end_of_row) | (pos_in_list_1==0):
        first_encrypted_letter=grid[(pos_in_list_1+1)]
    else:
        first_encrypted_letter=grid[(pos_in_list_1-4)]
    if (pos_in_list_2 not in end_of_row) | (pos_in_list_2==0):
        second_encrypted_letter=grid[(pos_in_list_2+1)]
    else:
        second_encrypted_letter=grid[(pos_in_list_2-4)]

    return first_encrypted_letter,second_encrypted_letter

def playfair_encrypt_col_pair(grid, pair):
    """if two letters are in the same col,
    this is the method to decrypt 

    Args:
        grid ([list]): [list of the playfair grid]
        pair ([str]): [pair of strings in form e.g "AB"]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns encrypted letters as a tuple]
    """

    pos_in_list_1=grid.index(pair[0])
    pos_in_list_2=grid.index(pair[1])

    if pos_in_list_1 >19:
        first_encrypted_letter=grid[(pos_in_list_1-20)]
    else:
        first_encrypted_letter=grid[(pos_in_list_1+5)]
    if pos_in_list_2 >19:
        second_encrypted_letter=grid[(pos_in_list_2-20)]
    else:
        second_encrypted_letter=grid[(pos_in_list_2+5)]

    return first_encrypted_letter,second_encrypted_letter


def playfair_encrypt_rectangle(grid, x_1,y_1,x_2,y_2):
    """if two letters are in not in the same col/row,
    this is the method to decrypt 

    Args:
        grid ([list]): [playfair grid]
        x_1 ([): [first letter, row]]
        y_1 ([first letter col]): [first letter, col]]
        x_2 ([second ]): [second letter, row]]
        y_2 ([type]): [second letter, col]]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns encrypted letters as a tuple]
    """

    first_encrypted_letter=grid[(x_1*5+y_2)]
    second_encrypted_letter=grid[(x_2*5+y_1)]

    return first_encrypted_letter,second_encrypted_letter


def playfair_encrypt_pair(playfair_list, pair):
    """Takes the playfair grid and a pair, calculates which method
    of encryption it should use (row, col, rectangle, then proceeds
    to do this decryption)

    Args:
        playfair_list ([list]): [playfair grid]
        pair ([str]): [pair you want to encrypt i.e "AB"]

    Returns:
        [first_decrpyted_letter,
        second_decrpyted_letter]: [Returns encrypted letters as a tuple]
    """
    (l1_row,l1_col)=get_play_fair_row_col(playfair_grid=playfair_list,
                                                    letter=pair[0])

    (l2_row,l2_col)=get_play_fair_row_col(playfair_grid=playfair_list,
                                                    letter=pair[1])
    if l1_row==l2_row:
        (first_encrypted_letter, 
        second_encrypted_letter)=playfair_encrypt_row_pair(grid=playfair_list, pair=pair)
    elif l1_col==l2_col:
        (first_encrypted_letter, 
        second_encrypted_letter)=playfair_encrypt_col_pair(grid=playfair_list, pair=pair)
    else:
        (first_encrypted_letter, 
        second_encrypted_letter)=playfair_encrypt_rectangle(grid=playfair_list, 
                                                            x_1=l1_row,
                                                            y_1=l1_col,
                                                            x_2=l2_row,
                                                            y_2=l2_col)

    return first_encrypted_letter, second_encrypted_letter


def unpack_list_of_tuples(list_tuples):
    """takes the list of tuples e.g
    [("A","B),("C","D)] and unpacks them into a normal list
    like ["A","B","C","D]

    Args:
        list_tuples ([list]): [description]

    Returns:
        [text]: [list] the untupled list
    """

    text=[]
    for i in range(len(list_tuples)):
        first,second=list_tuples[i]
        text.append(first)
        text.append(second)

    return text