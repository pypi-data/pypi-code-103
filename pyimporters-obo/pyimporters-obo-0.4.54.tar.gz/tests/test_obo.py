from pathlib import Path

from progress.bar import Bar
from pyimporters_plugins.base import Term

from pyimporters_obo.obo import OBOKnowledgeParser, OBOOptionsModel


def test_obo():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/small.obo')
    parser = OBOKnowledgeParser()
    options = OBOOptionsModel()
    concepts = list(parser.parse(source, options.dict(), Bar('Processing')))
    assert len(concepts) == 6
    c0: Term = concepts[0]
    assert c0.identifier == 'CVCL_E548'
    assert c0.preferredForm == '#15310-LN'
    assert len(c0.properties['altForms']) == 8
    assert set(c0.properties['altForms']) == {'15310-LN', 'TER461', 'TER-461', 'Ter 461', 'TER479', 'TER-479',
                                              'Ter 479', 'Extract 519'}
    assert c0.properties['wikidataId'] == 'Q54398957'


def test_obo_with_scope():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/small.obo')
    parser = OBOKnowledgeParser()
    options = OBOOptionsModel(synonym_scopes="EXACT,NARROW")
    concepts = list(parser.parse(source, options.dict(), Bar('Processing')))
    assert len(concepts) == 6
    c0: Term = concepts[0]
    assert c0.identifier == 'CVCL_E548'
    assert c0.preferredForm == '#15310-LN'
    assert len(c0.properties['altForms']) == 1
    assert c0.properties['altForms'] == ['15310-LN']
    assert c0.properties['wikidataId'] == 'Q54398957'


def test_obo_zipped():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/small.zip')
    parser = OBOKnowledgeParser()
    options = OBOOptionsModel()
    concepts = list(parser.parse(source, options.dict(), Bar('Processing')))
    assert len(concepts) == 6
    c0: Term = concepts[0]
    assert c0.identifier == 'CVCL_E548'
    assert c0.preferredForm == '#15310-LN'
    assert len(c0.properties['altForms']) == 8
    assert set(c0.properties['altForms']) == {'15310-LN', 'TER461', 'TER-461', 'Ter 461', 'TER479', 'TER-479',
                                              'Ter 479', 'Extract 519'}
    assert c0.properties['wikidataId'] == 'Q54398957'
