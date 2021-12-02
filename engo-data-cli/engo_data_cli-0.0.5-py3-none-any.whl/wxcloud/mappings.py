from hashlib import md5
import re
import time
from typing import Dict

from bs4 import BeautifulSoup

class Model:
   title: str = ''
   content: str = ''
   html: str = ''
   has_chinese: int = False
   tag: str = ''
   audio_uri: str = ''
   when: str = ''
   digest: str = ''
   enabled: int = True

   def decode_from_webscraper(self, dict: Dict):
      self.title = dict['title']
      self.content = self.__layout__(dict['content'])
      self.html = dict['content']
      self.audio_uri = dict['audio-url-href']
      self.digest = md5(self.title.encode(encoding='utf-8')).hexdigest()
      m = re.search(r'(.+)\((\d+\/\d+\/\d+)\)', dict['navigation'])

      if m != None:
          self.when = m.groups()[1]

   def encode(self) -> Dict:
      d = dict()
      d['title'] = self.title
      d['content'] = self.content
      # d['html'] = self.html
      d['hasChinese'] = self.has_chinese
      d['tag'] = self.tag
      d['audioUri'] = self.audio_uri
      d['enabled'] = self.enabled
      d['digest'] = self.digest

      if self.when != '':
          d['when'] = time.strptime(self.when, '%Y/%m/%d')

      return d

   def __layout__(self, text: str) -> str:
      soup = BeautifulSoup(text, 'html.parser')
      self.__data_extract__(soup.select('.byline'))
      self.__data_extract__(soup.select('.datetime'))
      self.__data_extract__(soup.select('.contentImage'))
      self.__data_extract__(soup.select('br'))
      self.__data_extract__(soup.select('ins'))
      self.__data_extract__(soup.select('script'))
      self.__tag_replace__(soup.select('h2'), '\\\\n')
      self.__tag_replace__(soup.select('strong'))
      self.__tag_replace__(soup.select('p'), '\\\\n')
      self.__tag_replace__(soup.select('div'))
      self.__tag_replace__(soup.select('em'))
      self.__tag_replace__(soup.select('span'))
      
      html = soup.__str__()
      text = re.sub('\\n', '', html)
      text = re.sub('\\r', '', text)
      return text

   def __tag_replace__(self, tags, tail = ''):
       for tag in tags:
           text = tag.get_text() + tail
           tag.replace_with(text)

   def __data_extract__(self, tags):
      for tag in tags:
         tag.extract()

