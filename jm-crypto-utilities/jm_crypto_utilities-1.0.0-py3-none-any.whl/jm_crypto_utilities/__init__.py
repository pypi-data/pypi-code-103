__version__ = '1.0.0'

class MyCryptoUtils:

  def validateHex(self, hexIn):
    if type(hexIn) == bytes:
      hexIn = hexIn.decode()
    if len(hexIn) % 2 != 0:
      print("Hex string must contain an even number of characters. Left pad each hex byte with zeros using zfill().")
      return
    return hexIn

  def validateBin(self, binIn):
    if type(binIn) == bytes:
      binIn = binIn.decode()
    if len(binIn) % 8 != 0:
      print("Binary string must contain a multiple of 8 bits. Left pad each hex byte with zeros using zfill().")
      return
    return binIn

  def hex2bin(self, hexStr, bitLen=8):
    binStr = ""
    i = 0
    hexStr = self.validateHex(hexStr)
    while i < len(hexStr):
      hexDigs = hexStr[i:i+2]
      binStr += bin(int(hexDigs, 16))[2:].zfill(bitLen)
      i += 2
    return binStr
  
  def bin2hex(self, binStr, hexDigLen=2):
    hexStr = ""
    i = 0
    binStr = self.validateBin(binStr)
    while i < len(binStr):
      hexStr += hex(int(binStr[i:i+8], 2))[2:].zfill(hexDigLen)
      i += 8
    hexStr = hexStr.upper()
    return hexStr

  def ascii2bin(self, asciiStr, bitLen=8):
    binStr = ""
    if type(asciiStr) == bytes:
      asciiStr = asciiStr.decode()
    for char in asciiStr:
      binStr += bin(ord(char))[2:].zfill(bitLen)
    return binStr

  def bin2ascii(self, binStr):
    asciiStr = ""
    i = 0
    binStr = self.validateBin(binStr)
    while i < len(binStr):
      binDigs = binStr[i:i+8]
      asciiStr += chr(int(binDigs, 2))
      i += 8
    return asciiStr

  def hex2base64(self, hexStr):
    import base64
    b64Str = base64.b64encode(base64.b16decode(hexStr))
    return b64Str

  def base642hex(self, b64Str):
    import base64
    hexStr = base64.b16encode(base64.b64decode(b64Str))
    return hexStr

  def base642ascii(self, b64Str):
    import base64
    asciiStr = base64.b64decode(b64Str)
    return asciiStr.decode()

  def ascii2base64(self, asciiStr):
    import base64
    if type(asciiStr) == str:
      asciiStr = asciiStr.encode()
    b64Str = base64.b64encode(asciiStr)
    return b64Str.decode()

  def xor(self, in1, in2):
    if type(in1) == bytes or type(in1) == bytearray:
      in1 = in1.decode()[2:]
    if type(in2) == bytes or type(in2) == bytearray:
      in2 = in2.decode()[2:]
    if len(in1) > len(in2):
      print("Length of input #1 is greater than #2. Trimming input #1.")
      in1 = in1[:len(in2)]
    if len(in2) > len(in1):
      print("Length of input #2 is greater than #1. Trimming input #2.")
      in2 = in2[:len(in1)]
    xorStr = ""
    for bit1, bit2 in zip(in1, in2):
      xorStr += str(int(bit1) ^ int(bit2))
    return xorStr

  def gcd(self, a, b):
    if b == 0:
      return a
    else:
      return self.gcd(b, a%b)

  def residue(self, p, allCols=False, doPrint=False):
    numRows = p-1
    numCols = p-1
    for g in range(1, numRows+1):
      vals = []
      if self.gcd(g, p) != 1: continue
      for j in range(1, numCols+1):
        val = pow(g, j, p)
        vals.append(val)
        if val == 1 and not allCols:
          break
      vals.sort()
      if doPrint:
        print(vals)
      return vals

  def modInverse(self, a, m):
    for x in range(1, m):
      if (((a%m) * (x%m)) % m ==1):
        return x
    return -1

  def totient(self, n):
    assert n >= 1
    count = 0
    for i in range(n):
      if self.gcd(i, n) == 1:
        count += 1
    return count

  def fermatEulerPrimeTest(self, num2test, numtrials):
    import random
    aPrime = True
    randGen = random.SystemRandom()
    for i in range(numtrials):
      a = randGen.randrange(1, num2test)
      # Is 'a' witness for composite? 
      # pow(a, N-1, N) is a^N-1 (mod N)
      if pow(a, num2test-1, num2test) != 1:
        return not aPrime
      return aPrime # likely prime (but not certain)

  def gcmValidateWN(self, N, weight):
    res = self.gcd(N, weight)
    return res

  def gcmTrapdoor(self, superIncSeq, weight, N):
    T = (weight * superIncSeq) % N
    return T

  def gcmGenPubKey(self, superIncSeq, weight, N):
    pubKey = []
    for i in range(0, len(superIncSeq)-1):
      pubKey.append(self.gcmTrapdoor(superIncSeq[i], weight, N))
    return pubKey

  def gcmSolveSuperIncSeq(self, target, superIncSeq):
    tmp = superIncSeq[::-1]
    myNums = []
    idx = []
    i = 0
    for num in tmp:
      if num <= target:
        myNums.append(num)
        target = target - num
        idx.append(len(superIncSeq)-i-1)
      i += 1
    myNums = myNums[::-1]
    idx = idx[::-1]
    return myNums, idx

  def birthdayParadox(self):
    import math
    answer = input("Enter input type ([decimal] or [nBits]): ")
    n = input("Enter value (decimal number or number of bits): ")
    if answer == "nBits":
      res = 2 ** (n / 2)
    elif answer == "decimal":
      res = math.sqrt(.25 + 2 * math.log(2) * n)
    else:
      print("Input type not recognized")
      return
    print("Number of things (or trials) required to achieve 50% chance of collision: ", res)
    return res

  def cyclicGroupGen(self, n, operator='mult'):
    group = []
    if operator == 'mult':
      for i in range(0, n):
        test = self.gcd(i, n)
        if test == 1:
          group.append(i)
    elif operator == 'add':
      for i in range(0, n):
        group.append(i)
    else:
      print("Group operator not recognized")
    return group

  def findGenerators(self, group, operator='mult'):
    gens = []
    if operator == 'mult':
      groupOrder = len(group) + 1
      for a in group:
        tmp = []
        for b in group:
          tmp.append(pow(a, b, groupOrder))
        tmp.sort()
        if tmp == group:
          gens.append(a)
    elif operator == 'add':
      groupOrder = len(group)
      for a in group:
        if self.gcd(a, groupOrder) == 1:
          gens.append(a)
    else:
      print("Group operator not recognized")
    return gens