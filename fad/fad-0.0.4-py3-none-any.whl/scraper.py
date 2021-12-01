import time
import shutil

import requests
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from fad.utils import get_driver_executable_path, get_anchor_selector, create_save_directory, progressbar, convert_title
from fad.constants import FACEBOOK_DOMAIN

EXECUTABLE_PATH = str(get_driver_executable_path())

class Scraper(object):
    def __init__(self, config):
        """
        Initilize a Scraper instance
        @param config - obj | The config object
        """
        print('Initialize scraper ...')
        self.config = config
        opts = Options()
        opts.headless = not config['debug']

        self.browser = Firefox(executable_path=EXECUTABLE_PATH, options=opts)
        self.selector = get_anchor_selector(config['type'])

    def navigate(self, url):
        """
        Navigate to an url
        @param url - str | The url to navigate
        """
        if url.startswith('/'):
            url = FACEBOOK_DOMAIN + url
        self.browser.get(url)

    def exec(self, script):
        """
        Execute JavaScript code
        @param script - str | The script to execute
        @return result of script
        """
        return self.browser.execute_script(script)

    def find_element(self, selector):
        """
        Safe find an element matching css selector
        @param selector - str | The css selector
        @return the element (or None if the element doesn't exist)
        """
        try:
            return self.browser.find_element(By.CSS_SELECTOR, selector)
        except NoSuchElementException:
            return None

    def find_elements(self, selector):
        """
        Safe find all elements matching css selector
        @param selector - str | The css selector
        @return the element (or None if the element doesn't exist)
        """
        return self.browser.find_elements(By.CSS_SELECTOR, selector)

    def find_element_with_timeout(self, selector):
        """
        Safe wait until finding an element
        @param selector - str | The css selector
        @return the element (or None if the element doesn't exist)
        """
        try:
            return WebDriverWait(self.browser, self.config['wait_timeout']).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        except (NoSuchElementException, TimeoutException):
            return None

    def login(self):
        """
        Try to login facebook with Email & Password
        @return boolean | If success, return True
        """

        # bypass login process if email or password (or both) is missing 
        if not self.config['email'] or not self.config['password']:
            return False

        # login if email and password provided
        print('Try to logging in Facebook with email & password provided ...')
        self.navigate(FACEBOOK_DOMAIN)
        # Selectors
        login_button = self.find_element('button[name="login"]')
        email_field = self.find_element('input#email')
        pass_field = self.find_element('input#pass')

        if not login_button or not email_field or not pass_field:
            print('Error: Something went wrong')
            self.browser.quit()
            exit()
        
        # fill email & password
        email_field.send_keys(self.config['email'])
        pass_field.send_keys(self.config['password'])
        login_button.click()
        return True

    
    """
    Collect all photo anchors in the html page
    """
    def get_anchors(self):
        """
        Navigate to an album & get all anchor elements of photos
        """
        print('Getting anchor elements ...')
        # navigate to album url & wait for page completely loaded
        self.navigate(self.config['album']) 
        self.find_element_with_timeout(self.selector)
        # scroll to the end of the page
        last_height = self.exec("return document.body.scrollHeight")

        while True:
            self.exec("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(self.config['timeout'])
            # stop when scrolling to the end of the page
            new_height = self.exec("return document.body.scrollHeight")
            
            if new_height == last_height:
                break

            last_height = new_height
        
        anchors = self.find_elements(self.selector)
        return anchors


    """
    Download all photos from anchors collected
    """
    def download_photos(self, anchors):
        print("Starting downloader ...")
        if len(anchors) == 0:
            print("WARN: No photos loaded. Script is exiting.")
            self.browser.quit()
            exit()
        
        single_photo_urls = list(map(lambda a: a.get_attribute('href'), anchors))
        default_album_name = convert_title(self.browser.title)
        save_dir = create_save_directory(self.config['dir'], self.config['name'] or default_album_name)
        count = 0
        total = len(single_photo_urls)

        for sp_url in single_photo_urls:
            self.navigate(sp_url)
            photo = self.find_element_with_timeout('img[data-visualcompletion="media-vc-image"]')
            
            if not photo:
                continue

            url = photo.get_attribute('src')
            file_name = url.split('?')[0].split('/')[-1]
            res = requests.get(url, stream=True)
            save_path = save_dir / file_name
            
            if res.status_code == 200:
                with open(save_path, 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
            
            count = count + 1
            progressbar(count, total, 'Downloading:  ')

        # print successful download message
        print('\n')
        print(f'Dowload Completed: {total} photos')
        print(f'Open {save_dir} to see your downloaded album')
        # Quit browser after done
        self.browser.quit()
    
