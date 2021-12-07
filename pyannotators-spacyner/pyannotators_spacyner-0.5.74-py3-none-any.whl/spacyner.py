import os
import sys
from enum import Enum
from functools import lru_cache
from typing import Type, List, cast, Optional

import spacy
from pydantic import BaseModel, Field
from pymultirole_plugins.util import comma_separated_to_list
from pymultirole_plugins.v1.annotator import AnnotatorParameters, AnnotatorBase
from pymultirole_plugins.v1.schema import Document, Span, Annotation, Term
from scispacy.linking_utils import Entity
from spacy.cli.download import download_model, get_compatibility, get_version
from spacy.errors import OLD_MODEL_SHORTCUTS
from spacy.language import Language
from spacy.util import run_command
from wasabi import msg

_home = os.path.expanduser('~')
xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')
cache_dir = os.path.join(xdg_cache_home, 'scispacy')
os.environ["SCISPACY_CACHE"] = cache_dir


class SciSpacyLinker(str, Enum):
    umls = 'umls'
    mesh = 'mesh'


class SpacyNERParameters(AnnotatorParameters):
    model: str = Field("en_core_web_sm",
                       description="Name of the [spacy model](https://spacy.io/models) to use for NER extraction")
    scispacy_linker: Optional[SciSpacyLinker] = Field(None,
                                                      description="Name of the [scispacy linker](https://github.com/allenai/scispacy) which performs linking to a knowledge base.")
    types_filter: Optional[str] = Field(None, description="Retain only entities belonging to the comma-separated list of types")
    mention_threshold: Optional[float] = Field(0.85,
                                               description="The threshold that a entity candidate must reach to be added.")
    mention_max: Optional[int] = Field(1,
                                       description="The maximum number of entities which will be returned for a given mention")


class SpacyNERAnnotator(AnnotatorBase):
    """[SpacyNER](https://github.com/facebook/spacyner) annotator.
    """

    def annotate(self, documents: List[Document], parameters: AnnotatorParameters) \
            -> List[Document]:
        params: SpacyNERParameters = \
            cast(SpacyNERParameters, parameters)
        # Create parsing context with time and language information
        nlp, linker = get_nlp(params.model, params.scispacy_linker)
        types_as_set = set(comma_separated_to_list(params.types_filter))
        for document in documents:
            document.annotations = []
            if not document.sentences:
                document.sentences = [Span(start=0, end=len(document.text))]
            sents = [document.text[s.start:s.end] for s in document.sentences]
            asents = nlp.pipe(sents)
            for sent, asent in zip(document.sentences, asents):
                for ent in asent.ents:
                    start = sent.start + ent.start_char
                    end = sent.start + + ent.end_char
                    terms = []
                    if linker is not None:
                        for umls_ent in ent._.kb_ents:
                            score = umls_ent[1]
                            if score >= params.mention_threshold:
                                kbent: Entity = linker.kb.cui_to_entity[umls_ent[0]]
                                types = types_as_set.intersection(kbent.types)
                                if types or len(types_as_set) == 0:
                                    props = {'types': kbent.types if len(types_as_set) == 0 else list(types),
                                             'aliases': kbent.aliases}
                                    term = Term(identifier=umls_ent[0], lexicon=params.scispacy_linker.value,
                                                preferredForm=kbent.canonical_name, score=score, properties=props)
                                    if len(terms) < params.mention_max:
                                        terms.append(term)
                                    else:
                                        break
                    if len(types_as_set) == 0 or len(terms) > 0:
                        document.annotations.append(Annotation(start=start, end=end,
                                                               labelName=ent.label_.lower(),
                                                               label=ent.label_,
                                                               text=document.text[start:end],
                                                               terms=terms))
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return SpacyNERParameters


@lru_cache(maxsize=None)
def get_nlp(model, linker=None):
    try:
        nlp: Language = spacy.load(model)
    except BaseException:
        nlp = load_spacy_model(model)
    if linker is not None:
        from scispacy.linking import EntityLinker
        linker: EntityLinker = nlp.add_pipe("scispacy_linker", config={"linker_name": linker.value})
    return nlp, linker


def load_spacy_model(model, *pip_args):
    if '_sci_' in model:
        model_name = model
        download_sci_model(model)
    else:
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


def download_sci_model(
        filename: str, user_pip_args=None) -> None:
    download_url = f"https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/{filename}-0.4.0.tar.gz"
    pip_args = list(user_pip_args) if user_pip_args is not None else []
    cmd = [sys.executable, "-m", "pip", "install"] + pip_args + [download_url]
    run_command(cmd)
