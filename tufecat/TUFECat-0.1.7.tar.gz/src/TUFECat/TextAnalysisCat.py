# -*- coding: utf-8 -*-

import jieba
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from snownlp import sentiment
from snownlp import SnowNLP
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer
from gensim import corpora, models
import gensim


def draw_word_cloud(word):
    words = jieba.cut(word)
    wordstr = " ".join(words)
    sw = set(STOPWORDS)
    wc = WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf',  # 设置字体格式
        max_words=300,
        max_font_size=70,
        stopwords=sw,
        background_color='white',
        scale=20,
    ).generate(wordstr)
    # 显示词云图 
    plt.imshow(wc.recolor())
    plt.axis("off")
    plt.show()

def analysis_text_expression(text):
    s = SnowNLP(text)
    if s.sentiments <= 0.4: 
        commment = '表现为消极情绪倾向'
    elif s.sentiments > 0.4 and s.sentiments <= 0.6:
        commment = '表现为中立情绪倾向'
    else:
        commment = '表现为积极情绪倾向'
    print('该文本的情感倾向得分为：' ,s.sentiments,commment) 
    
def lda_model(text_url,num_topics=10,num_words=3):
    tokenizer = RegexpTokenizer(r'\w+')
    en_stop = get_stop_words('en')
    p_stemmer = PorterStemmer()
    with open(text_url, "r",encoding = 'utf-8') as f:
        text = f.read()
    doc_set = [text]
    texts = []

    for i in doc_set:
        raw = i.lower()
        tokens = tokenizer.tokenize(raw)
        stopped_tokens = [i for i in tokens if not i in en_stop]
        stemmed_tokens = [p_stemmer.stem(i) for i in stopped_tokens]
        texts.append(stemmed_tokens)

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics)
    for topic in lda.print_topics(num_topics=num_topics, num_words=num_words):
        print(topic)
    return lda

def keywords(text_url,num_keywords=10):
    with open(text_url, "r",encoding = 'utf-8') as f:
        text = f.read()
    text = SnowNLP(text)
    print(text.keywords(limit=num_keywords))
    
