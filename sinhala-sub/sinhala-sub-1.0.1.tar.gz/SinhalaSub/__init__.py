import bs4
import requests
from bs4 import BeautifulSoup as bs

# search engine
def search_sub(Name):
    def did_you(query, other=""):
        text = query + other
        text = text.replace(" ", "+")
        url = 'https://google.com/search?q=' + text
        request_result = requests.get(url)
        soup = bs4.BeautifulSoup(request_result.text, "html.parser")
        did_you_ = ""
        try:
            did_you_ = soup.find('div', {'class': 'MUxGbd v0nnCb lyLwlc'})
            did_you_ = str(did_you_.getText().replace(other, ""))
            did_you_ = did_you_.replace(":https://www.imdb.com/title", "")
        except Exception as e:
            pass
        if did_you_ is None:
            search = query
        else:
            search = did_you_
            search = search.replace("Did you mean: ", "").replace("Showing results for ", "")
        return search

    def baiscopelk_search(search):
        baiscopelk_url = "https://www.baiscopelk.com/?s="
        url = baiscopelk_url + search
        request_result = requests.get(url)
        soup = bs4.BeautifulSoup(request_result.text, "html.parser")
        site_items = soup.find_all('h2', {"class": "post-box-title"})
        links = []
        titles = []
        for x in range(len(site_items)):
            if "mega-menu-link" in str(site_items[x]) or "rel=\"bookmark\"" in str(site_items[x]) or "ttip" in str(
                    site_items[x]):
                pass
            else:
                htmldata = str(site_items[x])
                page_soup1 = bs4.BeautifulSoup(htmldata, "html.parser")
                hreflink = page_soup1.findAll('a')
                if len(hreflink) != 0:
                    search_list = search.split()
                    cc = 1
                    if len(hreflink) != 0:
                        for key in range(len(search_list)):
                            if search_list[key].isnumeric():
                                if str(search_list[key]).lower() not in str(hreflink[0].getText().lower()):
                                    cc = 0
                            else:
                                if str(search_list[key]).lower() + " " not in str(hreflink[0].getText().lower()):
                                    cc = 0
                        if cc == 1:
                            title = hreflink[0].getText()
                            try:
                                ne_title = title[:title.index(" | ")]
                            except:
                                ne_title = title
                            if ne_title not in titles:
                                titles.append(ne_title)
                                links.append(hreflink[0]['href'])
        return {"title": titles, 'link': links}

    def pirate_search(search):
        pirate_url = "https://piratelk.com/?s="
        url = pirate_url + search
        request_result = requests.get(url)
        soup = bs4.BeautifulSoup(request_result.text, "html.parser")
        site_items = soup.find_all('h2', {"class": "post-box-title"})

        links = []
        titles = []
        for x in range(len(site_items)):
            htmldata = str(site_items[x])
            page_soup1 = bs4.BeautifulSoup(htmldata, "html.parser")
            hreflink = page_soup1.findAll('a')
            search_list = search.split()
            cc = 1
            if len(hreflink) != 0:
                for key in range(len(search_list)):
                    if str(search_list[key]).lower() not in str(hreflink[0].getText().lower()):
                        cc = 0
                if cc == 1:
                    title = hreflink[0].getText()
                    try:
                        ne_title = title[:title.index(" | ")]
                    except:
                        ne_title = title
                    if ne_title not in titles:
                        titles.append(ne_title)
                        links.append(hreflink[0]['href'])
        return {"title": titles, 'link': links}

    def cineru_search(search):
        cineru_url = "https://cineru.lk/?s="
        url = cineru_url + search
        request_result = requests.get(url)
        soup = bs4.BeautifulSoup(request_result.text, "html.parser")
        site_items = soup.find_all('h2', {"class": "post-box-title"})

        links = []
        titles = []
        for x in range(len(site_items)):
            htmldata = str(site_items[x])
            page_soup1 = bs4.BeautifulSoup(htmldata, "html.parser")
            hreflink = page_soup1.findAll('a')
            search_list = search.split()
            cc = 1
            if len(hreflink) != 0:
                for key in range(len(search_list)):
                    if str(search_list[key]).lower() not in str(hreflink[0].getText().lower()):
                        cc = 0
                title = hreflink[0].getText()
                llink = hreflink[0]['href']
                if cc == 1 and 'tv_series/' not in llink:

                    try:
                        ne_title = title[:title.index(" | ")]
                    except:
                        ne_title = title
                    if ne_title not in titles:
                        titles.append(ne_title)
                        links.append(llink)
        return {"title": titles, 'link': links}

    def search_engine(search):
        search = search.lower()
        search = did_you(search, " subtitles")
        search = search.replace("(", " ").replace(")", " ")
        baiscopelk = baiscopelk_search(search)
        pirate = pirate_search(search)
        cineru = cineru_search(search)
        if len(baiscopelk['title']) > 3:
            return baiscopelk
        elif len(cineru['title']) > 3:
            return cineru
        elif len(pirate['title']) > 3:
            return pirate
        else:
            new_title = baiscopelk['title'] + pirate['title'] + cineru['title']
            new_link = baiscopelk['link'] + pirate['link'] + cineru['link']
            if len(new_title) > 0:
                return {'title': new_title, 'link': new_link}
            else:
                return "Not Result"
    return search_engine(Name)


# Download
def download(url):
    r1 = requests.get(url)
    html_data = r1.text
    soup = bs(html_data, 'html.parser')

    def cineru():
        links = soup.select('a[data-link]')
        try:
            for i in links:
                lin = str(i)
                link = lin[lin.index('data-link="') + 11:lin.index('" href')]
                return link
        except Exception as e:
            print(e)
            return "error"

    def baiscopelk():
        links = soup.find_all("p", {"style": "padding: 0px; text-align: center;"})
        try:
            for i in links:
                lin = str(i)
                link = lin[lin.index('<a href="') + 9:lin.index('"><img ')]
                return link
        except Exception as e:
            print(e)
            return "error"

    def piratelk():
        links = soup.find_all("a", {"class": "aligncenter download-button"})
        try:
            for i in links:
                lin = str(i)
                link = lin[lin.index('href="') + 6:lin.index('" rel')]
                return link
        except Exception as e:
            print(e)
            return "error"

    sites = ["https://cineru.lk", "https://www.baiscopelk.com", "https://piratelk.com"]
    if sites[0] in url:
        site_message = cineru()
    elif sites[1] in url:
        site_message = baiscopelk()
    else:
        site_message = piratelk()
    r3 = requests.get(site_message)
    sv = str(site_message)
    if sv[-1]=="/":
        sv = sv[:sv.rindex("/")]
    if r3.status_code == 200:
        if "rar/" in site_message:
            sv = sv.replace("rar/","")
            sv = sv[sv.rindex("/")+1:]
            file_name = sv+"@SinhalaSubDown_Bot.rar"
        else:
            sv = sv[sv.rindex("/")+1:]
            file_name = sv.replace(".zip","")+"@SinhalaSubDown_Bot.zip"
        file = open(file_name, "wb")
        file.write(r3.content)
        file.close()
        print("File download success !")
        print(file_name)
        doc = open(file_name, 'rb')
        return {'file': doc ,"name":file_name}