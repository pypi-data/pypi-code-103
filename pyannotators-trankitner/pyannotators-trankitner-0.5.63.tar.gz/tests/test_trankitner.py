from typing import List

from pyannotators_trankitner.trankitner import TrankitNERAnnotator, TrankitNERParameters
from pymultirole_plugins.v1.schema import Document


def test_trankitner_english():
    model = TrankitNERAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == TrankitNERParameters
    annotator = TrankitNERAnnotator()
    parameters = TrankitNERParameters(lang='english')
    docs: List[Document] = annotator.annotate([Document(
        text="Paris is the capital of France and Emmanuel Macron is the president of the French Republic.",
        metadata=parameters.dict())], parameters)
    doc0 = docs[0]
    assert len(doc0.annotations) == 4
    paris = doc0.annotations[0]
    france = doc0.annotations[1]
    macron = doc0.annotations[2]
    republic = doc0.annotations[3]
    assert paris.label == 'LOC'
    assert france.label == 'LOC'
    assert macron.label == 'PER'
    assert republic.label == 'LOC'


def test_trankitner_arabic():
    model = TrankitNERAnnotator.get_model()
    model_class = model.construct().__class__
    assert model_class == TrankitNERParameters
    annotator = TrankitNERAnnotator()
    parameters = TrankitNERParameters(lang='arabic')
    docs: List[Document] = annotator.annotate([Document(
        text="باريس هي عاصمة فرنسا وإيمانويل ماكرون هو رئيس الجمهورية الفرنسية",
        metadata=parameters.dict())], parameters)
    doc0 = docs[0]
    assert len(doc0.annotations) == 3
    paris = doc0.annotations[0]
    france = doc0.annotations[1]
    macron = doc0.annotations[2]
    assert paris.label == 'LOC'
    assert france.label == 'LOC'
    assert macron.label == 'PER'
