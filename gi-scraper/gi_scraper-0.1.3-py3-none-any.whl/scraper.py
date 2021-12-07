from selenium import webdriver
from selenium.webdriver import ActionChains
from threading import Thread
from .progressbar import ProgressBar
from .driver_manager import Manager
from tkinter.filedialog import askdirectory
from urllib import parse, request
from tkinter import Tk
import time
import os


class Scraper:
    def __init__(self, query, count=50, tCount=1, quality=True, downloadImages=False, saveList=False, defaultDir=False, dirPath="", driverPath=""):
        self.images = dict()
        self.ctr = 0
        self.url = "https://www.google.com/search?{}&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjR5qK3rcbxAhXYF3IKHYiBDf8Q_AUoAXoECAEQAw&biw=1291&bih=590"
        if driverPath == "":
            driverPath = Manager().chromeDriver()
        self.driverPath = driverPath.replace("/", "\\")
        self.fetch(query, count, tCount, quality, downloadImages, saveList, defaultDir, dirPath)
    
    def checkDir(self, dName, cnt):
        if os.path.isdir(dName):
            dName = dName.replace(f" ({cnt - 1})", "")
            dName = dName + f" ({cnt})"
            return self.checkDir(dName, cnt + 1)
        else:
            return dName
    
    def createDir(self, query, defaultDir, dirPath):
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        if dirPath is not None and len(dirPath) != 0:
            directory = dirPath + "\\GIS Downloads\\" + query
        else:
            if not defaultDir:
                directory = askdirectory(parent=root)
                if directory is not None and len(directory) != 0:
                    directory = directory + "\\GIS Downloads\\" + query
                    directory.replace("/", "\\")
                else:
                    print("No Directory Selected... Creating Default Directory!")
                    directory = os.getcwd() + "\\GIS Downloads\\" + query
            else:
                directory = os.getcwd() + "\\GIS Downloads\\" + query
        
        
        directory = self.checkDir(dName=directory, cnt=0)
        os.makedirs(directory, exist_ok=True)
        print("Saving to... ", directory)
        return directory

    def fetch(self, query, count=50, tCount=1, quality=True, downloadImages=False, saveList=False, defaultDir=False, dirPath=""):
        thr = []
        query = query.strip()

        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--headless")
        options.add_argument('--log-level=3')

        if tCount > 8:
            tCount = 8
            print("THREAD COUNT SET : ", tCount, ", LIMITING TO 8")
        else:
            print("THREAD COUNT SET : ", tCount)

        if quality:
            fetch = self.sub_fetch1
            if count > 150:
                print("QUALITY SET : TRUE, GIVEN COUNT :",
                      count, ", LIMITING TO : 150")
                count = 150
        else:
            fetch = self.sub_fetch2
            if count > 300:
                print("QUALITY SET : FALSE, GIVEN COUNT :", count ,", LIMITING TO : 300")
                count = 300
        
        self.pb = ProgressBar(count, "Getting Images")
        
        for i in range(tCount):
            t = Thread(target=fetch, args=(query, options, count, i))
            thr.append(t)
            t.start()
        
        for t in thr:
            t.join()
        
        del self.pb
        
        if downloadImages:
            self.completed = 0
            pCount = tCount
            dirName = self.createDir(query, defaultDir, dirPath)

            pcr = []
            self.downloader = ProgressBar(len(self.images), "Downloading Images")
            for i in range(pCount):
                p = Thread(target=self.download_images, args=(query, dirName, pCount, i))
                pcr.append(p)
                p.start()
            
            for p in pcr:
                p.join()
            
            if saveList:
                self.saveToList(dirName, query)

            del self.downloader
        
        elif saveList and not downloadImages:
            dirName = self.createDir(query, defaultDir, dirPath)
            self.saveToList(dirName, query)
        
        return self.images
    
    def sub_fetch1(self, query, options, count=100, tid=0):
        driver = webdriver.Chrome(executable_path=self.driverPath, chrome_options=options)
        url = self.url.format(parse.urlencode({'q': query}))
        driver.get(url)
        try:
            y = 0
            if tid == 0:
                cnt = 0
            else:
                cnt = 50 * tid

            while True:
                cnt += 1
                if len(self.images) >= count:break
                driver.execute_script(f"window.scrollBy(0, {y});")
                element = driver.find_element_by_id("islmp")
                anchors = element.find_elements_by_css_selector(f"#islrg > div.islrc > div:nth-child({cnt}) > a.wXeWr.islib.nfEiy")
                for anchor in anchors:
                    ActionChains(driver).click(anchor).perform()
                    time.sleep(1.0)
                    img = anchor.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div[2]/div[1]/a/img')
                    if len(self.images) >= count:break
                    else:
                        src = img.get_attribute("src")
                        if src is None:continue
                        src = str(src)
                        if src.startswith("data:image/") or src.startswith("https://encrypted"):continue
                        if src not in self.images.values():
                            self.images[self.ctr] = src
                            self.ctr += 1
                    driver.back()
                y += 1000
                self.pb.ProgressBar(self.ctr)
        except Exception as e:
            pass
    
    def sub_fetch2(self, query, options, count=100, tid=0):
        driver = webdriver.Chrome(executable_path=self.driverPath, chrome_options=options)
        url = self.url.format(parse.urlencode({'q': query}))
        driver.get(url)

        try:
            y = tid * 1000

            while True:
                if len(self.images) >= count:break
                driver.execute_script(f"window.scrollBy(0, {y});")
                imgs = driver.find_elements_by_class_name("rg_i")
                for img in imgs:
                    src = img.get_attribute("src")
                    if len(self.images) >= count:break
                    else:
                        if src is None:continue
                        src = str(src)
                        if src not in self.images.values():
                            self.images[self.ctr] = src
                            self.ctr += 1
                y += 10
                self.pb.ProgressBar(self.ctr)
        except Exception as e:
            pass
    
    def download_images(self, query, dir, pCount=1, tid=0):
        totalTaskLength = len(self.images)
        taskLength = totalTaskLength//pCount
        chunkStart = tid * taskLength
        if tid == pCount - 1:
            chunkEnd = len(self.images)
        else:
            chunkEnd = chunkStart + taskLength
        
        opener = request.build_opener()
        opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        request.install_opener(opener)
        for index in range(chunkStart, chunkEnd):
            img = self.images[index]
            file = f"{dir}\\{query}_{str(tid)}_{str(index).rjust(3,'0')}.jpg"
            try:
                request.urlretrieve(img, file)
                self.completed += 1
                self.downloader.ProgressBar(self.completed)
            except Exception as e:
                pass
    
    def saveToList(self, dirName, query):
        dirName = dirName + f"\\{query}.txt"
        with open(dirName, "a") as fa:
            for index, link in self.images.items():
                fa.write(f"{str(index)} : {link}\n")
