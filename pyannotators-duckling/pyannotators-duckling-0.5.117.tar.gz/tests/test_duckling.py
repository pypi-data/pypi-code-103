from datetime import datetime
from typing import List
from pyannotators_duckling.duckling import DucklingAnnotator, DucklingParameters, get_context
from pymultirole_plugins.v1.schema import Document


def test_duckling():
    model = DucklingAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == DucklingParameters
    annotator = DucklingAnnotator()
    parameters = DucklingParameters()
    docs: List[Document] = annotator.annotate([Document(
        text="Aujourd'hui nous sommes quelle date? Le 1er Juillet 2021, OK alors tu me dois 15 euros et 50 cts!",
        metadata=parameters.dict())], parameters)
    doc0 = docs[0]
    assert len(doc0.annotations) == 3
    ann0 = doc0.annotations[0]
    ann1 = doc0.annotations[1]
    ann2 = doc0.annotations[2]
    assert ann0.label == 'time'
    assert ann0.properties['grain'] == 'day'
    assert ann1.label == 'time'
    assert ann1.properties['grain'] == 'day'
    dt = datetime.fromisoformat(ann1.properties['value'])
    assert dt.day == 1
    assert dt.month == 7
    assert dt.year == 2021
    assert ann2.label == 'amount-of-money'
    assert ann2.properties['value'] == 15.5
    assert ann2.properties['unit'] == 'EUR'
    annotator2 = DucklingAnnotator()
    parameters2 = DucklingParameters(lang='en')
    docs: List[Document] = annotator2.annotate([Document(
        text="Aujourd'hui nous sommes quelle date? Le 1er Juillet 2021, OK alors tu me dois 15 euros et 50 cts!",
        metadata=parameters.dict())], parameters2)


def test_cached_context():
    parameters1 = DucklingParameters(lang='fr')
    context1 = get_context(parameters1.time_zone, parameters1.lang, parameters1.locale)
    parameters2 = DucklingParameters(lang='fr')
    context2 = get_context(parameters2.time_zone, parameters2.lang, parameters2.locale)
    assert id(context2) == id(context1)
    parameters3 = DucklingParameters(lang='en')
    context3 = get_context(parameters3.time_zone, parameters3.lang, parameters3.locale)
    assert id(context3) != id(context1)
