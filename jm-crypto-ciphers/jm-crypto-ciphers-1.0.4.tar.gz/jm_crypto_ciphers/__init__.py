__version__ = '1.0.4'

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

  #
  # Start of DES encryption/decryption section
  #

  def initialPerm(self, x):
    permutation = [58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16, 8, 57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7]

    return self.permute(permutation, x)

  def finalPerm(self, x):
    permutation = [40, 8, 48, 16, 56, 24, 64, 32, 39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25]

    return self.permute(permutation, x)

  def fFuncPerm(self, x):
    permutation = [16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31, 10, 2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25]

    return self.permute(permutation, x)

  def pc1Perm(self, key):
    assert len(key) == 64
    permutation = [57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44, 36, 63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4]
    
    return self.permute(permutation, key)

  def pc2Perm(self, key):
    assert len(key) == 56
    permutation = [14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4, 26, 8, 16, 7, 27, 20, 13, 2, 41, 52, 31, 37, 47, 55, 30, 40, 51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32]
    
    return self.permute(permutation, key)

  def expansion(self, x):
    assert len(x) == 32

    permutation = [32, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9, 8, 9, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 16, 17, 18, 19, 20, 21, 20, 21, 22, 23, 24, 25, 24, 25, 26, 27, 28, 29, 28, 29, 30, 31, 32, 1]

    return self.permute(permutation, x)

  def sBox1(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals =  [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
            [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
            [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
            [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def sBox2(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals = [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
            [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
            [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
            [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def sBox3(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals = [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
            [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
            [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
            [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def sBox4(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals = [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
            [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
            [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
            [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def sBox5(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals = [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
            [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
            [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
            [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def sBox6(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals = [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
            [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
            [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
            [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def sBox7(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals = [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
            [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
            [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
            [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def sBox8(self, x):
    assert len(x) == 6

    # Define the s-box values
    vals = [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
            [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
            [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
            [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]

    # Compute the output
    return self.computeSBoxOut(x, vals)

  def computeSBoxOut(self, x, vals):
    row = int(x[0]) * pow(2, 0) + int(x[5]) * pow(2, 1)
    col = int(x[1]) * pow(2, 0) + int(x[2]) * pow(2, 1) + int(x[3]) * pow(2, 2) + int(x[4]) * pow(2, 3)

    return bin(vals[row][col])[2:].zfill(4)

  def fFunc(self, x, rndKey):
    import jm_crypto_utilities
    utils = jm_crypto_utilities.MyCryptoUtils()

    # Compute expansion function
    out = self.expansion(x)  

    # XOR expansion function output with round key
    out = utils.xor(out, rndKey)

    # Compute s-boxes
    out = self.sBox1(out[0:6]) + self.sBox2(out[6:12]) + self.sBox3(out[12:18]) + self.sBox4(out[18:24]) + self.sBox5(out[24:30]) + self.sBox6(out[30:36]) + self.sBox7(out[36:42]) + self.sBox8(out[42:48])

    # Permute and return value
    return self.fFuncPerm(out)

  def permute(self, permutation, x):
    # Initialize array to hold permuted values
    y = [0] * len(permutation)

    # Run the permutation
    for i in range(len(permutation)):
      y[i] = x[permutation[i] - 1]

    return ''.join(str(elem) for elem in y)

  def genRoundKeys(self, numRounds, key):
    if len(key) == 64:
      # PC-1 permutation
      out = self.pc1Perm(key)
    elif len(key) != 56:
      print("Invalid key length " + str(len(key)) + "in genRoundKeys!")
      return

    # Split key into two halves
    keyLeft = out[0:28]
    keyRight = out[28:56]

    # Generate round keys
    rndKeys = [0] * numRounds
    for i in range(numRounds):
      if i == 1 or i == 2 or i == 9 or i == 16: # Rotate left 1 bit
        keyLeft = keyLeft[1:] + keyLeft[0]
        keyRight = keyRight[1:] + keyRight[0]
      else: # Rotate left 2 bits
        keyLeft = keyLeft[2:] + keyLeft[0:2]
        keyRight = keyRight[2:] + keyRight[0:2]

      # PC-2 permutation
      rndKeys[i] = self.pc2Perm(keyLeft + keyRight)

    return rndKeys

  def getBlocks(self, msg):
    import math

    # Determine the number of blocks
    nBlocks = math.ceil(len(msg) / 64)

    # Split into blocks
    blocks = []
    for i in range(nBlocks):
      if i == (nBlocks - 1): # last block
        blocks.append(msg[i*64:].zfill(64))
      else:
        blocks.append(msg[i*64:i*64+64].zfill(64))
    
    return blocks, nBlocks

  def des_encdec(self, msg, keys, nRounds, purpose):
    import jm_crypto_utilities
    utils = jm_crypto_utilities.MyCryptoUtils()

    # Reverse the round keys if decryption
    if purpose == 'decrypt':
      roundKeys = keys[::-1]
    else:
      roundKeys = keys
    
    # Initial permutation
    msg = self.initialPerm(msg)
    
    # Split plaintext into two halves
    left = msg[:32]
    right = msg[32:]

    for i in range(nRounds):
      in1 = left
      in2 = self.fFunc(right, roundKeys[i])
      left = right
      right = utils.xor(in1, in2)

    # Swap left and right halves
    out = right + left

    # Final permutation
    out = self.finalPerm(out)

    return out

  #
  # End of DES encryption/decryption section
  #