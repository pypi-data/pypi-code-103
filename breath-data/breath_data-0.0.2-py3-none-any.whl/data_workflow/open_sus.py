import sys
import pandas as pd

def loadcsv() -> pd.DataFrame:
    srag_2013 = pd.read_csv(
        "https://opendatasus.saude.gov.br/dataset/e6b03178-551c-495c-9935-adaab4b2f966/resource/4919f202-083a-4fac-858d-99fdf1f1d765/download/influd13_limpo_final.csv",
        sep=';', encoding='cp1252', dtype=str)
    srag_2014 = pd.read_csv(
        "https://opendatasus.saude.gov.br/dataset/e6b03178-551c-495c-9935-adaab4b2f966/resource/2182aff1-4e8b-4aee-84fc-8c9f66378a2b/download/influd14_limpo-final.csv",
        sep=';', encoding='cp1252', dtype=str)
    srag_2015 = pd.read_csv(
        "https://opendatasus.saude.gov.br/dataset/e6b03178-551c-495c-9935-adaab4b2f966/resource/97cabeb6-f09e-47a5-8358-4036fb10b535/download/influd15_limpo-final.csv",
        sep=';', encoding='cp1252', dtype=str)
    srag_2016 = pd.read_csv(
        "https://opendatasus.saude.gov.br/dataset/e6b03178-551c-495c-9935-adaab4b2f966/resource/dbb0fd9b-1345-47a5-86db-d3d2f4868a11/download/influd16_limpo-final.csv",
        sep=';', encoding='cp1252', dtype=str)
    srag_2017 = pd.read_csv(
        "https://opendatasus.saude.gov.br/dataset/e6b03178-551c-495c-9935-adaab4b2f966/resource/aab28b3c-f6b8-467f-af0b-44889a062ac6/download/influd17_limpo-final.csv",
        sep=';', encoding='cp1252', dtype=str)
    srag_2018 = pd.read_csv(
        "https://opendatasus.saude.gov.br/dataset/e6b03178-551c-495c-9935-adaab4b2f966/resource/a7b19adf-c6e6-4349-a309-7a1ec0f016a4/download/influd18_limpo-final.csv",
        sep=';', encoding='cp1252', dtype=str)
    srag_201314 = srag_2013.merge(srag_2014, how='outer')
    srag_20131415 = srag_201314.merge(srag_2015, how='outer')
    srag_2013141516 = srag_20131415.merge(srag_2016, how='outer')
    srag_201314151617 = srag_2013141516.merge(srag_2017, how='outer')
    srag_20131415161718 = srag_201314151617.merge(srag_2018, how='outer')
    return srag_20131415161718
