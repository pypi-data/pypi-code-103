from pathlib import Path
from typing import List

from pyconverters_speech.speech import SpeechConverter, SpeechParameters, TrfModel
from pymultirole_plugins.v1.schema import Document
from starlette.datastructures import UploadFile


def test_speech_wav():
    model = SpeechConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == SpeechParameters
    converter = SpeechConverter()
    parameters = SpeechParameters()
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/2.wav')
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'audio/wav'), parameters)
        assert len(docs) == 1
        doc0 = docs[0]
        assert doc0.text.startswith('on bed seven')


def test_speech_webm():
    model = SpeechConverter.get_model()
    model_class = model.construct().__class__
    assert model_class == SpeechParameters
    converter = SpeechConverter()
    parameters = SpeechParameters(model=TrfModel.wav2vec2_large_fr_voxpopuli_french)
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/ae26ccf4-ea2b-4bc7-b112-9bdb00931577.webm')
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'audio/webm'), parameters)
        assert len(docs) == 1
        doc0 = docs[0]
        assert 'personnes' in doc0.text
