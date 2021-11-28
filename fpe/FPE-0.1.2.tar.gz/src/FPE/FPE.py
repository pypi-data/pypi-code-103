from FPE import Format
from FPE import Mode
from FPE import formatter
from FPE import fpe_csv 

def generate_tweak(length):
    return formatter.mode_selector.ff1.get_random_bytes(length)

def generate_key():
    return formatter.mode_selector.ff1.get_random_bytes(16) 

class New:
    def __init__(self, key, tweak, mode):
        if len(key) != 16:
           raise ValueError(f"{key} is not a valid key, the length must be 128 bit. The length was: {len(key)*8}")
        if (len(tweak) != 7 and mode == Mode.FF3):
            raise ValueError(f"{tweak} is not a valid Tweak, the length must be 56 bit. The length was: {len(tweak)*8}")
        if not Mode.isMode(mode):
            raise ValueError(f"{mode} is not a valid mode, please use a valid mode. All valid modes can be found in the README")
    
        
        
        
        self.tweak = tweak
        self.mode = mode
        self.key = key

    def set_key(self,key):
        self.key = key

    def encrypt(self,text,dataFormat):
        return formatter.encrypt(text,self.key,self.tweak,dataFormat,self.mode)

    def decrypt(self,text,dataFormat):
        return formatter.decrypt(text,self.key,self.tweak,dataFormat,self.mode)

    def encryptCSV(self,csvFilePath,encryptedFilePath,formats):
        return fpe_csv.encrypt_csv(csvFilePath,encryptedFilePath,self.key,self.tweak,formats,self.mode)

    def decryptCSV(self,csvFilePath,decryptedFilePath,formats): 
        return fpe_csv.decrypt_csv(csvFilePath,decryptedFilePath,self.key,self.tweak,formats,self.mode)

    def generateData(self,csvFilePath,rows,formats,names):
        return fpe_csv.generate_test_data(csvFilePath,rows,formats,names,self.tweak,self.mode)  


