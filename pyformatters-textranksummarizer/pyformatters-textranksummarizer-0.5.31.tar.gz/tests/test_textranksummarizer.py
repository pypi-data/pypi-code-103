import json
from copy import deepcopy
from pathlib import Path

import pytest
from pyformatters_textranksummarizer.textranksummarizer import TextRankSummarizerFormatter, \
    TextRankSummarizerParameters, TextRankAlgo
from pymultirole_plugins.v1.schema import Document, DocumentList
from starlette.responses import Response


@pytest.mark.parametrize("algorithm", [a.value for a in TextRankAlgo])
def test_textranksummarizer_french(algorithm):
    parameters = TextRankSummarizerParameters(lang="fr", algo=algorithm)
    formatter = TextRankSummarizerFormatter()
    doc = Document(text="""Un nuage de fumée juste après l’explosion, le 1er juin 2019.
        Une déflagration dans une importante usine d’explosifs du centre de la Russie a fait au moins 79 blessés samedi 1er juin.
        L’explosion a eu lieu dans l’usine Kristall à Dzerzhinsk, une ville située à environ 400 kilomètres à l’est de Moscou, dans la région de Nijni-Novgorod.
        « Il y a eu une explosion technique dans l’un des ateliers, suivie d’un incendie qui s’est propagé sur une centaine de mètres carrés », a expliqué un porte-parole des services d’urgence.
        Des images circulant sur les réseaux sociaux montraient un énorme nuage de fumée après l’explosion.
        Cinq bâtiments de l’usine et près de 180 bâtiments résidentiels ont été endommagés par l’explosion, selon les autorités municipales. Une enquête pour de potentielles violations des normes de sécurité a été ouverte.
        Fragments de shrapnel Les blessés ont été soignés après avoir été atteints par des fragments issus de l’explosion, a précisé une porte-parole des autorités sanitaires citée par Interfax.
        « Nous parlons de blessures par shrapnel d’une gravité moyenne et modérée », a-t-elle précisé.
        Selon des représentants de Kristall, cinq personnes travaillaient dans la zone où s’est produite l’explosion. Elles ont pu être évacuées en sécurité.
        Les pompiers locaux ont rapporté n’avoir aucune information sur des personnes qui se trouveraient encore dans l’usine.
        """)
    resp: Response = formatter.format(doc, parameters)
    assert resp.status_code == 200
    assert resp.media_type == "text/plain"
    summary = resp.body.decode(resp.charset)

    parameters.as_metadata = "summary"
    docs = formatter.process([doc], parameters)
    summarized: Document = docs[0]
    assert summary == summarized.metadata['summary']

    parameters.as_metadata = None
    docs = formatter.process([doc], parameters)
    summarized: Document = docs[0]
    assert summary == summarized.text


def test_textranksummarizer_french_with_sents():
    testdir = Path(__file__).parent / 'data'
    json_file = testdir / "french.json"
    with json_file.open("r") as fin:
        doc = json.load(fin)
    doc = Document(**doc)
    ori_len = len(doc.text)
    parameters = TextRankSummarizerParameters(lang="fr", num_sentences=2)
    formatter = TextRankSummarizerFormatter()
    docs = formatter.process([doc], parameters)
    assert len(docs[0].text) < ori_len


def test_textranksummarizer_english():
    parameters = TextRankSummarizerParameters(num_sentences=2)
    formatter = TextRankSummarizerFormatter()
    doc = Document(text="""The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, and the tallest structure in Paris.
    Its base is square, measuring 125 metres (410 ft) on each side. During its construction, the Eiffel Tower surpassed the Washington Monument to become the tallest man-made structure in the world, a title it held for 41 years until the Chrysler Building in New York City was finished in 1930.
    It was the first structure to reach a height of 300 metres. Due to the addition of a broadcasting aerial at the top of the tower in 1957, it is now taller than the Chrysler Building by 5.2 metres (17 ft).
    Excluding transmitters, the Eiffel Tower is the second tallest free-standing structure in France after the Millau Viaduct.
        """)
    resp: Response = formatter.format(doc, parameters)
    assert resp.status_code == 200
    assert resp.media_type == "text/plain"
    summary = resp.body.decode(resp.charset)

    parameters.as_metadata = "summary"
    docs = formatter.process([doc], parameters)
    summarized: Document = docs[0]
    assert summary == summarized.metadata['summary']

    parameters.as_metadata = None
    docs = formatter.process([doc], parameters)
    summarized: Document = docs[0]
    assert summary == summarized.text


@pytest.mark.skip(reason="Not a test")
def test_textranksummarizer_kantar():
    testdir = Path(__file__).parent / 'data'
    json_file = testdir / "futilecyclingtxt-documents.json"
    with json_file.open("r") as fin:
        docs = json.load(fin)
    docs = [Document(**doc) for doc in docs]
    parameters = TextRankSummarizerParameters(num_sentences=2)
    formatter = TextRankSummarizerFormatter()
    # rows = []
    for doc in docs:
        resp: Response = formatter.format(doc, parameters)
        assert resp.status_code == 200
        summary = resp.body.decode(resp.charset)
        doc.metadata['summary'] = summary
        # rows.append({
        #     'Title': doc.title,
        #     'Content': doc.text,
        #     'Summary': summary
        # })
    # row_file = testdir / f"{json_file.stem}_{parameters.model.value.replace('/', '_')}.xlsx"
    # df = pd.DataFrame.from_records(rows)
    # df.to_excel(row_file)
    sum_file = testdir / f"{json_file.stem}_textrank.json"
    dl = DocumentList(__root__=docs)
    with sum_file.open("w") as fout:
        print(dl.json(exclude_none=True, exclude_unset=True, indent=2), file=fout)


def test_textranksummarizer_boerhinger():
    testdir = Path(__file__).parent / 'data'
    json_file = testdir / "stefantestmov22-document-33933676.txt.json"
    with json_file.open("r") as fin:
        doc = json.load(fin)
    ori_doc = Document(**doc)
    doc = deepcopy(ori_doc)
    ori_len = len(ori_doc.text)
    parameters = TextRankSummarizerParameters(num_sentences=2)
    formatter = TextRankSummarizerFormatter()
    docs = formatter.process([doc], parameters)
    sum1 = docs[0].text
    assert len(sum1) < ori_len
    doc = deepcopy(ori_doc)
    parameters.preserve_order = True
    docs = formatter.process([doc], parameters)
    sum2 = docs[0].text
    assert len(sum2) < ori_len
    assert sum1 != sum2
    assert len(sum1) == len(sum2)
