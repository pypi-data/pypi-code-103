from os import getenv
import pandas as pd
import mariadb
import sys
from elasticsearch import Elasticsearch
import spacy
nlp = spacy.load('es_core_news_md', disable=['parser','ner','textcat','...'] )



columns = ['id', 'country', 'media_outlet', 'url', 'title', 'text', 'date', 'year', 'journalist', 'month']

sql_vars={
    "__username__":"",
    "__password__": "",
    "__cursor__":None,
    "__host__": "",
    "__port__": "",
    "__database__":"Sun"

}

elastic_vars = {
    "__ip__" : "45.56.113.162",
    "__port__": 9200,
    "__es__": Elasticsearch(
        "45.56.113.162",
        port=9200,
        )
    
}

############ 0 LOGGING #############
def set_elastic_vars(__ip__=None, __port__=None):
    """[summary]

    Args:
        username (str, optional): [description]. Defaults to "sophia2api".
        password (str, optional): [description]. Defaults to "".
    """
    arguments=locals()
    has_changed=False
    global elastic_vars
    for a,b in arguments.items():
        if (b is not None):
            elastic_vars[a]=b
            has_changed=True
    if has_changed:
        elastic_vars["__es__"] = Elasticsearch(
            elastic_vars["__ip__"],
            port=elastic_vars["__port__"],
        )
    return 1

def set_sql_vars(__username__="sophia2api", __password__="", __host__="45.56.109.120", __port__=14096, __database__="Sun"):
    """[summary]

    Args:
        __username__ (str, optional): [description]. Defaults to "sophia2api".
        __password__ (str, required): [description]. Defaults to "".
        __host__ (str, optional): [description]. Defaults to "45.79.130.8".
        __port__ (int, optional): [description]. Defaults to 14096.
        __database__ (str, optional): [description]. Defaults to "Sun".
    """
    arguments=locals()
    global sql_vars

    for a,b in arguments.items():
        if (b is not None):
            sql_vars[a]=b
    
    return connect_sun()

def connect_sun():
    """[summary]
    Returns:
        [type]: [description]
    """
    global sql_vars
    try:
        conn = mariadb.connect(
            user=sql_vars["__username__"],
            password=sql_vars["__password__"],
            host=sql_vars["__host__"],
            port=sql_vars["__port__"],
            database=sql_vars["__database__"]
        )
        sql_vars["__cursor__"] = conn.cursor()
        return "successful connection"
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return "connection could not be established"

def __connection_validator():
    if sql_vars["__cursor__"] is None: sys.exit("connect to the database first with: db.set_credentials(password)")

############ 1 INFO #############

def list_countries():
    """provides a list with all the countries that currently have media outlets in Sun

    Returns:
        [string]: [country_name]
    """
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT DISTINCT country FROM news")
    return [x[0] for x in sql_vars["__cursor__"].fetchall()]

def list_media_outlets(countries=["all"]): 
    pd.set_option("display.max_rows",None)
    __connection_validator()
    if "all" in countries: countries=list_countries()
    media_outlets=[]
    for country in countries:
        sql_vars["__cursor__"].execute("SELECT DISTINCT media_outlet FROM news WHERE country=?",(country,))
        for media_outlet in sql_vars["__cursor__"].fetchall():
            media_outlets.append((country, media_outlet[0]))
    return pd.DataFrame(media_outlets,columns=["country", "media_outlet_name"])


def stats_countries():
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT country, count(id) FROM news GROUP BY country")
    return pd.DataFrame(sql_vars["__cursor__"].fetchall(),columns=["country", "quantity"])
    

def stats_countries_by_date(_from, _to):
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT country, count(id) FROM news WHERE date >= ? AND date <= ? GROUP BY country",(_from,_to))
    return pd.DataFrame(sql_vars["__cursor__"].fetchall(),columns=["country", "quantity"])
    

def stats_media_outlet():
    pd.set_option("display.max_rows",None)
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT country, media_outlet, count(id) FROM news GROUP BY media_outlet")
    return pd.DataFrame(sql_vars["__cursor__"].fetchall(),columns=["country", "media_outlet_name", "quantity"])

def stats_media_outlet_by_country(country='chile'):
    pd.set_option("display.max_rows",None)
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT country, media_outlet, count(id) FROM news WHERE country = ? GROUP BY media_outlet",(country,))
    return pd.DataFrame(sql_vars["__cursor__"].fetchall(),columns=["country", "media_outlet_name", "quantity"])

def stats_media_outlet_by_country_by_date(country='chile'): #por desarrollar
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT country, media_outlet, count(id) FROM news WHERE country = ? GROUP BY media_outlet",(country,))
    return pd.DataFrame(sql_vars["__cursor__"].fetchall(),columns=["country", "media_outlet_name", "quantity"])


############ 2 DATASETS #############

def last_n(n=1):
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT *, month(date) as month FROM news ORDER BY ID DESC LIMIT ?" , (n,))
    return pd.DataFrame(sql_vars["__cursor__"].fetchall(), columns=columns)

def get_dataset(keyword, country, from_, to_):
    global elastic_vars
    query = {
        "query": { 
            "bool": {
                "must": [{
                    "match": {
                        "text":keyword
                        }
                    }],
                "filter":[
                    {"range":{
                        "date":{
                            "gte": from_,
                            "lt": to_
                            }
                        }
                    },
                    {"term":{
                        "country": country
                        }
                    }
                    ]
                }
            }
        }
    res = elastic_vars["__es__"].search(index="news", body=query, size=10000)
    print("Son %d noticias encontradas..." % res['hits']['total']['value'])
    
    data = {'id_news':[],'country':[],'media_outlet':[],'url':[],'title':[],'text':[],'date':[],'search':[]}
    df = pd.DataFrame(data)
    
    for hit in res['hits']['hits']:
        id_news = hit['_source']['id_news']
        country = hit['_source']['country']
        media_outlet = hit['_source']['media_outlet']
        url = hit['_source']['url']
        title = hit['_source']['title']
        text = hit['_source']['text']
        date = hit['_source']['date']
        search = keyword
    
        new_row = {'id_news':id_news, 'country':country, 'media_outlet':media_outlet, 'url':url, 'title':title, 'text':text, 'date':date, 'search':search}
    
        df = df.append(new_row, ignore_index=True)
    
    return df
    
    
    
    
    
    
    
'''def dataset_by_country(country, _from, _to):
    __connection_validator()
    sql_vars["__cursor__"].execute("SELECT *, month(date) as month FROM news WHERE date >= ? AND date <= ? AND country = ?", (_from, _to, country))
    sophia_dataframe= pd.DataFrame(sql_vars["__cursor__"].fetchall(), columns=columns)
    to_return=sophia_dataframe.astype({"year": "Int64"})
    del sophia_dataframe
    return to_return 

def load_dataset():
		data = {'id':[1,2], 
                'country':['chile','france'],
'media_outlet':['latercera','mediapart'], 'url':['www','www'], 
'title':['un titulo','un titre'], 
'text':['un texto','un texte'], 
'date':['2020-01-01','2020-01-02']}
		df = pd.DataFrame(data=data)
		return df
'''
#save on js? as parameter of load or another function especially for download?
#if __username__ is None: set_credentials()