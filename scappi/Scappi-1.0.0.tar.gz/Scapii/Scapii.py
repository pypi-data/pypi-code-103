'''
Scapii
Written by MrFluid [https://scratch.mit.edu/users/MrFluid]
'''

# -- Imports --
import json, requests, os
os.system('pip install scratchclient')
from scratchclient import ScratchSession as ss

os.system('clear')
print("For any help using Scapii, visit the Documentation, - https://github.com/kruffer/Scapii/blob/main/README.md")
print("+=====================================+")
print("Scapii Made by MrFluid")
print("Contact me @ https://scratch.mit.edu/users/MrFluid/")
print("+=====================================+")
print(" ")
print(" ")
print(" ")
# -- Functions --
def readURL(URL):
  return json.loads(requests.get(URL).text)

def readHTML(HTML):
  html = HTML
  while True:
    try:
      html = html.replace(html[html.index('<'):html.index('>') + 1],'').strip()
    except:
      break
  return html.split('\n')

class UserSession:
  def __init__(self, Username, Password):
    global Login
    self.session = ss(Username,Password)
    self.Username = Username
    Login = Username, Password
  def Comment(self, catagory = 'profile', location = 'MrFluid', comment = 'Follow MrFluid!'):
    if catagory.lower() == 'profile':
      self.session.get_user(location).post_comment(comment)
    elif catagory.lower() == 'project':
      self.session.get_project(location).post_comment(comment)
    elif catagory.lower() == 'studio':
      self.session.get_studio(location).post_comment(comment)
    else:
      raise('Invalid catagory')
  def Follow(self,username = 'MrFluid'):
    self.session.get_user(username).follow()
  def Unfollow(self,username = 'griffpatch'):
    self.session.get_user(username).unfollow()
  def Love(self, ProjectID = 000000000):
    self.session.get_project(ProjectID).love()
  def Favorite(self, ProjectID = 000000000):
    self.session.get_project(ProjectID).favorite()
  def Unlove(self, ProjectID = 000000000):
    self.session.get_project(ProjectID).unlove()
  def Unfavorite(self, ProjectID = 000000000):
    self.session.get_project(ProjectID).unfavorite()
  def ToggleProjectComments(self, ProjectID):
    self.session.get_project(ProjectID).toggle_commenting()
  def Share(self, ProjectID):
    self.session.get_project(ProjectID).share()
  def Unshare(self, ProjectID):
    self.session.get_project(ProjectID).unshare()
  def View(self, ProjectID):
    self.session.get_project(ProjectID).view()
  def SetThumbNail(self,ProjectID, filename):
    self.session.get_project(ProjectID).set_thumbnail(filename)
  def SetStudioDescription(self, StudioID, text):
    self.session.get_studio(StudioID).set_description(text)
  '''
  def ToggleComments(self):
    self.session.get_user(self.Username).toggle_commenting()
  def Report(self,username):
    self.session.get_user(username).report()
  def SetBio(self, bio = 'Follow @MrFluid!'):
    self.session.set_bio(bio)
  def SetWiwo(self, wiwo = 'Follow @MrFluid'):
    self.session.set_status(wiwo)
  def SetFeatured(self, ID):
    self.session.set_featured_project('',ID)
  '''
  class CloudSession:
    def __init__(self,ProjectID):
      global Login
      self.session = ss(Login[0],Login[1])
      self.connection = self.session.create_cloud_connection(ProjectID)
    def SetVar(self, VarName, VarValue):
      self.connection.set_cloud_variable(VarName,VarValue)
    def GetVar(self, VarName):
      return self.connection.get_cloud_variable(VarName)

class API:
  class Users:
    def __init__(self, User = None):
      if User != None:
        self.json1 = readURL(f'https://api.scratch.mit.edu/users/{User}')
        self.id = self.json1['id']
        self.username = self.json1['username']
        self.scratchteam = self.json1['scratchteam']
        self.join = self.json1['history']['joined']
        self.profile = self.json1['profile']
        self.images = self.profile['images']
        self.wiwo = self.profile['status']
        self.bio = self.profile['bio']
        self.country = self.profile['country']
        self.new = readURL(f'https://api.scratch.mit.edu/users/{self.username}/messages/count')['count']
        try:
          self.json2 = readURL(f'https://scratchdb.lefty.one/v2/user/info/{self.username}')
          self.status = self.json2['status']
          self.school = self.json2['school']
          self.statistics = self.json2['statistics']
          self.loves = self.statistics['loves']
          self.favorites = self.statistics['favorites']
          self.comments = self.statistics['comments']
          self.views = self.statistics['views']
          self.follows = self.statistics['followers']
          self.followed = self.statistics['following']
        except:
          pass
      else:
        pass
    def rank(self, country = False, category = 'followers'):
      if country == False:
        return self.statistics['ranks'][category]
      else:
        return self.statistics['ranks']['country'][category]
    def history(self, category = 'followers', amount = 30):
      return readURL(f'https://scratchdb.lefty.one/v3/user/graph/{self.username}/{category}?segment=1&range={str(amount - 1)}')
    def ranks(self, country = 'global', category = 'followers', page = 1):
      self.users = readURL(f'https://scratchdb.lefty.one/v3/user/rank/{country}/{category}/{str(int(page) - 1)}')
      self.names = []
      for user in self.users:
        self.names.append(user['username'])
      return self.names
    def projects(self, amount = 10):
      self.ids = []
      for self.page in range(amount):
        try:
          id = readURL(f'https://api.scratch.mit.edu/users/{self.username}/projects?offset={self.page}')[0]['id'] 
          if id != '':
            self.ids.append(id)
        except:
          break
      return self.ids
    def following(self, amount = 10):
      self.users = []
      for self.page in range(amount):
        try:
          user = readURL(f'https://api.scratch.mit.edu/users/{self.username}/following?offset={self.page}')[0]['username']
          if user != '':
            self.users.append(user)
        except:
          break
      return self.users
    def followers(self, amount = 10):
      self.users = []
      for self.page in range(amount):
        try:
          user = readURL(f'https://api.scratch.mit.edu/users/{self.username}/followers?offset={self.page}')[0]['username']
          if user != '':
            x = readURL(f'https://api.scratch.mit.edu/users/{user}')['username']
            self.users.append(user)
            print(x)
        except:
          break
      return self.users
    def favorited(self, amount = 10):
      self.ids = []
      for self.page in range(amount):
        try:
          id = readURL(f'https://api.scratch.mit.edu/users/{self.username}/favorites?offset={self.page}')[0]['id']
          if id != '':
            self.ids.append(id)
        except:
          break
      return self.ids
    def activity(self, amount = 10):
      self.contents = []
      self.text = requests.get(f'').text.split('</li>')
      for self.c in self.text:
        try:
          self.content = readHTML(self.c)
          self.action = self.content[1].strip()
          self.object = self.content[2].strip()
          self.time = str(self.content[3]).replace('\xa0',' ').strip()
          self.contents.append({'action':self.action, 'object':self.object, 'time':self.time})
        except:
          pass
      return self.contents

  class Projects:
    def __init__(self, ProjectID = None):
      if ProjectID != None:
        self.json1 = readURL(f'https://api.scratch.mit.edu/projects/{ProjectID}')
        self.id = self.json1['id']
        self.title = self.json1['title']
        self.notes = self.json1['description']
        self.instructions = self.json1['instructions']
        self.comments = self.json1['comments_allowed']
        self.author = self.json1['author']['username']
        self.images = self.json1['images']
        self.history = self.json1['history']
        self.created = self.history['created']
        self.modified = self.history['modified']
        self.shared = self.history['shared']
        self.stats = self.json1['stats']
        self.views = self.stats['views']
        self.loves = self.stats['loves']
        self.favorites = self.stats['favorites']
        self.remixes = self.stats['remixes']
        self.parent = self.json1['remix']['parent']
        self.root = self.json1['remix']['root']
        self.json2 = readURL(f'https://scratchdb.lefty.one/v3/project/info/{self.id}')
        try:
          self.statistics = self.json2['statistics']
          self.comments = self.statistics['comments']
          self.metadata = self.json2['metadata']
          self.costumes = self.metadata['costumes']
          self.blocks = self.metadata['blocks']
          self.variables = self.metadata['variables']
          self.assets = self.metadata['assets']
        except:
          pass
    def rank(self, catagory = 'views'):
      return self.statistics['ranks'][catagory]
    def ranks(self, catagory = 'views',page = 1):
      self.projects = readURL(f'https://scratchdb.lefty.one/v3/project/rank/{catagory}/{str(int(page) - 1)}')
      self.ids = []
      for self.project in self.projects:
        self.names.append(self.project['id'])
      return self.ids
    def remixed(self, amount = 10):
      self.ids = []
      for self.page in range(amount):
        try:
          self.ID = readURL(f'https://api.scratch.mit.edu/projects/{str(self.id)}/remixes?offset={str(self.page)}&limit=1')[0]['id']
          if self.ID != '':
            self.ids.append(self.ID)
        except:
          break
      return self.ids
      
  class Main:
    def __init__(self):
      self.health = readURL('https://api.scratch.mit.edu/health')
      self.news = readURL('https://api.scratch.mit.edu/news')
      self.front = readURL('https://api.scratch.mit.edu/proxy/featured')
      self.remixed = self.front['community_most_remixed_projects']
      self.loved = self.front['community_most_loved_projects']
      self.design = self.front['scratch_design_studio']
      self.curator = self.front['curator_top_projects']
      self.featured = self.front['community_featured_projects']
    def explore(self, catagory1 = 'Projects', catagory2 = 'trending', amount = 10):
      self.ids = []
      for self.page in range(amount):
        try:
          self.id = readURL(f'https://api.scratch.mit.edu/explore/{catagory1}/?mode={catagory2}&offset={self.page}')[0]['id']
          if self.id != '':
            self.ids.append(self.id)
        except:
          break
      return self.ids
    def search(self, catagory1 = 'projects',catagory2 = 'trending', search = 'MrFluid', amount = 10):
      self.ids = []
      for self.page in range(amount):
        try:
          self.id = readURL(f'https://api.scratch.mit.edu/search/{catagory1}/?q={search}&offset={self.page}&mode={catagory2}')[0]['id']
          if self.id != '':
            self.ids.append(self.id)
        except:
          break
      return self.ids














try:
    import re
    import os
    import logging
    import sys
    import websocket
except ModuleNotFoundError as e:
    print(e)
    os.chdir(os.getcwd())
    os.system('pip install -r requirements.txt')
try:
    ws = websocket.WebSocket()
except:
    os.system('pip install --force-reinstall websocket-client')
logging.basicConfig(filename='Scapii.log', level=logging.INFO)


class Scapii():
    def __init__(self, username, password):
        self.chars = """AabBCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789 -_`~!@#$%^&*()+=[];:'"\|,.<>/?}{"""
        global uname
        uname = username
        self.username = username
        self.password = password
        self.headers = {
            "x-csrftoken": "a",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
            "referer": "https://scratch.mit.edu",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
        try:
            data = json.dumps({
                "username": username,
                "password": password
            })
            request = requests.post(
                'https://scratch.mit.edu/login/', data=data, headers=self.headers)
            self.sessionId = re.search(
                '\"(.*)\"', request.headers['Set-Cookie']).group()
            self.token = request.json()[0]["token"]
            global sessionId
            sessionId = self.sessionId
            headers = {
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchlanguage=en;permissions=%7B%7D;",
                "referer": "https://scratch.mit.edu",
            }
            request = requests.get(
                "https://scratch.mit.edu/csrf_token/", headers=headers)
            self.csrftoken = re.search(
                "scratchcsrftoken=(.*?);", request.headers["Set-Cookie"]
            ).group(1)

        except AttributeError:
            sys.exit('Error: Invalid credentials. Authentication failed.')
        else:
            self.headers = {
                "x-csrftoken": self.csrftoken,
                "X-Token": self.token,
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken="
                + self.csrftoken
                + ";scratchlanguage=en;scratchsessionsid="
                + self.sessionId
                + ";",
                "referer": "",
            }

    def decode(self, text):
        decoded = ""
        text = str(text)
        y = 0
        for i in range(0, len(text)//2):
            x = self.chars[int(str(text[y])+str(text[int(y)+1]))-1]
            decoded = str(decoded)+str(x)
            y += 2
        return decoded

    def encode(self, text):
        encoded = ""
        length = int(len(text))
        for i in range(0,length):
            try:
                x = int(self.chars.index(text[i])+1)
                if x < 10:
                    x = str(0)+str(x)
                encoded = encoded + str(x)
            except ValueError:
                logging.error('Character not supported')
        return encoded
    class project:
        def __init__(self, id):
            self.id = id

        def getStats(self, stat):
            if stat == "loves" or stat == "faves" or stat == "views" or stat == "remixes":
                if stat == "loves":
                    r = requests.get(
                        "https://api.scratch.mit.edu/projects/"+str(self.id))
                    data = r.json()
                    return data['stats']['loves']
                else:
                    if stat == "faves":
                        r = requests.get(
                            "https://api.scratch.mit.edu/projects/"+str(self.id))
                        data = r.json()
                        return data['stats']['favorites']
                    else:
                        if stat == "remixes":
                            r = requests.get(
                                "https://api.scratch.mit.edu/projects/"+str(self.id))
                            data = r.json()
                            return data['stats']['remixes']
                        else:
                            if stat == "views":
                                r = requests.get(
                                    "https://api.scratch.mit.edu/projects/"+str(self.id))
                                data = r.json()
                                return data['stats']['views']

        def getComments(self):
            uname = requests.get(
                "https://api.scratch.mit.edu/projects/"+str(self.id)).json()
            if uname != {"code": "NotFound", "message": ""}:
                uname = uname['author']['username']
                data = requests.get("https://api.scratch.mit.edu/users/" +
                                    str(uname)+"/projects/"+str(self.id)+"/comments").json()
                comments = []
                if data != {"code": "ResourceNotFound", "message": "/users/"+str(uname)+"/projects/175/comments does not exist"} and data != {"code": "NotFound", "message": ""}:
                    x = ""
                    for i in data:
                        if "content" in i:
                            x = i['content']
                        else:
                            if "image" in i:
                                x = i['image']
                            else:
                                x = "None"
                        comments.append(
                            str('Username: '+str(uname))+(str(', Content: ')+str(x)))
                    return data

        def getInfo(self):
            r = requests.get(
                'https://api.scratch.mit.edu/projects/'+str(self.id)
            ).json()
            return r

        def fetchAssets(self, type='img'):
            '''
            You may have problems with fetching assets since some projects may not have any assets, or are fetched as binary code and not JSON
            '''

            r = json.loads(requests.get(
                'https://projects.scratch.mit.edu/'+str(self.id)
            ).text.encode('utf-8'))

            assets = []
            for i in range(len(r['targets'])):
                if type == 'img':
                    assets.append('https://cdn.assets.scratch.mit.edu/internalapi/asset/' +
                                  str(r['targets'][i]['costumes'][0]['md5ext'])+'/get')
                elif type == 'snd':
                    assets.append('https://cdn.assets.scratch.mit.edu/internalapi/asset/' +
                                  str(r['targets'][i]['sounds'][0]['md5ext'])+'/get')
            return assets

    class studioSession:
        def __init__(self, sid):
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }
            self.sid = sid

        def inviteCurator(self, user):
            self.headers["referer"] = (
                "https://scratch.mit.edu/studios/" + str(self.sid) + "/curators/")
            requests.put("https://scratch.mit.edu/site-api/users/curators-in/" +
                         str(self.sid) + "/invite_curator/?usernames=" + user, headers=self.headers)

        def addStudioProject(self, pid):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(pid)
            return requests.post("https://api.scratch.mit.edu/studios/"+str(self.sid)+"/project/"+str(pid), headers=self.headers)

        def postComment(self, content, parent_id="", commentee_id=""):
            self.headers['referer'] = (
                "https://scratch.mit.edu/studios/" +
                str(self.sid) + "/comments/"
            )
            data = {
                "commentee_id": commentee_id,
                "content": content,
                "parent_id": parent_id,
            }
            return requests.post(
                "https://scratch.mit.edu/site-api/comments/gallery/"
                + str(self.sid)
                + "/add/",
                headers=self.headers,
                data=json.dumps(data),
            )

        def getComments(self):
            r = requests.get(
                "https://api.scratch.mit.edu/studios/"+str(self.sid)+"/comments")
            data = r.json()
            comments = []
            for i in data:
                x = i['content']
                comments.append(x)
            return json.dumps(comments)

        def follow(self):
            self.headers['referer'] = "https://scratch.mit.edu/studios/" + \
                str(self.sid)
            return requests.put(
                "https://scratch.mit.edu/site-api/users/bookmarkers/"
                + str(self.sid)
                + "/remove/?usernames="
                + self.username,
                headers=self.headers,
            ).json()

        def unfollow(self):
            self.headers['referer'] = "https://scratch.mit.edu/studios/" + \
                str(self.sid)
            return requests.put(
                "https://scratch.mit.edu/site-api/users/bookmarkers/"
                + str(id)
                + "/remove/?usernames="
                + self.username,
                headers=self.headers,
            ).json()

    class projectSession:
        def __init__(self, pid):
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }
            self.pid = pid

        def share(self):
            self.headers["referer"] = (
                "https://scratch.mit.edu/projects/"+str(self.pid)
            )
            return requests.put("https://api.scratch.mit.edu/proxy/projects/"+str(self.pid)+"/share", headers=self.headers)

        def unshare(self):
            self.headers["referer"] = (
                "https://scratch.mit.edu/projects/"+str(self.pid)
            )
            return requests.put("https://api.scratch.mit.edu/proxy/projects/"+str(self.pid)+"/unshare", headers=self.headers)

        def favorite(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.post(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/favorites/user/"
                + self.username,
                headers=self.headers,
            ).json()

        def unfavorite(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.delete(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/favorites/user/"
                + self.username,
                headers=self.headers,
            ).json()

        def love(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.post(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/loves/user/"
                + self.username,
                headers=self.headers,
            ).json()

        def unlove(self):
            self.headers['referer'] = "https://scratch.mit.edu/projects/" + \
                str(self.pid)
            return requests.delete(
                "https://api.scratch.mit.edu/proxy/projects/"
                + str(self.pid)
                + "/loves/user/"
                + self.username,
                headers=self.headers,
            ).json()

    class userSession:
        def __init__(self, username):
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }
            self.username = uname
            self.uname2 = username

        def followUser(self):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + \
                str(self.username)+"/"
            return requests.put(
                "https://scratch.mit.edu/site-api/users/followers/"
                + self.username
                + "/add/?usernames="
                + self.uname2,
                headers=self.headers,
            ).json()

        def unfollowUser(self):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + \
                str(self.username)+"/"
            return requests.put(
                "https://scratch.mit.edu/site-api/users/followers/"
                + self.username
                + "/remove/?usernames="
                + self.uname2,
                headers=self.headers,
            ).json()

        def toggleCommenting(self):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + \
                str(self.username)
            return requests.post(
                "https://scratch.mit.edu/site-api/comments/user/" +
                str(self.username)+"/toggle-comments/",
                headers=self.headers,
            )

        def postComment(self,content, parent_id="", commentee_id=""):
            self.headers['referer'] = "https://scratch.mit.edu/users/" + self.uname2
            data = {
                'content': content,
                'parent_id': parent_id,
                'commentee_id': commentee_id
            }
            return requests.post("https://scratch.mit.edu/site-api/comments/user/"+ self.uname2 +"/add/",data=json.dumps(data),headers=self.headers).json()

    class user:
        def __init__(self, user):
            self.user = user
            self.headers = {
                "x-csrftoken": "a",
                "x-requested-with": "XMLHttpRequest",
                "Cookie": "scratchcsrftoken=a;scratchlanguage=en;",
                "referer": "https://scratch.mit.edu",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
            }

        def exists(self):
            return requests.get("https://api.scratch.mit.edu/accounts/checkusername/"+str(self.user)).json() == {"username": self.user, "msg": "username exists"}

        def getMessagesCount(self):
            self.headers['referer'] = "https://scratch.mit.edu"
            return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)+"/messages/count").json()['count']

        def getMessages(self):
            return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)+"/messages" + "/", headers=self.headers).json()

        def getStatus(self):
            return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)).json()['profile']['status']

        def getBio(self):
            return requests.get("https://api.scratch.mit.edu/users/"+str(self.user)).json()['profile']['bio']

        def getProjects(self):
            r = requests.get(
                "https://api.scratch.mit.edu/users/"+str(self.user)+"/projects")
            data = r.json()
            titles = []
            for i in data:
                x = i['title']
                y = i['id']
                titles.append('ID: ' + str(y))
                titles.append('Title: ' + str(x))
            return titles

    class scratchConnect:
        def __init__(self, pid):
            global ws
            global PROJECT_ID
            self.username = uname
            PROJECT_ID = pid
            ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+sessionId+';',
                       origin='https://scratch.mit.edu', enable_multithread=True)
            ws.send(json.dumps({
                'method': 'handshake',
                'user': self.username,
                'project_id': str(pid)
            }) + '\n')

        def setCloudVar(self, variable, value):
            try:
                ws.send(json.dumps({
                    'method': 'set',
                    'name': '☁ ' + variable,
                    'value': str(value),
                    'user': self.username,
                    'project_id': str(PROJECT_ID)
                }) + '\n')
            except BrokenPipeError:
                logging.error('Broken Pipe Error. Connection Lost.')
                ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+sessionId+';',
                           origin='https://scratch.mit.edu', enable_multithread=True)
                ws.send(json.dumps({
                    'method': 'handshake',
                    'user': self.username,
                    'project_id': str(PROJECT_ID)
                }) + '\n')
                logging.info('Re-connected to wss://clouddata.scratch.mit.edu')
                logging.info('Re-sending the data')
                ws.send(json.dumps({
                    'method': 'set',
                    'name': '☁ ' + variable,
                    'value': str(value),
                    'user': self.username,
                    'project_id': str(PROJECT_ID)
                }) + '\n')

        def readCloudVar(self, name, limit="1000"):
            try:
                resp = requests.get("https://clouddata.scratch.mit.edu/logs?projectid=" +
                                    str(PROJECT_ID)+"&limit="+str(limit)+"&offset=0").json()
                for i in resp:
                    x = i['name']
                    if x == ('☁ ' + str(name)):
                        return i['value']
            except:
                return 'Sorry, there was an error.'

    class scratchDatabase:
        def __init__(self, pid):
            self.chars = """AabBCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789 -_`~!@#$%^&*()+=[];:'"\|,.<>/?}{"""
            self.id = pid
            self.username = uname
            ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+sessionId+';',
                       origin='https://scratch.mit.edu', enable_multithread=True)
            ws.send(json.dumps({
                'method': 'handshake',
                'user': self.username,
                'project_id': str(self.id)
            }) + '\n')

        def __decode(self, text):
            decoded = ""
            text = str(text)
            y = 0
            for i in range(0, len(text)//2):
                x = self.chars[int(str(text[y])+str(text[int(y)+1]))-1]
                decoded = str(decoded)+str(x)
                y += 2
            return decoded

        def __encode(self, text):
            encoded = ""
            length = int(len(text))
            for i in range(0,length):
                try:
                    x = int(self.chars.index(text[i])+1)
                    if x < 10:
                        x = str(0)+str(x)
                    encoded = encoded + str(x)
                except ValueError:
                    logging.error('Character not supported')
            return encoded

        def __setCloudVar(self, variable, value):
            try:
                ws.send(json.dumps({
                    'method': 'set',
                    'name': '☁ ' + variable,
                    'value': str(value),
                    'user': self.username,
                    'project_id': str(self.id)
                }) + '\n')
            except BrokenPipeError:
                logging.error('Broken Pipe Error. Connection Lost.')
                ws.connect('wss://clouddata.scratch.mit.edu', cookie='scratchsessionsid='+sessionId+';',
                           origin='https://scratch.mit.edu', enable_multithread=True)
                ws.send(json.dumps({
                    'method': 'handshake',
                    'user': self.username,
                    'project_id': str(self.id)
                }) + '\n')
                logging.info('Re-connected to wss://clouddata.scratch.mit.edu')
                logging.info('Re-sending the data')
                ws.send(json.dumps({
                    'method': 'set',
                    'name': '☁ ' + variable,
                    'value': str(value),
                    'user': self.username,
                    'project_id': str(self.id)
                }) + '\n')

        def __readCloudVar(self, name, limit="1000"):
            try:
                resp = requests.get("https://clouddata.scratch.mit.edu/logs?projectid=" +
                                    str(self.id)+"&limit="+str(limit)+"&offset=0").json()
                for i in resp:
                    x = i['name']
                    if x == ('☁ ' + str(name)):
                        return i['value']
            except json.decoder.JSONDecodeError:
                resp = requests.get("https://clouddata.scratch.mit.edu/logs?projectid=" +
                                    str(self.id)+"&limit="+str(limit)+"&offset=0").json()
                for i in resp:
                    x = i['name']
                    if x == ('☁ ' + str(name)):
                        return i['value']

        def startLoop(self):
            data = []
            while True:
                encodedMethod = self.__readCloudVar('Method')
                if encodedMethod != None:
                    Method = self.__decode(encodedMethod)
                if Method == "set":
                    encodedSend = self.__readCloudVar('Send')
                    Send = str(self.__decode(encodedSend))
                    encodedVal = self.__readCloudVar('Data')
                    Val = str(self.__decode(encodedVal))
                    print(Val)
                    intVal = self.__decode(encodedVal)
                    c = 0
                    for i in Send:
                        if str(i) in "1234567890":
                            c = int(c)+1
                    if c == len(Send):
                        if int(Send) > len(data):
                            if int(Send) == int(len(data))+1:
                                data.append(intVal)
                                logging.info('Data added.')
                                tosend = self.__encode('Data added.')
                                self.__setCloudVar('Return', tosend)
                                self.__setCloudVar('Method', '')
                            else:
                                while len(data) != int(Send)-1:
                                    data.append('none')
                                data.append(intVal)
                                logging.info('Data added.')
                                tosend = self.__encode('Data added.')
                                self.__setCloudVar('Return', tosend)
                                self.__setCloudVar('Method', '')
                        else:
                            data.pop(int(Send)-1)
                            data.insert(int(Send), intVal)
                            logging.info('Data added.')
                            tosend = self.__encode('Data added.')
                            self.__setCloudVar('Return', tosend)
                            self.__setCloudVar('Method', '')
                    else:
                        tosend = self.__encode(
                            'Invalid input. Variable name must be int.')
                        self.__setCloudVar('Return', tosend)
                if Method == "get":
                    encodedSend = self.__readCloudVar('Send')
                    Send = self.__decode(encodedSend)
                    c = 0
                    for i in Send:
                        if str(i) in "1234567890":
                            c = int(c)+1
                    if c == len(Send) and int(Send) > 0 and int(Send) < int(len(data))+1:
                        tosend = self.__encode(data[int(Send)-1])
                        self.__setCloudVar('Return', tosend)
                        logging.info('Data sent.')
                        self.__setCloudVar('Method', '')
                    else:
                        tosend = self.__encode('Invalid input.')
                        self.__setCloudVar('Return', tosend)
                if Method == "delete":
                    encodedSend = self.__readCloudVar('Send')
                    Send = self.__decode(encodedSend)
                    c = 0
                    for i in Send:
                        if str(i) in "1234567890":
                            c = int(c)+1
                    if c == len(Send) and int(Send) > 0 and int(Send) < int(len(data))+1:
                        data.pop(int(Send)-1)
                        data.insert(int(Send)-1, 'none')
                        logging.info('Variable deleted.')
                        tosend = self.__encode('Variable deleted.')
                        self.__setCloudVar('Return', tosend)
                    else:
                        tosend = self.__encode('Invalid input.')
                        self.__setCloudVar('Return', tosend)

    class turbowarpDatabase:
        def __init__(self, pid):
            self.chars = """AabBCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789 -_`~!@#$%^&*()+=[];:'"\|,.<>/?}{"""
            self.id = pid
            self.username = uname
            ws.connect('wss://clouddata.turbowarp.org',
                       origin='https://turbowarp.org', enable_multithread=True)
            ws.send(json.dumps({
                'method': 'handshake',
                'user': self.username,
                'project_id': str(self.id)
            }) + '\n')

        def __decode(self, text):
            decoded = ""
            text = str(text)
            y = 0
            for i in range(0, len(text)//2):
                x = self.chars[int(str(text[y])+str(text[int(y)+1]))-1]
                decoded = str(decoded)+str(x)
                y += 2
            return decoded

        def __encode(self, text):
            encoded = ""
            length = int(len(text))
            for i in range(0,length):
                try:
                    x = int(self.chars.index(text[i])+1)
                    if x < 10:
                        x = str(0)+str(x)
                    encoded = encoded + str(x)
                except ValueError:
                    logging.error('Character not supported')
            return encoded

        def __readCloudVar(self, variable):
            ws.send(json.dumps({
                'method': 'get',
                'project_id': str(turbowarpid)
            }) + '\n')
            data = ws.recv()
            data = data.split('\n')
            result = []
            for i in data:
                result.append(json.loads(i))
            for i in result:
                if i['name'] == '☁ ' + variable:
                    return i['value']

        def __setCloudVar(self, variable, value):
            ws.send(json.dumps({
                'method': 'set',
                'name': '☁ ' + variable,
                'value': str(value),
                'user': self.username,
                'project_id': str(turbowarpid)
            }) + '\n')

        def __readCloudVar(self, name, limit="1000"):
            try:
                resp = requests.get("https://clouddata.scratch.mit.edu/logs?projectid=" +
                                    str(self.id)+"&limit="+str(limit)+"&offset=0").json()
                for i in resp:
                    x = i['name']
                    if x == ('☁ ' + str(name)):
                        return i['value']
            except json.decoder.JSONDecodeError:
                resp = requests.get("https://clouddata.scratch.mit.edu/logs?projectid=" +
                                    str(self.id)+"&limit="+str(limit)+"&offset=0").json()
                for i in resp:
                    x = i['name']
                    if x == ('☁ ' + str(name)):
                        return i['value']

        def startLoop(self):
            data = []
            while True:
                encodedMethod = self.__readCloudVar('Method')
                if encodedMethod != None:
                    Method = self.__decode(encodedMethod)
                if Method == "set":
                    encodedSend = self.__readCloudVar('Send')
                    Send = str(self.__decode(encodedSend))
                    encodedVal = self.__readCloudVar('Data')
                    Val = str(self.__decode(encodedVal))
                    print(Val)
                    intVal = self.__decode(encodedVal)
                    c = 0
                    for i in Send:
                        if str(i) in "1234567890":
                            c = int(c)+1
                    if c == len(Send):
                        if int(Send) > len(data):
                            if int(Send) == int(len(data))+1:
                                data.append(intVal)
                                logging.info('Data added.')
                                tosend = self.__encode('Data added.')
                                self.__setCloudVar('Return', tosend)
                                self.__setCloudVar('Method', '')
                            else:
                                while len(data) != int(Send)-1:
                                    data.append('none')
                                data.append(intVal)
                                logging.info('Data added.')
                                tosend = self.__encode('Data added.')
                                self.__setCloudVar('Return', tosend)
                                self.__setCloudVar('Method', '')
                        else:
                            data.pop(int(Send)-1)
                            data.insert(int(Send), intVal)
                            logging.info('Data added.')
                            tosend = self.__encode('Data added.')
                            self.__setCloudVar('Return', tosend)
                            self.__setCloudVar('Method', '')
                    else:
                        tosend = self.__encode(
                            'Invalid input. Variable name must be int.')
                        self.__setCloudVar('Return', tosend)
                if Method == "get":
                    encodedSend = self.__readCloudVar('Send')
                    Send = self.__decode(encodedSend)
                    c = 0
                    for i in Send:
                        if str(i) in "1234567890":
                            c = int(c)+1
                    if c == len(Send) and int(Send) > 0 and int(Send) < int(len(data))+1:
                        tosend = self.__encode(data[int(Send)-1])
                        self.__setCloudVar('Return', tosend)
                        logging.info('Data sent.')
                        self.__setCloudVar('Method', '')
                    else:
                        tosend = self.__encode('Invalid input.')
                        self.__setCloudVar('Return', tosend)
                if Method == "delete":
                    encodedSend = self.__readCloudVar('Send')
                    Send = self.__decode(encodedSend)
                    c = 0
                    for i in Send:
                        if str(i) in "1234567890":
                            c = int(c)+1
                    if c == len(Send) and int(Send) > 0 and int(Send) < int(len(data))+1:
                        data.pop(int(Send)-1)
                        data.insert(int(Send)-1, 'none')
                        logging.info('Variable deleted.')
                        tosend = self.__encode('Variable deleted.')
                        self.__setCloudVar('Return', tosend)
                    else:
                        tosend = self.__encode('Invalid input.')
                        self.__setCloudVar('Return', tosend)

    class turbowarpConnect:
        def __init__(self, pid):
            global ws
            global turbowarpid
            self.username = uname
            turbowarpid = pid
            ws.connect('wss://clouddata.turbowarp.org',
                       origin='https://turbowarp.org', enable_multithread=True)
            ws.send(json.dumps({
                'method': 'handshake',
                'user': self.username,
                'project_id': str(turbowarpid)
            }) + '\n')

        def setTurbowarpVar(self, variable, value):
            ws.send(json.dumps({
                'method': 'set',
                'name': '☁ ' + variable,
                'value': str(value),
                'user': self.username,
                'project_id': str(turbowarpid)
            }) + '\n')

        def readTurbowarpVar(self, variable):
            ws.send(json.dumps({
                'method': 'get',
                'project_id': str(turbowarpid)
            }) + '\n')
            data = ws.recv()
            data = data.split('\n')
            result = []
            for i in data:
                result.append(json.loads(i))
            for i in result:
                if i['name'] == '☁ ' + variable:
                    return i['value']
            return 'Variable not found.'