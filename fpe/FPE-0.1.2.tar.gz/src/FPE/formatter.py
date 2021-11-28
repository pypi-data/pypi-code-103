from FPE import mode_selector
from FPE import format_translator
from FPE import Format
from math import log

        
def encrypt(text,key,tweak,dataFormat,mode):
    if not Format.isFormat(dataFormat):
        raise ValueError(f"{dataFormat} is not a valid format, please use a valid format. All valid formats can be found in the README")
    
    if dataFormat == Format.EMAIL:
        plainNumerals =  format_translator.text_to_numeral_list(text, dataFormat)
        radixes = format_translator.get_radix_by_format(dataFormat)

        if not (radixes[0] > 1 and radixes[0] <2**16):
            raise ValueError(f"{radixes[0]} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(plainNumerals[0]) > 1 and len(plainNumerals[1]) <= (2 * int(log(2**96, radixes[0])))) and mode == 0:
            raise ValueError(f"{plainNumerals[0]} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(plainNumerals[0])}")
        if not (len(plainNumerals[0]) > 1 and len(plainNumerals[1]) <= 2**32) and mode == 1:
            raise ValueError(f"{plainNumerals[0]} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(plainNumerals[0])}")
        if not (radixes[0]**len(plainNumerals[0]) >= 1000000):
            raise ValueError(f"{radixes[0]} and {len(plainNumerals[0])} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radixes[0]**len(plainNumerals[0])}")
        if not (radixes[1] > 1 and radixes[1] <2**16):
            raise ValueError(f"{radixes[1]} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(plainNumerals[1]) > 1 and len(plainNumerals[1]) <= 2 * int(log(2**96, radixes[1]))) and mode == 0:
            raise ValueError(f"{plainNumerals} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(plainNumerals[1])}")
        if not (len(plainNumerals[1]) > 1 and len(plainNumerals[1]) <= 2**32) and mode == 1:
            raise ValueError(f"{plainNumerals} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(plainNumerals[1])}")
        if not (radixes[1]**len(plainNumerals[1]) >= 1000000):
            raise ValueError(f"{radixes[1]} and {len(plainNumerals[1])} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radixes[1]**len(plainNumerals[1])}")
        
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
        if not (radixes[1] > 1 and radixes[1] <2**16):
            raise ValueError(f"{radixes[1]} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(plainNumerals[1]) > 1 and len(plainNumerals[1]) <= 2 * int(log(2**96, radixes[1]))) and mode == 0:
            raise ValueError(f"{plainNumerals[1]} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(plainNumerals[1])}")
        if not (len(plainNumerals[1]) > 1 and len(plainNumerals[1]) <= 2**32) and mode == 1:
            raise ValueError(f"{plainNumerals[1]} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(plainNumerals[1])}")
        if not (radixes[1]**len(plainNumerals[1]) >= 1000000):
            raise ValueError(f"{radix[1]} and {len(plainNumerals[1])} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radixes[1]**len(plainNumerals[1])}")
        
        cipherNumerals = []

        
        cipherNumerals.append(mode_selector.encrypt(plainNumerals[1][:5],key,tweak,radixes[1],mode))
        
        cipherNumerals.append(
                (plainNumerals[0] + 
                int(''.join([str(x) for x in plainNumerals[1][:5]]) + 
                str(int.from_bytes(key,'big'))))%radixes[0])

        return format_translator.numeral_list_to_text(cipherNumerals, dataFormat)

    else:
        plainNumerals = format_translator.text_to_numeral_list(text, dataFormat)
        radix = format_translator.get_radix_by_format(dataFormat)
        if not (radix > 1 and radix <2**16):
            raise ValueError(f"{radix} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(plainNumerals) > 1 and len(plainNumerals) <= 2 * int(log(2**96, radix))) and mode == 0:
            raise ValueError(f"{plainNumerals} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(plainNumerals)}")
        if not (len(plainNumerals) > 1 and len(plainNumerals) <= 2**32) and mode == 1:
            raise ValueError(f"{plainNumerals} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(plainNumerals)}")
        if not (radix**len(plainNumerals) >= 1000000):
            raise ValueError(f"{radix} and {len(plainNumerals)} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radix**len(plainNumerals)}")
        
        
        cipherNumerals = mode_selector.encrypt(plainNumerals,key,tweak,radix,mode)
        
        return format_translator.numeral_list_to_text(cipherNumerals, dataFormat)

def decrypt(text,key,tweak,dataFormat,mode):
    if not Format.isFormat(dataFormat):
        raise ValueError(f"{dataFormat} is not a valid format, please use a valid format. All valid formats can be found in the README")
    if dataFormat == Format.EMAIL:
        cipherNumerals = format_translator.text_to_numeral_list(text, dataFormat)
        radixes = format_translator.get_radix_by_format(dataFormat)

        if not (radixes[0] > 1 and radixes[0] <2**16):
            raise ValueError(f"{radixes[0]} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(cipherNumerals[0]) > 1 and len(cipherNumerals[1]) <= (2 * int(log(2**96, radixes[0])))) and mode == 0:
            raise ValueError(f"{cipherNumerals[0]} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(cipherNumerals[0])}")
        if not (len(cipherNumerals[0]) > 1 and len(cipherNumerals[1]) <= 2**32) and mode == 1:
            raise ValueError(f"{cipherNumerals[0]} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(cipherNumerals[0])}")
        if not (radixes[0]**len(cipherNumerals[0]) >= 1000000):
            raise ValueError(f"{radixes[0]} and {len(cipherNumerals[0])} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radixes[0]**len(cipherNumerals[0])}")
        if not (radixes[1] > 1 and radixes[1] <2**16):
            raise ValueError(f"{radixes[1]} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(cipherNumerals[1]) > 1 and len(cipherNumerals[1]) <= 2 * int(log(2**96, radixes[1]))) and mode == 0:
            raise ValueError(f"{cipherNumerals} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(cipherNumerals[1])}")
        if not (len(cipherNumerals[1]) > 1 and len(cipherNumerals[1]) <= 2**32) and mode == 1:
            raise ValueError(f"{cipherNumerals} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(cipherNumerals[1])}")
        if not (radixes[1]**len(cipherNumerals[1]) >= 1000000):
            raise ValueError(f"{radixes[1]} and {len(cipherNumerals[1])} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radixes[1]**len(cipherNumerals[1])}")
        
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

        if not (radixes[1] > 1 and radixes[1] <2**16):
            raise ValueError(f"{radixes[1]} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(cipherNumerals[1]) > 1 and len(cipherNumerals[1]) <= 2 * int(log(2**96, radixes[1]))) and mode == 0:
            raise ValueError(f"{cipherNumerals[1]} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(cipherNumerals[1])}")
        if not (len(cipherNumerals[1]) > 1 and len(cipherNumerals[1]) <= 2**32) and mode == 1:
            raise ValueError(f"{cipherNumerals[1]} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(cipherNumerals[1])}")
        if not (radixes[1]**len(cipherNumerals[1]) >= 1000000):
            raise ValueError(f"{radix[1]} and {len(cipherNumerals[1])} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radixes[1]**len(cipherNumerals[1])}")

        plainNumerals = []

        plainNumerals.append(mode_selector.decrypt(cipherNumerals[1][:5],key,tweak,radixes[1],mode))

        plainNumerals.append(
                (cipherNumerals[0] - 
                int(''.join([str(x) for x in plainNumerals[0][:5]]) + 
                str(int.from_bytes(key,'big'))))%radixes[0])
        return format_translator.numeral_list_to_text(plainNumerals, dataFormat)

    else:
        radix = format_translator.get_radix_by_format(dataFormat)
        cipherNumerals = format_translator.text_to_numeral_list(text, dataFormat)

        if not (radix > 1 and radix <2**16):
            raise ValueError(f"{radix} is not a valid Radix, The radix must be 2 <= radix => 2^16.")
        if not (len(cipherNumerals) > 1 and len(cipherNumerals) <= 2 * int(log(2**96, radix))) and mode == 0:
            raise ValueError(f"{cipherNumerals} is not a valid message, The length must be between 2 and 2*(log_radix(2^96)). The message length was: {len(cipherNumerals)}")
        if not (len(cipherNumerals) > 1 and len(cipherNumerals) <= 2**32) and mode == 1:
            raise ValueError(f"{cipherNumerals} is not a valid message, The length must be between 2 and 2^32). The message length was: {len(cipherNumerals)}")
        if not (radix**len(cipherNumerals) >= 1000000):
            raise ValueError(f"{radix} and {len(cipherNumerals)} is not a valid combination of Radix and message-length, radix^message-length must be greater or equal to 1.000.000. It was: {radix**len(cipherNumerals)}")

        plainNumerals = mode_selector.decrypt(cipherNumerals,key,tweak,radix,mode)

        return format_translator.numeral_list_to_text(plainNumerals, dataFormat)
