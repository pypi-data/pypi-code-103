from typing import Type, List, cast
from collections_extended import RangeMap
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.processor import ProcessorBase, ProcessorParameters
from pymultirole_plugins.v1.schema import Document, Sentence


class ReadingGridParameters(ProcessorParameters):
    separator: str = Field("", description="Separator to append to the remaining sentences")


class ReadingGridProcessor(ProcessorBase):
    """"A processor that generate a reduced/focussed version of the document keeping only the sentences
    that actually contain annotations.
    """

    def process(self, documents: List[Document], parameters: ProcessorParameters) \
            -> List[Document]:
        params: ReadingGridParameters = \
            cast(ReadingGridParameters, parameters)
        for document in documents:
            sentences = []
            annotations = []
            start = 0
            text = ""
            separator = params.separator
            if not separator.startswith("\n"):
                separator = "\n" + separator
            if not separator.endswith("\n"):
                separator = separator + "\n"
            if document.sentences is not None and document.annotations is not None:
                sentence_map = RangeMap()
                for s in document.sentences:
                    sentence_map[s.start:s.end] = []
                for a in document.annotations:
                    sentence_map[a.start].append(a)
                for sent in sentence_map.ranges():
                    ann_list = sent.value
                    if ann_list:
                        sstart = start
                        send = sstart + (sent.stop - sent.start)
                        sentences.append(Sentence(start=sstart, end=send))
                        text += document.text[sent.start:sent.stop] + separator
                        for a in ann_list:
                            astart = a.start - sent.start
                            aend = a.end - sent.start
                            a.start = sstart + astart
                            a.end = sstart + aend
                            annotations.append(a)
                        start = len(text)
            if text.endswith(separator):
                text = text[:-len(separator)]
            document.sentences = sentences
            document.annotations = annotations
            document.text = text
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return ReadingGridParameters
