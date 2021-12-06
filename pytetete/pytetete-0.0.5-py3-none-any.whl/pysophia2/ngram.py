import numpy as np
from spacy import load as LOAD
from spacy.matcher import Matcher
from collections import Counter
import matplotlib.pyplot as plt

nlp = LOAD('es_core_news_md', disable=['parser','ner','textcat','...'] )
matcher = Matcher(nlp.vocab)

pattern_1 = [{"POS": "NOUN"},{"LOWER": "de"}, {"POS": "NOUN"}]
pattern_2 = [{"POS": "NOUN"}, {"POS": "ADJ"}]

matcher.add("NOUN-de-NOUN", [pattern_1])
matcher.add("NOUN-ADJ", [pattern_2])


def get_keywords(dataFrame):
    new_row=np.zeros(len(dataFrame.index))
    dataFrame['keywords']=new_row
    for index,rows in dataFrame.iterrows():
        text=rows["text"]
        filteredText=''.strip()
        tokens = nlp(text)
        '''tokens = [token
                 for token in tokens
                 if not token.is_stop and not token.is_punct]'''
        for token in tokens:
            if token.pos_ == "NOUN" :
                filteredText=filteredText+str(token.text.lower().strip())+","
                
        matches = matcher(tokens)
        for mach_id, start, end in matches:
            span = tokens[start:end]
            filteredText=filteredText+str(span.text.lower().strip())+","
        dataFrame.loc[index,'keywords']=filteredText
        
def get_frequency(df):
    if "keywords" not in df:
        get_keywords(df)
    concept_freq_total=Counter({})

    for index, row in df.iterrows():
        arreglo=row["keywords"].split(",")
        arreglo.pop()
        concept_freq = Counter(arreglo)
        concept_freq_total = concept_freq_total + concept_freq
    return {"total_elements": sum(concept_freq_total.values()), "dictionary": concept_freq_total}

def group_by_date(dataset, granularity="month"):
    if granularity == "month":
        return dataset.groupby(by=["month","year"])
    if granularity == "year":
        return dataset.groupby(by=["year"])
    if granularity == "day":
        return dataset.groupby(by=["date"])
    
    
def build_sophia2_ngram_struct(dataset1,granularity="month"):
    if "keywords" not in dataset1:
        get_keywords(dataset1)
    dataset=dataset1.copy()
    dataset["month"]=dataset['date'].apply(lambda x: x.split("-")[1])
    dataset["year"]=dataset['date'].apply(lambda x: x.split("-")[0])
    gb_dataset=group_by_date(dataset, granularity)
    sophia2_ngram_struct = {}
    if granularity == "day":
        for key, ds in gb_dataset:
            sophia2_ngram_struct[key.strftime("%Y/%m/%d")] = get_frequency(ds)
    elif granularity == "month":
        for (month,year), ds in gb_dataset:
            sophia2_ngram_struct[(str(year)+"/"+str(month))] = get_frequency(ds)
    elif granularity == "year":
        for year, ds in gb_dataset:
            sophia2_ngram_struct[str(year)] = get_frequency(ds)
    else: return "Wrong granularity parameter, please use 'day', 'month' or 'year' as granularity parameter instead of "+granularity
    
    return sophia2_ngram_struct

def sophia_ngram_view(struct, words, annotate):
    ngram_dictionary={}
    for palabra in words:
        ngram_dictionary[palabra]=[]
        keys=[]
        for key in struct:
            keys.append(key)
            ngram_dictionary[palabra].append(struct[key]["dictionary"][palabra])
        plt.plot(keys,ngram_dictionary[palabra],label=palabra)
        plt.legend(loc=5, bbox_to_anchor=(1.3, 0.5), fancybox=True, shadow=True )
        plt.title("PySophia NGramViewer")
        if(annotate):
            for xy in zip(keys, ngram_dictionary[palabra]):                                       # <--
                plt.annotate('%s' % xy[1], xy=xy, textcoords='data')
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Apariciones', fontsize=12)
    
    
def get_n_most_freq(freq_struct, n, graph=False):
    '''provides a list with all the countries that currently have media outlets in Sun

    Returns:
        [string]: [country_name]
    '''
    dict_orders = sorted(freq_struct["dictionary"].items(), key=lambda x: x[1], reverse=True)
    if graph:
        
        x = [x[0] for x in dict_orders[:n]]
        y = [x[1]/freq_struct["total_elements"] for x in dict_orders[:n]]
        plt.bar(x,y)
        plt.title("term frequency top %i words" %(n))
    return dict_orders[:n]


