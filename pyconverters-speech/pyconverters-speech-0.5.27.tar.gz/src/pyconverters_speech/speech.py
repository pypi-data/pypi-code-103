import os
from enum import Enum
from functools import lru_cache
from tempfile import NamedTemporaryFile
from typing import Type, List, cast

import filetype as filetype
from filetype.types.audio import Wav
from pydantic import BaseModel, Field
from pydub import AudioSegment
from pymultirole_plugins.v1.converter import ConverterParameters, ConverterBase
from pymultirole_plugins.v1.schema import Document
from starlette.datastructures import UploadFile
from transformers import AutomaticSpeechRecognitionPipeline, pipeline, AutoTokenizer, Wav2Vec2Processor
from transformers.pipelines.automatic_speech_recognition import ffmpeg_read

_home = os.path.expanduser('~')
xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')


class TrfModel(str, Enum):
    wav2vec2_base_960h = "facebook/wav2vec2-base-960h"
    wav2vec2_large_fr_voxpopuli_french = "jonatasgrosman/wav2vec2-large-fr-voxpopuli-french"


class SpeechParameters(ConverterParameters):
    model: TrfModel = Field(TrfModel.wav2vec2_base_960h,
                            description="""Which [Transformers model](
                            https://huggingface.co/models?pipeline_tag=automatic-speech-recognition) fine-tuned
                            for Speech Recognition to use, can be one of:<br/>
                            <li>`facebook/wav2vec2-base-960h`: The base model pretrained and fine-tuned on 960 hours of Librispeech on 16kHz sampled speech audio.<br/>
                            <li>`jonatasgrosman/wav2vec2-large-fr-voxpopuli-french`: Fine-tuned facebook/wav2vec2-large-fr-voxpopuli on French using the Common Voice.""")
    lowercase: bool = Field(True, description="Convert to lowercase")


class SpeechConverter(ConverterBase):
    """Speech converter .
    """

    def convert(self, source: UploadFile, parameters: ConverterParameters) \
            -> List[Document]:
        params: SpeechParameters = \
            cast(SpeechParameters, parameters)

        # Create cached pipeline context with model
        p: AutomaticSpeechRecognitionPipeline = get_pipeline(params.model)
        kind = filetype.guess(source.file)
        source.file.seek(0)
        doc: Document = None
        if kind is not None and kind.mime.startswith('audio') or kind.mime.startswith('video'):
            inputs = None
            if isinstance(kind, Wav):
                inputs = source.file.read()
            else:
                try:
                    codec = "opus" if kind.extension == "webm" else None
                    segment = AudioSegment.from_file(source.file, codec=codec)
                    # check audio export
                    with NamedTemporaryFile('w+b', suffix='.wav') as tmp_file:
                        segment.export(tmp_file, format="wav")
                        tmp_file.seek(0)
                        inputs = tmp_file.file.read()
                except BaseException as err:
                    raise err
            if inputs is not None:
                result = run_single(p, inputs)
                doc = Document(identifier=source.filename,
                               text=result['text'].lower() if params.lowercase else result['text'])
                doc.properties = {"fileName": source.filename}
        if doc is None:
            raise TypeError(f"Conversion of audio file {source.filename} failed")
        return [doc]

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return SpeechParameters


@lru_cache(maxsize=None)
def get_pipeline(model):
    p = pipeline("automatic-speech-recognition", model=model.value,
                 tokenizer=AutoTokenizer.from_pretrained(model.value))
    if model in [TrfModel.wav2vec2_large_fr_voxpopuli_french]:
        p.processor = Wav2Vec2Processor.from_pretrained(model.value)
    return p


def run_single(p, inputs):
    if hasattr(p, 'processor'):
        processor = p.processor
        if isinstance(inputs, bytes):
            inputs = ffmpeg_read(inputs, p.feature_extractor.sampling_rate)
        model_inputs = processor(inputs, return_tensors="pt", padding=True)
        for key in model_inputs:
            model_inputs[key] = model_inputs[key].clone()
    else:
        model_inputs = p.preprocess(inputs)
    model_outputs = p.forward(model_inputs)
    outputs = p.postprocess(model_outputs)
    return outputs
