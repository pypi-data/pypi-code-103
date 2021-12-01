from cryptology.tools import (type_str_error, 
                   type_alphabet_error,
                   type_int_error,
                   type_duplicate_letter_error,
                   get_pos_alphabet,
                   get_atbashed_pos_alphabet,
                   get_alphabet_from_pos,
                   get_atbashed_pos_alphabet_encrypt,
                   get_ceaser_pos,
                   get_ceaser_pos_decrypt,
                   keyword_text_match_up,
                   create_viginere_table,
                   viginere_get_table_decrypt,
                   viginere_get_table_encrypt,
                   playfair_grid_list,
                   playfair_deal_with_dups,
                   playfair_put_into_pairs,
                   playfair_decrypt_pair,
                   playfair_encrypt_pair,
                   unpack_list_of_tuples)

def atbash_decrypt(cipher_text):
    """Decrypts cipher text into plain text
       using the atbash ciper

    Args:
        cipher_text ([string]): [string of cipher texts to decrypt]

    Returns:
        [plain_text_joined]: [the decryped cipher text i.e plain text]
    """
    # error catching
    type_str_error(cipher_text)
    type_alphabet_error(cipher_text)
    
    # transformation letters to atbashed equivalent
    letter_pos=get_pos_alphabet(cipher_text)
    atbashed_pos=get_atbashed_pos_alphabet(letter_pos)
    plain_text=get_alphabet_from_pos(atbashed_pos)
    
    # joins plain text into a string
    plain_text_joined = "".join(plain_text)
    
    
    return plain_text_joined

def atbash_encrypt(plain_text):
    """Encrypts plain text into cipher text
       using the atbash ciper

    Args:
        plain_text ([string]): [string of plain text to encryptt]

    Returns:
        [cipher_text_joined]: [the decryped cipher text i.e plain text]
    """
    # error catching
    type_str_error(plain_text)
    type_alphabet_error(plain_text)
    
    # transformation letters to atbashed equivalent
    letter_pos=get_pos_alphabet(plain_text)
    atbashed_pos=get_atbashed_pos_alphabet_encrypt(letter_pos)
    cipher_text=get_alphabet_from_pos(atbashed_pos)
    
    # joins plain text into a string
    cipher_text_joined = "".join(cipher_text)
    
    
    return cipher_text_joined


def ceaser_decrypt(cipher_text, shift):
    """Decrypts cipher text into plain text
       using the ceaser ciper

    Args:
        cipher_text ([string]): [string of cipher texts to decrypt]
        shift ([int]): [The shift key applied to ceaser]

    Returns:
        [plain_text_joined]: [the decrypted cipher text i.e plain text]
    """
    # error catching
    type_str_error(cipher_text)
    type_alphabet_error(cipher_text)
    type_int_error(shift)

    letter_pos=get_pos_alphabet(cipher_text)
    ceaser_pos=get_ceaser_pos(letters_pos=letter_pos,
                              shift=shift)

    plain_text=get_alphabet_from_pos(ceaser_pos)
    
    # joins plain text into a string
    plain_text_joined = "".join(plain_text)
    
    
    return plain_text_joined


def ceaser_encrypt(plain_text, shift):
    """ENcrypts plain text into cipher text
       using the ceaser ciper

    Args:
        plain_text ([string]): [string of plain text to encryptt]
        shift ([int]): [The shift key applied to ceaser]

    Returns:
        [cipher_text_joined]: [the decryped cipher text i.e plain text]
    """

    # error catching
    type_str_error(plain_text)
    type_alphabet_error(plain_text)
    type_int_error(shift)

    letter_pos=get_pos_alphabet(plain_text)
    ceaser_pos=get_ceaser_pos_decrypt(letters_pos=letter_pos,
                                      shift=shift)

    cipher_text=get_alphabet_from_pos(ceaser_pos)
    
    # joins plain text into a string
    cipher_text_joined = "".join(cipher_text)
    
    
    return cipher_text_joined

def vigenere_decrypt(cipher_text, keyword, permutation=""):
    """Decrypts cipher text into plain text
       using the viginere ciper

    Args:
        cipher_text ([string]): [string of cipher texts to decrypt]
        keyword ([str]): [The keyword used to decrypt the cipher]
        permutation([str]) [The permutation of the vigenre table,
        defaults to standard "ABC"]
    Returns:
        [plain_text_joined]: [the decrypted cipher text i.e plain text]
    """
    # error catching
    type_str_error(cipher_text)
    type_alphabet_error(cipher_text)
    type_str_error(keyword)
    type_alphabet_error(keyword)
    type_str_error(permutation)
    type_duplicate_letter_error(permutation)
    
    # capitalise 
    keyword=keyword.upper()
    cipher_text=cipher_text.upper()
    permutation=permutation.upper()

    # remove white spaces
    keyword=keyword.replace(" ", "")
    cipher_text=cipher_text.replace(" ", "")
    permutation=permutation.replace(" ","")


    # create table
    table=create_viginere_table(permutation)


    # list of keyword next to cipher text
    key,cipher=keyword_text_match_up(text=cipher_text, 
                                     keyword=keyword) 
    
    # decrypt using table, keyword list & cipher
    plain_text=[viginere_get_table_decrypt(table,k,text) for [k,text] in zip(key,cipher)]    
    # joins plain text into a string
    plain_text_joined = "".join(plain_text)
    
    
    return plain_text_joined

def vigenere_encrypt(plain_text, keyword, permutation=""):
    """ENcrypts plain text into cipher text
       using the viginere ciper

    Args:
        plain_text ([string]): [string of plain text to encryptt]
        keyword ([str]): [The keyword used to encrypt the cipher]
        permutation([str]) [The permutation of the vigenre table,
        defaults to standard "ABC"]

    Returns:
        [cipher_text_joined]: [the decryped cipher text i.e plain text]
    """
    # error catching
    type_str_error(plain_text)
    type_alphabet_error(plain_text)
    type_str_error(keyword)
    type_alphabet_error(keyword)
    type_str_error(permutation)
    type_duplicate_letter_error(permutation)

    # capitalise 
    keyword=keyword.upper()
    plain_text=plain_text.upper()
    permutation=permutation.upper()

    # remove white spaces
    keyword=keyword.replace(" ", "")
    plain_text=plain_text.replace(" ", "")
    permutation=permutation.replace(" ","")

      # create table
    table=create_viginere_table(permutation)
    
    # list of keyword next to plain text
    key,text=keyword_text_match_up(text=plain_text, 
                                     keyword=keyword) 
    
    # decrypt using table, keyword list & cipher
    cipher_text=[viginere_get_table_encrypt(table,k,text) for [k,text] in zip(key,text) ]    
    # joins plain text into a string
    cipher_text_joined = "".join(cipher_text)
    
    
    return cipher_text_joined
    
def playfair_decrypt(cipher_text,keyword):
    """Decrypts cipher text into plain text
       using the playfair ciper

    Args:
        cipher_text ([string]): [string of cipher texts to decrypt]
        keyword ([str]): [The keyword used to decrypt the cipher]
    Returns:
        [plain_text_joined]: [the decrypted cipher text i.e plain text]
    """
    # catching errros
    type_str_error(cipher_text)
    type_alphabet_error(cipher_text)
    type_str_error(keyword)
    type_alphabet_error(keyword)

        # capitalise 
    keyword=keyword.upper()
    cipher_text=cipher_text.upper()

    # remove white spaces
    keyword=keyword.replace(" ", "")
    cipher_text=cipher_text.replace(" ", "")
    cipher_text=cipher_text.replace("J", "I")


    grid_list=playfair_grid_list(keyword)
    plain_text_adjusted_dups=playfair_deal_with_dups(cipher_text)

    paired_list=playfair_put_into_pairs(plain_text_adjusted_dups)
    descrypted_tuples=[playfair_decrypt_pair(playfair_list=grid_list,pair=pairs) for pairs in paired_list]

    plain_text=unpack_list_of_tuples(list_tuples=descrypted_tuples)
    plain_text_joined = "".join(plain_text)
    plain_text_no_x = plain_text_joined.replace("X","")

    return plain_text_no_x

def playfair_encrypt(plain_text,keyword):
    """ENcrypts plain text into cipher text
       using the playfair ciper

    Args:
        plain_text ([string]): [string of plain text to encryptt]
        keyword ([str]): [The keyword used to encrypt the cipher]

    Returns:
        [chiper_text_no_x]: [the decrytped cipher text i.e plain text]
    """
    # catching errors
    type_str_error(plain_text)
    type_alphabet_error(plain_text)
    type_str_error(keyword)
    type_alphabet_error(keyword)

    # capitalise 
    keyword=keyword.upper()
    plain_text=plain_text.upper()

    # remove white spaces
    keyword=keyword.replace(" ", "")
    plain_text=plain_text.replace(" ", "")
    plain_text=plain_text.replace("J", "I")

    grid_list=playfair_grid_list(keyword)
    plain_text_adjusted_dups=playfair_deal_with_dups(plain_text)

    paired_list=playfair_put_into_pairs(plain_text_adjusted_dups)
    descrypted_tuples=[playfair_encrypt_pair(playfair_list=grid_list,pair=pairs) for pairs in paired_list]

    chiper_text=unpack_list_of_tuples(list_tuples=descrypted_tuples)
    chiper_text_joined = "".join(chiper_text)
    chiper_text_no_x = chiper_text_joined.replace("X","")

    return chiper_text_no_x

# folder structure
# .innit. files
# read me
# license 
# CI/CD files
