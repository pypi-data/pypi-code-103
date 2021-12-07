import json
from collections import defaultdict
from itertools import groupby
from pathlib import Path

import pytest
from pymultirole_plugins.v1.schema import Document, Annotation
from starlette.responses import JSONResponse

from pyformatters_consolidate.consolidate import ConsolidateFormatter, ConsolidateParameters, ConsolidationType


def by_lexicon(a: Annotation):
    if a.terms:
        return a.terms[0].lexicon
    else:
        return ""


def by_label(a: Annotation):
    return a.labelName


def group_annotations(doc: Document, keyfunc):
    groups = defaultdict(list)
    for k, g in groupby(sorted(doc.annotations, key=keyfunc), keyfunc):
        groups[k] = list(g)
    return groups


def test_model():
    model = ConsolidateFormatter.get_model()
    model_class = model.construct().__class__
    assert model_class == ConsolidateParameters


# Arrange
@pytest.fixture
def original_doc():
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/response_1622736571452.json')
    with source.open("r") as fin:
        docs = json.load(fin)
        original_doc = Document(**docs[0])
        return original_doc


def assert_original_doc(original_doc):
    original_groups_lexicon = group_annotations(original_doc, by_lexicon)
    original_groups_label = group_annotations(original_doc, by_label)
    assert len(original_groups_lexicon[""]) == 22
    assert len(original_groups_lexicon["lex_location"]) == 1
    assert len(original_groups_lexicon["lex_person"]) == 8
    assert len(original_groups_label["organization"]) == 4
    assert len(original_groups_label["location"]) == 4
    assert len(original_groups_label["person"]) == 23
    return original_groups_lexicon, original_groups_label


def test_consolidate_linker(original_doc):
    # linker
    original_groups_lexicon, original_groups_label = assert_original_doc(original_doc)
    assert original_groups_lexicon is not None
    assert original_groups_label is not None
    doc = original_doc.copy(deep=True)
    formatter = ConsolidateFormatter()
    parameters = ConsolidateParameters(type=ConsolidationType.linker)
    resp: JSONResponse = formatter.format(doc, parameters)
    content = resp.body.decode(resp.charset)
    consolidated: Document = Document(**json.loads(content))
    consolidated_groups_lexicon = group_annotations(consolidated, by_lexicon)
    # consolidated_groups_label = group_annotations(consolidated, by_label)
    assert resp.status_code == 200
    assert resp.media_type == "application/json"
    assert len(original_doc.annotations) > len(consolidated.annotations)
    assert len(consolidated_groups_lexicon[""]) == 0
    assert "file.json" in resp.headers['Content-Disposition']


def test_consolidate_unknown(original_doc):
    # unknown
    original_groups_lexicon, original_groups_label = assert_original_doc(original_doc)
    assert original_groups_lexicon is not None
    assert original_groups_label is not None
    doc = original_doc.copy(deep=True)
    formatter = ConsolidateFormatter()
    parameters = ConsolidateParameters(type=ConsolidationType.unknown)
    resp: JSONResponse = formatter.format(doc, parameters)
    content = resp.body.decode(resp.charset)
    consolidated: Document = Document(**json.loads(content))
    # consolidated_groups_lexicon = group_annotations(consolidated, by_lexicon)
    consolidated_groups_label = group_annotations(consolidated, by_label)
    assert resp.status_code == 200
    assert resp.media_type == "application/json"
    assert len(original_doc.annotations) > len(consolidated.annotations)
    knowns_unknowns = defaultdict(list)
    for label, anns in consolidated_groups_label.items():
        k = 'unknown' if label.startswith("unknown_") else "known"
        knowns_unknowns[k].extend(anns)
    assert len(knowns_unknowns["known"]) > 0
    assert len(knowns_unknowns["unknown"]) > 0


def test_consolidate_unknown_only(original_doc):
    # unknwon only
    original_groups_lexicon, original_groups_label = assert_original_doc(original_doc)
    assert original_groups_lexicon is not None
    assert original_groups_label is not None
    doc = original_doc.copy(deep=True)
    formatter = ConsolidateFormatter()
    parameters = ConsolidateParameters(type=ConsolidationType.unknown_only)
    resp: JSONResponse = formatter.format(doc, parameters)
    content = resp.body.decode(resp.charset)
    consolidated: Document = Document(**json.loads(content))
    # consolidated_groups_lexicon = group_annotations(consolidated, by_lexicon)
    consolidated_groups_label = group_annotations(consolidated, by_label)
    assert resp.status_code == 200
    assert resp.media_type == "application/json"
    assert len(original_doc.annotations) > len(consolidated.annotations)
    knowns_unknowns = defaultdict(list)
    for label, anns in consolidated_groups_label.items():
        k = 'unknown' if label.startswith("unknown_") else "known"
        knowns_unknowns[k].extend(anns)
    assert len(knowns_unknowns["known"]) == 0
    assert len(knowns_unknowns["unknown"]) > 0
