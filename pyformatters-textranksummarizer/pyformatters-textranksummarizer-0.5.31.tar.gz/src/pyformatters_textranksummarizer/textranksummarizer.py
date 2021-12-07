from abc import ABC
from enum import Enum
from functools import lru_cache
from math import sqrt
from operator import itemgetter
from typing import Type, cast, List

import pytextrank  # noqa: F401
import spacy
from collections_extended import RangeMap
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.formatter import FormatterParameters, FormatterBase
from pymultirole_plugins.v1.processor import ProcessorBase, ProcessorParameters
from pymultirole_plugins.v1.schema import Document, Sentence
from spacy.cli.download import download_model, get_compatibility, get_version
from spacy.errors import OLD_MODEL_SHORTCUTS
from spacy.language import Language
from spacy.tokens import Doc
from starlette.responses import Response, PlainTextResponse
from wasabi import msg


# _home = os.path.expanduser('~')
# xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')

class TextRankAlgo(str, Enum):
    textrank = 'textrank'
    positionrank = 'positionrank'
    # biasedtextrank = 'biasedtextrank'


class TextRankSummarizerParameters(FormatterParameters):
    as_metadata: str = Field(None, description="""If defined generate the summary as a metadata of the input document,
    if not replace the text of the input document.""")
    lang: str = Field("en",
                      description="Name of the 2-letter language of the documents")
    algo: TextRankAlgo = Field(TextRankAlgo.textrank, description="""The textgraph algorithms to use<br />
    <li>`textrank` TextRank by [mihalcea04textrank](https://web.eecs.umich.edu/~mihalcea/papers/mihalcea.emnlp04.pdf)<br />
    <li>`positionrank` PositionRank by [florescuc17](https://www.aclweb.org/anthology/P17-1102.pdf)<br />""")
    # <li>`biasedtextrank` Biased TextRank by [kazemi-etal-2020-biased](https://www.aclweb.org/anthology/2020.coling-main.144.pdf)<br />""")
    algo: TextRankAlgo = Field(TextRankAlgo.textrank,
                               description="Name of the 2-letter language of the documents")
    num_sentences: float = Field(0.25, description="""Number of sentences of the summary:<br/>
        <li>If float in the range [0.0, 1.0], then consider num_sentences as a percentage of the original number
        of sentences of the document.""")
    num_phrases: int = Field(10, description="Maximum number of top-ranked phrases to use in the distance vectors.")
    preserve_order: bool = Field(False, description="""Flag to preserve the order of sentences as they originally
    occurred in the source text; defaults to `False`""")


class TextRankSummarizerFormatter(FormatterBase, ProcessorBase, ABC):
    """"A graphbased ranking model for text processing. Extractive sentence summarization.
    """

    # cache_dir = os.path.join(xdg_cache_home, 'trankit')
    def _check_sentences(self, nlp, algo: str, document: Document):
        doc: Doc = None
        if not document.sentences:
            doc = nlp(document.text)
        else:
            textrank = nlp.get_pipe(algo)
            parser = nlp.get_pipe("parser")
            with nlp.select_pipes(disable=["parser", algo]):
                doc = nlp(document.text)
                sent_map = RangeMap()
                for i, s in enumerate(document.sentences):
                    if s.end > s.start:
                        sent_map[s.start:s.end] = i
                current = -1
                for token in doc:
                    if token.idx in sent_map:
                        idsent = sent_map[token.idx]
                        if idsent != current:
                            token.is_sent_start = True
                            current = idsent
                if doc.has_annotation("SENT_START"):
                    doc = textrank(parser(doc))
        return doc

    def _summarize(self, document: Document, parameters: FormatterParameters) -> str:
        def int_float(v: float):
            if 0.0 <= v < 1.0:
                return v
            return int(abs(v))

        params: TextRankSummarizerParameters = \
            cast(TextRankSummarizerParameters, parameters)
        nlp = get_nlp(params.lang, params.algo.value)
        doc = self._check_sentences(nlp, params.algo.value, document)
        sent_bounds = [[s.start, s.end, set([])] for s in doc.sents]
        num_sentences = int_float(params.num_sentences)
        limit_sentences = round(len(sent_bounds) * num_sentences) if isinstance(num_sentences, float) else num_sentences
        phrase_id = 0
        unit_vector = []
        for p in doc._.phrases:
            unit_vector.append(p.rank)
            for chunk in p.chunks:
                for sent_start, sent_end, sent_vector in sent_bounds:
                    if chunk.start >= sent_start and chunk.end <= sent_end:
                        sent_vector.add(phrase_id)
                        break
            phrase_id += 1
            if phrase_id == params.num_phrases:
                break

        sum_ranks = sum(unit_vector)

        unit_vector = [rank / sum_ranks for rank in unit_vector]

        sent_rank = {}
        sent_id = 0
        for sent_start, sent_end, sent_vector in sent_bounds:
            sum_sq = 0.0
            for phrase_id in range(len(unit_vector)):
                if phrase_id not in sent_vector:
                    sum_sq += unit_vector[phrase_id] ** 2.0
            sent_rank[sent_id] = sqrt(sum_sq)
            sent_id += 1
        # sorted(sent_rank.items(), key=itemgetter(1))
        sent_text = {}
        sent_id = 0
        for sent in doc.sents:
            sent_text[sent_id] = sent.text.strip()
            sent_id += 1
        num_sent = 0
        summary_sentences = {}
        for sent_id, rank in sorted(sent_rank.items(), key=itemgetter(1)):
            summary_sentences[sent_id] = sent_text[sent_id]
            num_sent += 1
            if num_sent == limit_sentences:
                break
        if params.preserve_order:
            summary_sents = [v for k, v in sorted(summary_sentences.items(), key=itemgetter(0))]
        else:
            summary_sents = list(summary_sentences.values())
        return summary_sents

    def format(self, document: Document, parameters: FormatterParameters) \
            -> Response:
        summary_sentences = self._summarize(document, parameters)
        summary = '\n'.join(summary_sentences)
        return PlainTextResponse(summary)

    def process(self, documents: List[Document], parameters: ProcessorParameters) \
            -> List[Document]:
        params: TextRankSummarizerParameters = \
            cast(TextRankSummarizerParameters, parameters)
        for document in documents:
            summary_sentences = self._summarize(document, parameters)
            if params.as_metadata is not None and len(params.as_metadata):
                if not document.metadata:
                    document.metadata = {}
                document.metadata[params.as_metadata] = '\n'.join(summary_sentences)
            else:
                document.text = ""
                document.sentences = []
                for i, summary_sentence in enumerate(summary_sentences):
                    last = i == len(summary_sentences) - 1
                    start = len(document.text)
                    end = start + len(summary_sentence)
                    document.sentences.append(Sentence(start=start, end=end))
                    document.text += summary_sentence + ("\n" if not last else "")
                    document.annotations = None
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return TextRankSummarizerParameters


# Deprecated model shortcuts, only used in errors and warnings
MODEL_SHORTCUTS = {
    "en": "en_core_web_sm", "de": "de_core_news_sm", "es": "es_core_news_sm",
    "pt": "pt_core_news_sm", "fr": "fr_core_news_sm", "it": "it_core_news_sm",
    "nl": "nl_core_news_sm", "el": "el_core_news_sm", "nb": "nb_core_news_sm",
    "lt": "lt_core_news_sm", "xx": "xx_ent_wiki_sm"
}


@lru_cache(maxsize=None)
def get_nlp(lang: str, algo: str, ttl_hash=None):
    del ttl_hash
    model = MODEL_SHORTCUTS.get(lang, lang)
    # model = lang
    try:
        nlp: Language = spacy.load(model)
    except BaseException:
        nlp = load_spacy_model(model)
    nlp.add_pipe(algo, last=True)
    return nlp


def load_spacy_model(model, *pip_args):
    suffix = "-py3-none-any.whl"
    dl_tpl = "{m}-{v}/{m}-{v}{s}#egg={m}=={v}"
    model_name = model
    if model in OLD_MODEL_SHORTCUTS:
        msg.warn(
            f"As of spaCy v3.0, shortcuts like '{model}' are deprecated. Please "
            f"use the full pipeline package name '{OLD_MODEL_SHORTCUTS[model]}' instead."
        )
        model_name = OLD_MODEL_SHORTCUTS[model]
    compatibility = get_compatibility()
    if model_name not in compatibility:
        msg.fail(
            f"No compatible package found for '{model}' (spaCy v{spacy.about.__version__}), fallback to blank model")
        return spacy.blank(model_name)
    else:
        version = get_version(model_name, compatibility)
        download_model(dl_tpl.format(m=model_name, v=version, s=suffix), pip_args)
        msg.good(
            "Download and installation successful",
            f"You can now load the package via spacy.load('{model_name}')",
        )
        # If a model is downloaded and then loaded within the same process, our
        # is_package check currently fails, because pkg_resources.working_set
        # is not refreshed automatically (see #3923). We're trying to work
        # around this here be requiring the package explicitly.
        require_package(model_name)
        return spacy.load(model_name)


def require_package(name):
    try:
        import pkg_resources

        pkg_resources.working_set.require(name)
        return True
    except:  # noqa: E722
        return False
