from FPE import mode_selector
from FPE import format_translator
from FPE import Format
        
def encrypt(text,key,tweak,dataFormat,mode):
    if dataFormat == Format.EMAIL:
        plainNumerals =  format_translator.text_to_numeral_list(text, dataFormat)
        radixes = format_translator.get_radix_by_format(dataFormat)

        cipherNumerals = []

        cipherNumerals.append(mode_selector.encrypt(plainNumerals[0],key,tweak,radixes[0],mode))
        cipherNumerals.append(mode_selector.encrypt(plainNumerals[1],key,tweak,radixes[1],mode))
                        
        cipherNumerals.append(
                (plainNumerals[2] + 
                int(''.join([str(x) for x in plainNumerals[0]]) + 
                ''.join([str(x) for x in plainNumerals[1]]) +
                str(int.from_bytes(key,'big'))))%radixes[2])

        return format_translator.numeral_list_to_text(cipherNumerals, dataFormat)
        
    elif dataFormat == Format.CPR:
        plainNumerals = format_translator.text_to_numeral_list(text, dataFormat)
        radixes = format_translator.get_radix_by_format(dataFormat)

        cipherNumerals = []

        
        cipherNumerals.append(mode_selector.encrypt(plainNumerals[1],key,tweak,radixes[1],mode))
        
        cipherNumerals.append(
                (plainNumerals[0] + 
                int(''.join([str(x) for x in plainNumerals[1]]) + 
                str(int.from_bytes(key,'big'))))%radixes[0])

        return format_translator.numeral_list_to_text(cipherNumerals, dataFormat)

    else:
        plainNumerals = format_translator.text_to_numeral_list(text, dataFormat)
        radix = format_translator.get_radix_by_format(dataFormat)

        
        cipherNumerals = mode_selector.encrypt(plainNumerals,key,tweak,radix,mode)
        
        return format_translator.numeral_list_to_text(cipherNumerals, dataFormat)

def decrypt(text,key,tweak,dataFormat,mode):
    if dataFormat == Format.EMAIL:
        cipherNumerals = format_translator.text_to_numeral_list(text, dataFormat)
        radixes = format_translator.get_radix_by_format(dataFormat)

        plainNumerals = []

        plainNumerals.append(mode_selector.decrypt(cipherNumerals[0],key,tweak,radixes[0],mode))
        plainNumerals.append(mode_selector.decrypt(cipherNumerals[1],key,tweak,radixes[1],mode))
        
        plainNumerals.append(
                (cipherNumerals[2] - 
                int(''.join([str(x) for x in plainNumerals[0]]) + 
                ''.join([str(x) for x in plainNumerals[1]]) +
                str(int.from_bytes(key,'big'))))%radixes[2])

        return format_translator.numeral_list_to_text(plainNumerals, dataFormat)
        
    elif dataFormat == Format.CPR:
        cipherNumerals = format_translator.text_to_numeral_list(text, dataFormat)
        radixes = format_translator.get_radix_by_format(dataFormat)

        plainNumerals = []

        plainNumerals.append(mode_selector.decrypt(cipherNumerals[1],key,tweak,radixes[1],mode))

        plainNumerals.append(
                (cipherNumerals[0] - 
                int(''.join([str(x) for x in plainNumerals[0]]) + 
                str(int.from_bytes(key,'big'))))%radixes[0])
        return format_translator.numeral_list_to_text(plainNumerals, dataFormat)

    else:
        radix = format_translator.get_radix_by_format(dataFormat)
        plainNumerals = format_translator.text_to_numeral_list(text, dataFormat)


        cipherNumerals = mode_selector.decrypt(plainNumerals,key,tweak,radix,mode)

        return format_translator.numeral_list_to_text(cipherNumerals, dataFormat)
