from urllib import request
import zipfile
import os


class Manager:
    def __init__(self, browser="chrome"):
        self.browser = browser
        
    def chromeDriver(self):
        try:
            release = request.urlopen("https://chromedriver.storage.googleapis.com/LATEST_RELEASE").read().decode()

            request.urlretrieve(f"https://chromedriver.storage.googleapis.com/{release}/chromedriver_win32.zip", "chromedriver.zip")

            with zipfile.ZipFile("chromedriver.zip", "r") as ref:
                ref.extractall()

            os.remove("chromedriver.zip")
            return os.path.abspath("chromedriver.exe")
        except:
            raise Exception
