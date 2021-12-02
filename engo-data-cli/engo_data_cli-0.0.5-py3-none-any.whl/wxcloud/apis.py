import json
import re
from textwrap import dedent
import time
from typing import Dict, List

class CollectionMethod:
    def decode(self) -> str:
        return ''

class Query(json.JSONEncoder):
    env: str = ''
    collection:CollectionMethod

    def __init__(self, env, collection):
        self.env = env
        self.collection = collection

    def decode(self) -> str:
        result = dict()
        result['env'] = self.env
        result['query'] = self.collection.decode()
        return json.dumps(result)

class CollectionQuery(CollectionMethod):
    template: str = '''\
    db.collection(\"%s\").field({ %s: true }).where({%s: _.in([%s])}).limit(100).get()
    '''
    name: str = ''
    data: List = []
    field: str = ''

    def __init__(self, name: str, field: str):
        self.name = name
        self.field = field

    def decode(self) -> str:
        array = set(())
        for item in self.data:
            encoded = item.encode()
            section = encoded[self.field]
            array.add(f'\"{section}\"')
        template = dedent(self.template)
        template = template.strip()
        template = re.sub('\n', '', template)
        result = template % (self.name, self.field, self.field, str.join(',', array))
        return result

class CollectionAdd(CollectionMethod):
    template: str = '''\
    db.collection(\"%s\").add({
    data: [%s]
    })
    '''
    name: str = ''
    data: List = []

    def __init__(self, name: str):
        self.name = name

    def decode(self) -> str:
        array = set(())
        for item in self.data:
            encoded = item.encode()
            encoded = self.__escape_dict__(encoded)
            section = self.__deserialize__(encoded)
            array.add(section)

        template = dedent(self.template)
        template = template.strip()
        template = re.sub('\n', '', template)
        result = template % (self.name, str.join(',', array))
        return result

    def __deserialize__(self, d: Dict) -> str:
        result: list = []
        for key in d:
            if type(d[key]) == str:
                result.append(f'{key}: "{d[key]}"')
            elif type(d[key]) == time.struct_time:
                result.append(f'{key}: new Date("{time.strftime("%Y-%m-%d", d[key])}")')
            elif d[key] == True:
                result.append(f'{key}: true')
            elif d[key] == False:
                result.append(f'{key}: false')

        middle:str = ','.join(result)
        return '{'f'{middle}''}'

    def __escape_dict__(self, d: Dict) -> Dict:
        for key in d:
            if type(d[key]) == str:
                d[key] = self.__escape__(d[key])
        return d

    def __escape__(self, text: str) -> str:
        text = re.sub('\"', '&quot;', text)
        return text

    def size(self) -> int:
      return len(self.data)

class CollectionDelete(CollectionMethod):
    template: str = '''\
    db.collection(\"%s\").where({
      digest: _.in([%s])
    }).remove()
    '''
    name: str = ''
    data: List = []

    def __init__(self, name: str):
        self.name = name

    def decode(self) -> str:
        array: list = []
        for item in self.data:
            digest = item.digest
            array.append(f'\"{digest}\"')
            
        result = self.template % (self.name, str.join(',', array))
        return result

    def size(self) -> int:
      return len(self.data)

