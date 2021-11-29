__version__ = '0.0.2'

from publishnewsextratorp.file1 import IniciarDriver, ExcecaoAnoInvalido, ExtracaoPublishNews
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd