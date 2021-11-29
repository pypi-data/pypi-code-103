from selenium import webdriver
from functools import partial
import os

class WebDriver():
    _prefs = {
        "download.default_directory": None,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True
    }

    def __init__(self, driver='chrome', prefs='default', downloadDest='/'):
        self.options = webdriver.ChromeOptions()
        self.downloadDest = downloadDest
        if prefs == 'default':
            _prefs['download.default_directory'] = downloadDest
            self.options.add_experimental_option('prefs', _prefs)
        elif prefs is not None:
            self.options.add_experimental_option('prefs', prefs)
        if driver == 'chrome' :
            b = partial(webdriver.Chrome)
            if prefs: b = partial(b, chrome_options = self.options)
            self.browser = b()
        else:
            self.browser = None
    
    def quit(self):
        self.browser.quit()

    def downloadFile(self, url, newFilename=None, quitAfter=True):
        self.browser.get(url)
        pth = self.downloadDest
        fname = max([pth + '/' + f for f in os.listdir(pth)], key=os.path.getmtime)
        if newFilename:
            newFilename = os.path.basename(newFilename)
            newFilename = os.path.join(os.path.dirname(pth), newFilename)
            os.rename(fname, newFilename)
            return newFilename
        return fname

