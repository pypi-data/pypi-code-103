import asyncio
import os
import random
import time
from random import random

import pyperclip
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


class spyder():

    def agefans(self,thing):
        r= requests.get(f"https://www.agefans.cc/search?query={thing}&page=1")
        agefans=r.text
        soup = BeautifulSoup(agefans, 'html.parser')
        boardNameElements = soup.find_all('div', class_="cell_imform")
        links = [t.find('a',class_="cell_imform_name")['href'] for t in boardNameElements]
        name = [t.find('a',class_="cell_imform_name").text.replace('\n','').replace('\r','').replace('\xa0','').replace(' ','') for t in boardNameElements]
        lenlinks=len(links)
        lenname=len(name)
        if lenname!= lenname:
            print("error")
            quit

        data={}
        for i in range(lenlinks):
            data[i]={}
            data[i]["name"]=name[i]
            data[i]["link"]="https://www.agefans.cc"+links[i]
        return data

    def anime1(self,thing):
        r= requests.get(f"https://anime1.me/?s={thing}")
        anime1=r.text
        soup = BeautifulSoup(anime1, 'html.parser')
        boardNameElements = soup.find_all('h2', class_="entry-title")
        links = [t.find('a')['href'] for t in boardNameElements]
        name = [t.find('a').text.replace('\n','').replace('\r','').replace('\xa0','').replace(' ','') for t in boardNameElements]
        lenlinks=len(links)
        lenname=len(name)
        data={}
        if lenname!= lenname:
            print("error")
            quit
        for i in range(lenlinks):
            data[i]={}
            data[i]["name"]=name[i]
            data[i]["link"]=links[i]
        return data

    def youtube_search(self,thing):
        chrome = webdriver.Chrome()
        chrome.get("https://www.youtube.com/")
        sc = chrome.find_element_by_id("search")
        sc.send_keys(thing)
        sc = chrome.find_element_by_id("search-icon-legacy")
        sc.submit()
        soup = BeautifulSoup(chrome.page_source, "html.parser")
        chrome.close()
        soup=soup.find("a",class_="yt-simple-endpoint style-scope ytd-video-renderer")
        soup=soup.get("href")
        return f"https://www.youtube.com{soup}"

    def translate(self,thing):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless') 
        chrome = webdriver.Chrome(chrome_options=chrome_options)
        chrome.get("https://translate.google.com.tw/?sl=auto&tl=zh-TW&op=translate")
        sc = chrome.find_element_by_class_name("er8xn")
        sc.send_keys(thing)
        time.sleep(1)
        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        chrome.close()
        soup=soup.find("div",class_="J0lOec")
        soup=soup.find("span",jsname="W297wb").text
        return(soup)

    def removebg(self,thing):
        pyperclip.copy(thing)
        chrome = webdriver.Chrome()
        chrome.get("https://www.remove.bg/zh/upload")
        sc=chrome.find_element_by_xpath ('//button')
        sc.send_keys(Keys.CONTROL,'v')
        time.sleep(1)
        soup = BeautifulSoup(chrome.page_source, "html.parser")
        soup=soup.find_all("img")
        url=soup[1].get("src")
        return(url)

    def manhua(self,thing):
        mahun= []
        path=f".\mahun"
        folder = os.path.exists(f".\mahun")
        if not folder:
            os.mkdir(f'.\mahun')
            print('-----建立成功-----')
        else:
            print(path+'目錄已存在')
        url=f"https://www.manhuaren.com/search?title={thing}&language=1"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless') 
        chrome = webdriver.Chrome(chrome_options=chrome_options)
        chrome.get(f"{url}")
        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        chrome.close()
        soup=soup.find_all("a", limit=10)
        soup=soup[3].get('href')
        url=f"https://www.manhuaren.com{soup}"
        chrome = webdriver.Chrome(chrome_options=chrome_options)
        chrome.get(f"{url}")
        folder = os.path.exists(f".\mahun\{soup}")
        name=soup
        if not folder:
            os.mkdir(f'.\mahun\{name}')
            print('-----建立成功-----')
        else:
            print(path+'目錄已存在')
        btn= chrome.find_elements_by_xpath("//a[@onclick='sortBtnClick(this);' and @class='detail-list-title-right sort-2']")[0]
        btn.click()
        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        soup=soup.find_all("a", class_= "chapteritem")
        print(soup)
        print(len(soup))
        for i in range(len(soup)):
            mahun.append(soup[i].get('href'))
            path=f".\mahun\{name}"
            folder = os.path.exists(f".\mahun\{name}\{i}")
            if not folder:
                os.mkdir(f'.\mahun\{name}\{i}')
                fp = open(f'.\mahun\{name}\{i}\網址.txt', "a")
                fp.write("https://www.manhuaren.com"+mahun[i]) 
                fp.close()
                print('-----建立成功-----')
            else:
                print(path+'目錄已存在')
        chrome.close()
        for i in range(len(soup)):
            url="https://www.manhuaren.com"+mahun[i]
            print(url)
            chrome = webdriver.Chrome(chrome_options=chrome_options)
            chrome.get(url)
            btn= chrome.find_elements_by_xpath("//img[@style='position: absolute;width: 8%;bottom: 0;right: 4%;margin-bottom: 137%;']")[0]
            btn.click()  
            j=1
            while 1:
                try:
                    url = chrome.find_element_by_css_selector('#cp_img>img').get_attribute('src')
                    r = requests.get(url)
                    soup = BeautifulSoup(chrome.page_source, 'html.parser')
                    try:
                        soup=soup.find("div",class_="mask")
                        soup=soup.get("style")
                        if soup=="display:none;":
                            with open(f'.\mahun\{name}\{i}\{j}.png', 'wb') as f:
                                f.write(r.content)
                        else:
                            j=1
                            chrome.close()
                            break
                        time.sleep(1)
                        pages = chrome.find_element_by_link_text("下一页")
                        chrome.execute_script("arguments[0].click();", pages)
                        j=j+1
                    except:
                        try:
                            soup=soup.find("p",class_="final-title")
                            print(soup)
                            if soup=="未完待续，敬请期待更新":
                                j=1
                                chrome.close()
                                break
                        except:
                            with open(f'.\mahun\{name}\{i}\{j}.png', 'wb') as f:
                                    f.write(r.content)
                            time.sleep(1)
                            pages = chrome.find_element_by_link_text("下一页")
                            chrome.execute_script("arguments[0].click();", pages)
                            j=j+1 
                except:
                    print("下載完成")
                    chrome.close()
                    exit()

    def schimage(self,thing):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless') 
        
        chrome = webdriver.Chrome(chrome_options=chrome_options)
        chrome.get("http://iqdb.org/")
        sc = chrome.find_element_by_id("url")
        sc.send_keys(thing)
        sc.submit()
        soup = BeautifulSoup(chrome.page_source, 'html.parser')
        chrome.close()
        soup=soup.find_all("a", limit=2)
        soup=soup[1].get('href')
        if soup[0]!="h":
            soup="http:"+soup
        return(soup)

    def yandere(self,thing):
        response = requests.get(f"https://yande.re/post?tags={thing}")
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            soup=soup.find("span",class_="tag-type-character")
            tag=soup.find("a").text
            response = requests.get(f"https://yande.re/post?tags={tag}")
            soup = BeautifulSoup(response.text, "html.parser")
        except:
            pass
        soup=soup.find("div",class_="pagination")
        soup=soup.find_all("a")
        soup=soup[len(soup)-2].text
        a=random.randint(0,int(soup))
        response = requests.get(f"https://yande.re/post?page={a}&tags={tag}")
        soup = BeautifulSoup(response.text, "html.parser")
        soup=soup.find_all("a",class_="thumb")
        a=random.randint(0,len(soup))
        soup=soup[a].get("href")
        response = requests.get(f"https://yande.re/{soup}")
        soup = BeautifulSoup(response.text, "html.parser")
        soup=soup.find("img",class_="image js-notes-manager--toggle js-notes-manager--image")
        soup=soup.get("src")
        return(soup)

    def konachan(self,thing):
        response = requests.get(f"https://konachan.com/post?tags={thing}")
        soup = BeautifulSoup(response.text, "html.parser")
        try:
            soup=soup.find("span",class_="tag-type-character")
            tag=soup.find("a").text
            response = requests.get(f"https://konachan.com/post?tags={tag}")
            soup = BeautifulSoup(response.text, "html.parser")
        except:
            pass
        soup=soup.find("div",class_="pagination")
        soup=soup.find_all("a")
        soup=soup[len(soup)-2].text
        a=random.randint(0,int(soup))
        response = requests.get(f"https://konachan.com/post?tags={tag}")
        soup = BeautifulSoup(response.text, "html.parser")
        soup=soup.find_all("a",class_="thumb")
        a=random.randint(0,len(soup))
        soup=soup[a].get("href")
        response = requests.get(f"https://konachan.com/{soup}")
        soup = BeautifulSoup(response.text, "html.parser")
        soup=soup.find("img",class_="image")
        soup=soup.get("src")
        return(soup)

    def danbooru(self,thing):
        response = requests.get(f'https://danbooru.donmai.us/posts.json?tags={thing}') 
        jason = response.json()
        
        i=random.randint(1,20)
        picture=(jason[i]["large_file_url"])
        return(picture)

    def math(self,thing):
        chrome = webdriver.Chrome(ChromeDriverManager().install())
        chrome.get("https://zs.symbolab.com/solver/step-by-step/a+a=2?or=input")
        time.sleep(1)
        soup = BeautifulSoup(chrome.page_source, "html.parser")
        chrome.close()
        soup=soup.find("span",class_="solution_step_title_text mathquill-embedded-latex mathquill-rendered-math")
        soup=soup.find_all("span")
        for a in soup:
            try:
                ans+=a.text 
            except:
                ans=a.text 
        return(ans)
    

if __name__ == '__main__':
    data=input("meeee")
    sp=spyder()
    output=sp.agefans(data)
    print(output)
