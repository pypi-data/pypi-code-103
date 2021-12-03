#!/usr/bin/env python
# -*-coding:utf-8-*-


from my_python_module.nlp.corpus import laozi
from simple_nltk import FreqDist
from my_python_module.nlp.chinese_stop_words import STOP_WORDS
from my_python_module.nlp.utils import is_empty_string



def test_load_corpora():
    t = FreqDist(
        [i for i in laozi if (i not in STOP_WORDS and not is_empty_string(i))])

    assert t.most_common(50)[0][0] == '不'
