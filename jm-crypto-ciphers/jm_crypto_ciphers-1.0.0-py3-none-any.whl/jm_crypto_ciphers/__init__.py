__version__ = '1.0.0'

class myCiphers:

  def caesarEnc(self, pt, key):
    ct = ""
    for letter in pt:
      o = ord(letter)
      if letter.isupper():
        idx = ord(letter) - ord("A")
        pos = (idx + key) % 26 + ord("A")
        ct += chr(pos)
      elif letter.islower():
        idx = o - ord("a")
        pos = (idx + key) % 26 + ord("a")
        ct += chr(pos)
      elif letter.isdigit():
        ct += letter
      else:
        print("Unsupported character detected.")
    return ct

  def caesarDec(self, ct, key):
    pt = ""
    for letter in ct:
      o = ord(letter)
      if letter.isupper():
        idx = ord(letter) - ord("A")
        pos = (idx - key) % 26 + ord("A")
        pt += chr(pos)
      elif letter.islower():
        idx = o - ord("a")
        pos = (idx - key) % 26 + ord("a")
        pt += chr(pos)
      elif letter.isdigit():
        pt += letter
      else:
        print("Unsupported character detected.")
    return pt

  def vigenereEnc(self, pt, key, maintainCase):
    import math
    if len(pt) > len(key):
      key = key * math.ceil((len(pt) / len(key)))
      key = key[0:len(pt)]
    if maintainCase:
      caseFlags = []
      for char in pt:
        caseFlags.append(char.isupper())
    pt = pt.lower()
    key = key.lower()
    j = 0
    ct = ""
    for char in pt:
      if not ord('a') <= ord(char) <= ord('z'):
        ct += char # digits and punctuation
      else:
        first = ord(char) - ord('a')
        second = ord(key[j]) - ord('a')
        ct += chr((first + second) % 26 + ord('a'))
        j += 1
    if maintainCase:
      tmp = list(ct)
      for i in range(0, len(tmp)):
        if caseFlags[i] == True:
          tmp[i] = tmp[i].upper()
      ct = ''.join(char for char in tmp)
    return ct

  def vigenereDec(self, ct, key, maintainCase):
    import math
    if len(ct) > len(key):
      key = key * math.ceil((len(ct) / len(key)))
      key = key[0:len(ct)]
    if maintainCase:
      caseFlags = []
      for char in ct:
        caseFlags.append(char.isupper())
    ct = ct.lower()
    key = key.lower()
    j = 0
    pt = ""
    for char in ct:
      if not ord('a') <= ord(char) <= ord('z'):
        pt += char # digits and punctuation
      else:
        first = ord(char) - ord('a')
        second = ord(key[j]) - ord('a')
        pt += chr((first - second) % 26 + ord('a'))
        j += 1
    if maintainCase:
      tmp = list(pt)
      for i in range(0, len(tmp)):
        if caseFlags[i] == True:
          tmp[i] = tmp[i].upper()
      pt = ''.join(char for char in tmp)
    return pt

  def cbcEnc(self, key, iv, pt, blkLen=16, padStyle='pkcs7'):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    if type(pt) == str:
      pt = pt.encode()
    if type(iv) == str:
      iv = iv.encode()
    pt = pad(pt, blkLen, style=padStyle)
    pt = bytearray(pt)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ct = cipher.encrypt(pt)
    return ct, cipher.iv

  def cbcDec(self, key, iv, ct, blkLen=16, padStyle='pkcs7'):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    if type(ct) == str:
      ct = ct.encode()
    if type(iv) == str:
      iv = iv.encode()
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = cipher.decrypt(ct)
    pt = unpad(pt, blkLen, style=padStyle)
    return pt

  def ctrEnc(self, pt, key, iv, nonce=b'', blkLen=16, padStyle='pkcs7'):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad
    if type(pt) == str:
      pt = pt.encode()
    if type(iv) == str:
      iv = iv.encode()
    if type(nonce) == str:
      nonce = nonce.encode()
    pt = pad(pt, blkLen, style=padStyle)
    pt = bytearray(pt)
    cipher = AES.new(key, AES.MODE_CTR, initial_value=iv, nonce=nonce)
    ct = cipher.encrypt(pt)
    return ct

  def ctrDec(self, ct, key, iv, nonce=b'', blkLen=16, padStyle='pkcs7'):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
    if type(ct) == str:
      ct = ct.encode()
    if type(iv) == str:
      iv = iv.encode()
    if type(nonce) == str:
      nonce = nonce.encode()
    cipher = AES.new(key, AES.MODE_CTR, initial_value=iv, nonce=nonce)
    pt = cipher.decrypt(ct)
    pt = unpad(pt, blkLen, style=padStyle)
    return pt

  def cfbEnc(self, pt, key, iv, segSizeBits=8):
    from Crypto.Cipher import AES
    if type(pt) == str:
      pt = pt.encode()
    if type(iv) == str:
      iv = iv.encode()
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=segSizeBits)
    ct = cipher.encrypt(pt)
    return ct
  
  def cfbDec(self, ct, key, iv, segSizeBits=8):
    from Crypto.Cipher import AES
    if type(ct) == str:
      ct = ct.encode()
    if type(iv) == str:
      iv = iv.encode()
    cipher = AES.new(key, AES.MODE_CFB, iv=iv, segment_size=segSizeBits)
    pt = cipher.decrypt(ct)
    return pt

  def ofbEnc(self, pt, key, iv):
    from Crypto.Cipher import AES
    if type(pt) == str:
      pt = pt.encode()
    if type(iv) == str:
      iv = iv.encode()
    cipher = AES.new(key, AES.MODE_OFB, iv=iv)
    ct = cipher.encrypt(pt)
    return ct
    
  def ofbDec(self, ct, key, iv):
    from Crypto.Cipher import AES
    if type(ct) == str:
      ct = ct.encode()
    if type(iv) == str:
      iv = iv.encode()
    cipher = AES.new(key, AES.MODE_OFB, iv=iv)
    pt = cipher.decrypt(ct)
    return pt

  def gcmEnc(self, pt, key, nonce, header=b'', macLenBytes=16):
    from Crypto.Cipher import AES
    if type(pt) == str:
      pt = pt.encode()
    if type(nonce) == str:
      nonce = nonce.encode()
    if type(header) == str:
      header = header.encode()
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=macLenBytes)
    cipher.update(header)
    ct, tag = cipher.encrypt_and_digest(pt)
    return ct, tag

  def gcmDec(self, ct, tag, key, nonce, header=b'', macLenBytes=16):
    from Crypto.Cipher import AES
    if type(ct) == str:
      ct = ct.encode()
    if type(nonce) == str:
      nonce = nonce.encode()
    if type(header) == str:
      header = header.encode()
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=macLenBytes)
    cipher.update(header)
    pt = cipher.decrypt_and_verify(ct, tag)
    return pt