from bs4 import BeautifulSoup
import string
import requests 
from urllib.parse import quote
from selenium import webdriver

def launch_driver(wait=10, driver_directory=None):
    '''Launch a selenium webdriver'''
    if driver_directory is None:
        chromeDriver = "C:/Webdriver/chromedriver.exe"                # set the driver path 
    else: 
        chromeDriver = driver_directory
        
    driver = webdriver.Chrome(executable_path=chromeDriver)       # launch the driver 
    driver.implicitly_wait(wait)                                  # tell the driver to wait at least `wait` seconds before throwing up an error

    return driver

def clean_url(url):
    '''Clean urls with non-english characters such as tildes'''
    non_conformists = [s for s in url if s not in string.printable]       # we get a list of the troublemaker characters 
    for s in non_conformists:
        url = url.replace(s,quote(s))       # and use the quote function from urllib.parse to translate them 
    return url

def fresh_soup(url):    
    '''
    Collects and parses the page source from a given url, returns the parsed page source 
    - url : the url you wish to scrape
    '''
    
    try: 
        source = requests.get(url).content
        
    except:                                                                   # if the url is reject due to non formatted characters 
        url = clean_url(url)  
        source = requests.get(url).content
            
    soup = BeautifulSoup(source,"lxml")                                       # process it using beautiful soup 
    
    return soup

# Past Version using urllib 
# def fresh_soup(url):    
#     '''
#     Collects and parses the page source from a given url, returns the parsed page source 
#     - url : the url you wish to scrape
#     '''
#     hdr = {'User-Agent': 'Mozilla/5.0'}                                       # we will browse as if using the Mozilla Browser
    
#     try: 
#         req = urllib.request(url,headers=hdr)                                 # make a url request using the specified browser
#         source = urllib.urlopen(req,timeout=10).read()                        # retrieve the page source
        
#     except:                                                                   # if the url is reject due to non formatted characters 
#         url = clean_url(url)
        
#         req = urllib.Request(url,headers=hdr)                                 # the url should be readable now 
#         source = urllib.urlopen(req,timeout=10).read()                        
            
#     soup = BeautifulSoup(source,"lxml")                                       # process it using beautiful soup 
    
#     return soup