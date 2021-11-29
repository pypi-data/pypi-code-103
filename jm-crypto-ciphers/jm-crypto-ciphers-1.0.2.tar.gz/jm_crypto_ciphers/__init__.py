__version__ = '1.0.2'

class MyCiphers:

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

  def power(self, a, b, c):
    x = 1
    y = a
    while b > 0:
      if b % 2 != 0:
        x = (x * y) % c;
      y = (y * y) % c
      b = int(b / 2)
    return x % c

  def gamalKeyGen(self, q):
    import jm_crypto_utilities
    import random
    utils = jm_crypto_utilities.MyCryptoUtils()
    # Generate the cyclic group
    G = utils.cyclicGroupGen(q, 'add')
    # Find the generators of the cyclic group
    generators = utils.findGenerators(G, 'add')
    # Randomly select one of the generators
    g = random.choice(generators)
    # Randomly select an element of G
    x = random.choice(G)
    while self.gcd(x, q) != 1:
      x = random.choice(G)
    # Calculate h
    h = pow(g, x, q)
    # Generate the public key
    pubKey = [G, q, g, h]
    # Generate the private key
    privKey = [G, q, g, x]
    return pubKey, privKey

  def gamalEnc(self, pubKey, msg):
    import random
    # Extract components of the public key
    G = pubKey[0]
    q = pubKey[1]
    g = pubKey[2]
    h = pubKey[3]
    # Initialize a list to hold the encrypted characters
    c2 = []
    for i in range(0, len(msg)):
      c2.append(msg[i])
    # Randomly select an element of G
    y = random.choice(G)
    while self.gcd(y, q) != 1:
      y = random.choice(G)
    # Generate c1
    c1 = self.power(g, y, q)
    # Generate c2
    s = self.power(h, y, q)
    for i in range(0, len(c2)):
      c2[i] = s * ord(c2[i])
    return [c1, c2]

  def gamalDec(self, privKey, ct):
    # Extract components
    q = privKey[1]
    x = privKey[3]
    c1 = ct[0]
    c2 = ct[1]
    # Initialize a list for holding decrypted characters
    decrypted = []
    # Calculate h
    h = self.power(c1, x, q)
    # Decrypt the message
    for i in range(0, len(c2)):
      decrypted.append(chr(int(c2[i]/h)))
    return decrypted

  def gamalDigSigKeyGen(self, q):
    import jm_crypto_utilities
    import random
    utils = jm_crypto_utilities.MyCryptoUtils() 
    # Generate the cyclic group
    G = utils.cyclicGroupGen(q, 'mult')
    # Find the generators of the cyclic group
    generators = utils.findGenerators(G, 'mult')
    # Randomly select one of the generators
    g = random.choice(generators)
    # Randomly select an element of G
    x = random.choice(G)
    while self.gcd(x, q) != 1:
      x = random.choice(G)
    # Calculate h
    h = pow(g, x, q)
    # Generate the public key
    pubKey = [G, q, g, h]
    # Generate the private key
    privKey = [G, q, g, x]
    return pubKey, privKey

  def gamalSignMsg(self, privKey, msg):
    import random
    # Extract components of the public key
    G = privKey[0]
    q = privKey[1]
    g = privKey[2]
    x = privKey[3]
    # Randomly select an element of G, ensuring it is relatively prime to order q-1    
    k = random.choice(G)
    while self.gcd(k, q-1) != 1:
      k = random.choice(G)
    # Calculate 'r'
    r = pow(g, k, q)
    # Calculate 's'
    s = []
    for i in range(0, len(msg)):
      s.append(((ord(msg[i]) - x * r) * self.modInverse(k, q-1)) % (q - 1))
    return [r, s]

  def gamalVerSig(self, signature, pubKey, msg):
    # Extract signature components
    r = signature[0]
    s = signature[1]
    q = pubKey[1]
    g = pubKey[2]
    h = pubKey[3] # 'y' in some videos
    # Initialize lists
    gM = []
    test = []
    # Verify the signature
    for i in range(0, len(msg)):
      gM.append(pow(g, ord(msg[i]), q))
      val1 = pow(h, r)
      val2 = pow(r, s[i])
      test.append((val1 * val2) % q)
    return gM == test