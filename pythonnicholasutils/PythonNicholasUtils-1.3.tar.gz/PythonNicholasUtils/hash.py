from werkzeug.security import generate_password_hash, check_password_hash

def hash(data):
  #Hash a string using SHA256
  return generate_password_hash(data)

def check_hash(hashed_string, unhashed_string):
  #Checks if a password is correct 
  return check_password_hash(hashed_string, unhashed_string)

def encode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string

def decode(key, string):
    encoded_chars = []
    for i in range(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr((ord(string[i]) - ord(key_c) + 256) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = ''.join(encoded_chars)
    return encoded_string
