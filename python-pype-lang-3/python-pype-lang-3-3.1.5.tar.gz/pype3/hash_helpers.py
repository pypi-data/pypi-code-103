import hashlib
import binascii

def hash_pair(s1,s2='',hashSize=10):

    m=hashlib.sha224()
    ls=sorted([s1,s2])
    txts=' '.join(ls)
    
    m.update(txts.encode('utf-8'))
    
    digest=m.digest()
    
    return binascii.hexlify(digest).decode('utf-8')[:hashSize]


def hash_string(s,hashSize=10):

    return hash_pair(s,'',hashSize)
