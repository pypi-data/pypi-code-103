from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
import lxml, os, copy, pandas, time, datetime, requests, sys

class SSTime:
    
    month_table = [ 
        "i", "f", "m", "a", "M", "j", "J", "A", "s", "o", "n", "d"     
    ]

    def help():
        
        print("SSTime: ")
        
        print("\t[1] SSTime.name(basename = \"\", extension = \"\")\n")
    
    def _format_length(data, length):
        
        data = (str(data) if (type(data) != str) else data)
        
        return (length - len(data)) * "0" + data
    
    def name(basename = "", extension = ""):
        
        CT = datetime.datetime.now()
        
        year = int(CT.strftime("%y"))
        
        month = int(CT.strftime("%m"))
        
        day = int(CT.strftime("%d"))
        
        hour = int(CT.strftime("%H"))
        
        minute = int(CT.strftime("%M"))
        
        second = int(CT.strftime("%S"))
        
        return (
            f"{basename}_D-{SSTime.month_table[month - 1]}{SSTime._format_length(day, 2)}20{year}_T-{SSTime._format_length(hour, 2)}{SSTime._format_length(minute, 2)}{SSTime._format_length(second, 2)}{extension}"
        )

class SSParse:
    
    def help():
        
        print("SSParse:")
        
        print("\t[1] __init__(self, filename)")
        
        print("\t[2] fetch(self, key) # folder , name , extension \n")
    
    def __init__(self, filename):
        
        if (type(filename) != str):
            
            print(f"Warning [SSParse]: {filename} is not of type string.\n")
            
            self.valid = False
            
        else:
            
            self.valid = True
            
            self.filename = filename
            
            self.__parse_name()
            
    def __parse_name(self):
        
        _extension = (f".{self.filename.split('.')[-1]}" if ("." in self.filename) else "")
        
        name = self.filename[:len(self.filename) - len(_extension)]
        
        _name = (name.split("/")[-1] if ("/" in name) else name)
        
        _folder = name[:len(name) - len(_name)]
        
        self.dictionary = {
            "name" : _name,
            "folder" : _folder,
            "extension" : _extension
        }
        
    def fetch(self, key):
        
        if (self.valid):
            
            if (key in self.dictionary):
                
                return self.dictionary[key]
            
            else:
                
                print(f"Warning [SSParse]: {key} is not a valid key for fetching.\n")
                
        else:
            
            print("Warning [SSParse]: invalid filename.\n")
            
class SSFormat:
    
    class __Dict:
        
        def __init__(self):
            
            self.formatList = {
                "element_type" : [ None, str ],
                "search_type" : [ None, str ],
                "search_clue" : [ None, str ],
                "multiple" : [ False, bool ],
                "extract" : [ None, str ],
                "format" : [ None, any ],
                "nickname" : [ None, str ],
                "filter" : [ None, any ],
                "keep" : [ True, bool ]
            }
            
        def get(self, key):
            
            if (key in self.formatList):
                
                return self.formatList[key][0]
            
            else:
                
                print(f"Warning [SSFormat]: cannot fetch value with key {key}.\n")
        
        def alter(self, key, newVal):
            
            if ((key in self.formatList) and ((self.formatList[key][1] == any) or (type(newVal) == self.formatList[key][1]))):
                
                self.formatList[key][0] = newVal
                
            else:
                
                print(f"Warning [SSFormat]: cannot update {key} with {newVal}.\n")
    
    def help():
        
        print("SSInfo(): ")
        
        print("\t__init__(self, element_type, search_type = None, search_clue = None, multiple = False, extract = None, format = None, nickname = None, filter = None, keep = True)\n")
        
    def __parse_arguments(self, ** kwargs):
        
        for key, val in kwargs.items():
            
            self.dataList.alter(key, val)
            
    def __init__(self, element_type, ** kwargs):
        
        self.dataList = self.__Dict()
        
        self.dataList.alter("element_type", element_type)
        
        self.__parse_arguments(**kwargs)
    
    def __getitem__(self, key):
        
        return self.dataList.get(key)
    
class SSInfo:
    
    def help():
        
        print("SSInfo(): __init__(self, f_site, f_page, f_item, f_attr)\n")
    
    def __init__(self, f_site, f_page, f_item, f_attr):
        
        self.infoList = {
            "f_site" : f_site,
            "f_page" : f_page,
            "f_item" : copy.deepcopy(f_item),
            "f_attr" : copy.deepcopy(f_attr)
        }
            
    def __getitem__(self, key):
        
        if (key in self.infoList):
            
            return self.infoList[key]
        
        else:
            
            print("Warning [SSInfo]: cannot fetch value with key {key}.\n")
    
class SSData:
    
    def help():
        
        print("SSData(): ")
        
        print("\t[1] __init__(self, info, buffer = 100, timesleep = 0, filename = None)")
        
        print("\t[2] empty_data(self)")
        
        print("\t[3] buffer_exceeded(self)")
        
        print("\t[4] add_data(self, newData)")
        
        print("\t[5] save_data(self, start = False)\n")
    
    def __init__(self, info, buffer = 100, timesleep = 0, filename = None):
        
        self.info, self.buffer, self.filename = copy.deepcopy(info), buffer, self.__validate_name(filename)
        
        self.data, self.columns, self.tempname = self.empty_data(), self.__find_columns(), datetime.datetime.now().strftime("sstemp_%y%m%d%H%M%S.csv")
        
        self.timesleep = timesleep
    
    def __validate_name(self, name):
        
        if (type(name) != str):
            
            print(f"Warning [SSData]: {name} is not a string, using a random name.\n")
            
            return datetime.datetime.now().strftime("ssdata_%y%m%d%H%M%S.csv")
        
        elif ((len(name) >= 5) and (name[-4:] == ".csv")):
            
            return name
        
        else:
            
            print(f"Warning [SSData]: {name} is not a csv file, altering the file extension.\n")
            
            return name + ".csv"
            
    def empty_data(self):
        
        self.data = []
        
        return []
    
    def __find_columns(self):
        
        columns = []
        
        for index, attr in enumerate(self.info["f_attr"]):
            
            nickname = attr["nickname"]
            
            columns.append(nickname if (nickname != None) else index)
            
        return columns
    
    def buffer_exceeded(self):
        
        return (len(self.data) >= self.buffer)
    
    def add_data(self, newData):
        
        self.data += newData
    
    def __save_data(self):
        
        with open(self.filename, "a", encoding = "UTF-8") as WFILE:
            
            with open(self.tempname, "r", encoding = "UTF-8") as RFILE:
                
                WFILE.write(RFILE.read())
                
        os.remove(self.tempname)
    
    def __get_key(self, attrIndex):
    
        return self.columns[attrIndex]
        
    def __collapse_filter(self, data):
        
        for index in range(len(data) - 1, -1, -1):
            
            keep = True
            
            for _index, attr in enumerate(self.info["f_attr"]):
                
                if (self.info["f_attr"][_index]["filter"] != None):
                
                    if not (attr["filter"])(data[self.__get_key(_index)][index]):
                        
                        keep = False
                
            if not (keep):
                
                data = data.drop(index)
                
        for index in range(len(self.info["f_attr"]) - 1, -1, -1):
            
            if not (self.info["f_attr"][index]["keep"]):
            
                column = self.__get_key(index)
                
                data.pop(column)
            
        return data
    
    def save_data(self, start = False):
        
        self.__collapse_filter(pandas.DataFrame(self.data, columns = self.columns)).to_csv(
            self.tempname, 
            index = False, 
            header = start
        )
        
        self.__save_data()

class SSSave:
    
    def help():
        
        print("SSSave:")
        
        print("\t[1] __init__(self, filename, directlink, buffer = 4096, progress_bar = False, overwrite = None)")
        
        print("\t[2] download(self)\n")
    
    def __init__(self, filename, directlink, buffer = 4096, progress_bar = False, overwrite = None):
        
        self.buffer, self.progress_bar, self.overwrite = buffer, progress_bar, overwrite
        
        if ((type(filename) != str) or (type(directlink) != str)):
            
            print("Warning [SSSave]: arguments must be of string type.\n")
            
            self.valid = False
            
        else:
            
            self.filename, self.directlink, self.valid = filename, directlink, True
            
    def __file_exists(self, filename):
        
        if ((self.overwrite != True) and (os.path.isfile(filename))):
            
            fileParse = SSParse(filename)
            
            if (self.overwrite == None):
                
                while True:
                    
                    print(f"Warning [SSSave]: file {filename} already exists, overwrite? (Y/N)")
                    
                    userInput = input("> ").lower()
                    
                    if ("y" in userInput):
                        
                        return filename
                    
                    elif ("n" in userInput):
                        
                        break
            
            return datetime.datetime.now().strftime(f"{fileParse.fetch('folder')}ssfile_%y%m%d%H%M%S{fileParse.fetch('extension')}")
        
        else:
            
            return filename
    
    def _show_progress(self, current, total, endline = False):
        
        if (self.progress_bar):
        
            sys.stdout.write(f"\rDownloading [{self.directlink}] -> [{self.filename}] ({round(current/total*100, 1)}%)")
            
            sys.stdout.flush()

        if (endline):
   
            print("\n")
    
    def download(self):
        
        if (self.valid):

            self.filename = self.__file_exists(self.filename)

            fileData = requests.get(self.directlink, stream = True)
            
            length = int(fileData.headers.get("content-length"))
            
            temp = 0
            
            self._show_progress(temp, length)
            
            with open(self.filename, "wb") as writeFile:
                
                for data in fileData.iter_content(chunk_size = self.buffer):
                    
                    writeFile.write(data)
                    
                    self._show_progress(temp, length)
                    
                    temp += len(data)
                    
            self._show_progress(temp, length, endline = True)
        
        else:
            
            print("Warning [SSSave]: cannot download file because of unsupported arguments.\n")
        
class ScraperBaseClass:
    
    def __init__(self, info):
        
        self.info = copy.deepcopy(info)
        
        self.f_page = self._format_webpage()
    
    def _format_webpage(self):
        
        site, page = self.info.info["f_site"], self.info.info["f_page"]
        
        A, B = site[-1] == "/", page[0] == "/"
        
        if (A and B):
            
            return site[:-1] + page
        
        elif (A or B):
            
            return site + page
        
        else:
        
            return site + "/" + page
    
    def _find_attributes(self, source, attr):
        
        data = source.find_all if (attr["multiple"]) else source.find
        
        data = data(
            attr["element_type"],
            ** (
                {} if ((attr["search_type"] == None) or (attr["search_clue"] == None)) else { attr["search_type"] : attr["search_clue"] }
            )
        )
        
        data = (
            data if (type(attr["extract"]) != str)
            else data.text if (attr["extract"] == "text")
            else data[attr["extract"]]
        )
        
        if (attr["format"] != None):
            
            data = attr["format"](data)
            
        return data
    
    def _scrape_webpage(self, page):
        
        raise NotImplementedError("Must override ScraperBaseClass with StaticScraper or DynamicScraper!\n")
    
    def _show_progress(self, page = None, progress = None, pages = None, finish = False):
        
        
        if (finish):
            
            sys.stdout.flush()
        
        else:
            
            sys.stdout.write(f"\r\tScraping page {page} ({progress}/{pages})")
    
    def scrape(self, start = 1, pages = 1):
        
        _start = True
        
        print(f"Scraping {self.info.info['f_site']}")
        
        for page in range(start, start + pages):
            
            progress = page - start + 1
            
            self._show_progress(page, progress, pages)
            
            self.info.add_data(self._scrape_webpage(page))
            
            if (self.info.buffer_exceeded()):
                
                self.info.save_data(_start)
                
                self.info.empty_data()
                
                _start = False
            
            self._show_progress(finish = True)
            
        print("")
            
        if (len(self.info.data)):
            
            self.info.save_data(_start)
            
            self.info.empty_data()
    
class StaticScraper(ScraperBaseClass):
    
    def help():
        
        print("StaticScraper(): ")
        
        print("\t[1] __init__(self, info)")
        
        print("\t[2] scrape(self, start = 1, pages = 1)\n")
    
    def __init__(self, info):
        
        super(StaticScraper, self).__init__(info)
    
    def _scrape_webpage(self, page):
        
        webpage = self.f_page.format(page)
        
        data = BeautifulSoup(requests.get(webpage).text, "lxml")
        
        itemList = self._find_attributes(data, self.info.info["f_item"])
        
        scraped = []
        
        for item in itemList:
            
            attrList = []
            
            for attr in self.info.info["f_attr"]:
                
                attrList.append(self._find_attributes(item, attr))
                
            scraped.append(attrList)
            
        time.sleep(self.info.timesleep)
        
        return scraped
    
class DynamicScraper(ScraperBaseClass):
    
    driver_names = {
        "chrome" : webdriver.Chrome
        #, 
        #"firefox" : webdriver.Firefox   
    }
    
    def help():
        
        print("DynamicScraper(): ")
        
        print("\t[1] __init__(self, info, driver = 'chrome', path = None, window = True)")
        
        print("\t[2] scrape(self, start = 1, pages = 1)\n")
    
    def __check_boolean(self, value):
        
        if (type(value) != bool):
            
            print(f"Warning [DynamicScraper]: {value} is not a boolean value.\n")
            
            if ((value == 0) or (value == "0") or (value == "f")):
                
                return False
            
        return value
    
    def __check_driver_path(self, path):
        
        if ((type(path) != None) and ((type(path) != str) or (not os.path.isfile(path)))):
            
            raise NameError(f"Webdriver {self.driver} could not be found at {path}.\n")
            
        return path
    
    def __check_driver_name(self, name):
        
        if ((type(name) == str) and (name.lower() in self.driver_names)):
            
            return name.lower()
        
        else:
        
            raise NameError(f"{name} is not a supported driver name.\n\tSupported: {list(self.driver_names.keys())}\n")
    
    def __init__(self, info, driver = "chrome", path = None, window = True):
        
        super(DynamicScraper, self).__init__(info)
        
        self.driver = self.__check_driver_name(driver)
    
        self.path = self.__check_driver_path(path)
        
        self.window = self.__check_boolean(window)
        
    def __get_driver(self, name):
        
        return self.driver_names[name]
    
    def __get_parameter(self):
        
        op = {}
        
        if (self.path != None):
            
            _op = ChromeService(self.path)
            
            op["service"] = _op
            
        if (self.window == False):
            
            _op = webdriver.ChromeOptions()
            
            _op.add_argument("headless")
            
            op["options"] = _op
                
        return op
    
    def _scrape_webpage(self, page):
        
        webpage = self.f_page.format(page)
        
        driver = self.__get_driver(self.driver)(
            **(self.__get_parameter())
        )
        
        driver.get(webpage)
        
        data = BeautifulSoup(driver.page_source, "lxml")
        
        itemList = self._find_attributes(data, self.info.info["f_item"])
        
        scraped = []
        
        for item in itemList:
            
            attrList = []
            
            for attr in self.info.info["f_attr"]:
                
                attrList.append(self._find_attributes(item, attr))
                
            scraped.append(attrList)
            
        time.sleep(self.info.timesleep)
        
        return scraped
"""
def format_price(price):
    return eval(''.join([ x for x in price if x.isnumeric() or x == '.']))
def filter_price(price):
    return (price <= 40)
website = "http://books.toscrape.com/catalogue/"
pageformat = "page-{}.html"
itemformat = SSFormat(
    element_type = "li", search_type = "class_", search_clue = "col-xs-6 col-sm-4 col-md-3 col-lg-3", multiple = True
)
attrList = [
    SSFormat(element_type = "p", search_type = "class_", search_clue = "price_color", extract = "text", nickname = "price", format = format_price, filter = filter_price),
    SSFormat(element_type = "a", extract = "href", nickname = "url")
]
info = SSInfo(website, pageformat, itemformat, attrList)
data = SSData(info, timesleep = 2)
scraper = StaticScraper(data)
scraper.scrape(start = 1, pages = 20)
"""
"""
DynamicScraper.help()
website = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=processor&_sacat=0"
pageformat = "&_pgn={}"
itemformat = SSFormat(
    element_type = "li", search_type = "class_", search_clue = "s-item s-item__pl-on-bottom s-item--watch-at-corner", multiple = True
)
attrList = [
    SSFormat(element_type = "a", search_type = "class_", search_clue = "s-item__link", extract = "href")        
]
info = SSInfo(website, pageformat, itemformat, attrList)
data = SSData(info, timesleep = 0)
scraper = DynamicScraper(data, driver = "Chrome", path = "../../../chromedriver.exe", window = False)
scraper.scrape(start = 1, pages = 4)
"""
"""
SSSave.help()

file = SSSave("temp.json", "link", progress_bar = True, overwrite = False)

file.download()
"""
"""
SSTime.help()
timenow = SSTime.name()
print(timenow)
"""