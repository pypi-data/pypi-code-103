from nltk.probability import FreqDist
import matplotlib.pyplot as plt
__stop_words__ = ""

with open(__file__.replace("tools.py","stop_words.txt"), encoding='utf-8') as f:
    __stop_words__ = f.read().splitlines()




def get_frecuency(dataset):
    """provides a list with all the countries that currently have media outlets in Sun

    Returns:
        [string]: [country_name]
    """
    textos=dataset["text"].values
    concatenado = ' '.join(textos.ravel())
    tokenizado = concatenado.split(" ")
    qty_elements = len(tokenizado)
    tokenized_no_stopwords= [token for token in tokenizado if token not in __stop_words__]
    freq_dictionary = FreqDist(tokenized_no_stopwords)
    return {"total_elements": qty_elements, "dictionary": freq_dictionary}

def get_n_most_freq(freq_struct, n, graph=False):
    """provides a list with all the countries that currently have media outlets in Sun

    Returns:
        [string]: [country_name]
    """
    dict_orders = sorted(freq_struct["dictionary"].items(), key=lambda x: x[1], reverse=True)
    if graph:
        
        x = [x[0] for x in dict_orders[:n]]
        y = [x[1]/freq_struct["total_elements"] for x in dict_orders[:n]]
        plt.bar(x,y)
        plt.title("term frecuency top %i words" %(n))
    return dict_orders[:n]

def add_stop_word(word):
    __stop_words__.append(word)

def graph_term_frecuency_bar(freq_struct, words):
    y = []
    for word in words:
        y.append(freq_struct["dictionary"][word]/freq_struct["total_elements"])
    plt.bar(words,y)
    ("term frecuency bar graph")

#def graph_fusionated_term_frecuency_bar(freq_struct, words):

def group_by_date(dataset, granularity="month"):
    if granularity == "month":
        return dataset.groupby(by=["month","year"])
    if granularity == "year":
        return dataset.groupby(by=["year"])
    if granularity == "day":
        return dataset.groupby(by=["date"])
    
def build_sophia2_ngram_struct(dataset1,granularity="month"):
    dataset=dataset1.copy()
    gb_dataset=group_by_date(dataset, granularity)
    sophia2_ngram_struct = {}
    if granularity == "day":
        for key, ds in gb_dataset:
            sophia2_ngram_struct[key.strftime("%Y/%m/%d")] = get_frecuency(ds)
    elif granularity == "month":
        for (month,year), ds in gb_dataset:
            sophia2_ngram_struct[(str(year)+"/"+str(month))] = get_frecuency(ds)
    elif granularity == "year":
        for year, ds in gb_dataset:
            sophia2_ngram_struct[str(year)] = get_frecuency(ds)
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
        plt.title("Sophia NGramViewer")
        if(annotate):
            for xy in zip(keys, ngram_dictionary[palabra]):                                       # <--
                plt.annotate('%s' % xy[1], xy=xy, textcoords='data')
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Apariciones', fontsize=12)