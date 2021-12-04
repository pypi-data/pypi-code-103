import json
import os
import pickle
from abc import ABC, abstractmethod
from collections import Counter, defaultdict
from typing import Any, Dict, List

import langdetect
import pandas as pd
from sklearn.pipeline import make_pipeline
from tqdm import tqdm
from treegrams.transformers import TreeGramExtractor

import stanza
from tuhlbox import logger
from tuhlbox.stanza import StanzaToNltkTreesTransformer


class Contributor(ABC):
    def __init__(
        self,
        column_name: str,
        required_columns: List[str],
        flush_after_each_row: bool = False,
        overwrite: bool = False,
    ) -> None:
        self.column_name = column_name
        self.required_columns = required_columns
        self.flush_after_each_row = flush_after_each_row
        self.base_dir: str = ""
        self.overwrite = overwrite

    def contribute(self, csv_path: str) -> None:
        self.base_dir = os.path.dirname(csv_path)
        name = self.__class__.__name__
        df = pd.read_csv(csv_path)
        if not set(self.required_columns).issubset(set(df.columns)):
            raise Exception(f"not all column requirements for {name} are fulfilled.")

        if self.column_name in df.columns and not (
            self.overwrite or self.flush_after_each_row
        ):
            logger.info("skipping contributor %s, column exists", name)
            return
        logger.info(f"{name} is calculating column: " f"{self.column_name}")
        df = self.calculate(df)
        df.to_csv(csv_path)

    @abstractmethod
    def calculate(self, row: pd.DataFrame) -> pd.DataFrame:
        pass

    def read_subdir_file(self, path: str, mode: str = "text") -> Any:
        full_path = os.path.join(self.base_dir, path)
        if mode == "text":
            with open(full_path) as text_fh:
                return text_fh.read()
        if mode == "pickle":
            with open(full_path, "rb") as pickle_fh:
                return pickle.load(pickle_fh)

    def write_subdir_file(self, path: str, content: Any, mode: str = "text") -> None:
        full_path = os.path.join(self.base_dir, path)
        if mode == "text":
            with open(full_path, "w") as text_fh:
                text_fh.write(content)
        if mode == "pickle":
            with open(full_path, "wb") as pickle_fh:
                pickle.dump(content, pickle_fh)


class RowWiseContributor(Contributor):
    @abstractmethod
    def calculate_row(self, row: pd.Series) -> pd.Series:
        pass

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        new_rows = []
        for _, row in tqdm(df.iterrows(), total=df.shape[0]):
            new_rows.append(self.calculate_row(row))
        return pd.DataFrame(new_rows)


class LinguisticStatsContributor(RowWiseContributor):
    """
    Calculates the type/token ratio along with many other counts.

    Returns a dict with the distinct number of:
     - "upos": universal POS tags
     - "xpos": language-specific POS tags
     - "lemma": the word's lemma
     - "text": the word's text (type)
     - "deprel": the universal dependency relationship of this word to its parent
     - "tokens": total number of non-distinct tokens
     - "words": total number of non-distinct words
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            column_name="linguistic_stats", required_columns=["stanza"], **kwargs
        )

    def calculate_row(self, row: pd.Series) -> pd.Series:
        document = self.read_subdir_file(row["stanza"], "pickle")
        fields = ["upos", "xpos", "lemma", "text", "deprel"]
        sets = defaultdict(set)
        for word in document.iter_words():
            for field in fields:
                sets[field].add(getattr(word, field))
        result: Dict[str, Any] = {f: len(sets[f]) for f in fields}
        result["tokens"] = document.num_tokens
        result["words"] = document.num_words
        result["characters"] = len(f"{document.text}")
        result["sentence_lengths"] = [len(sent.tokens) for sent in document.sentences]
        row[self.column_name] = json.dumps(result)
        return row


class StanzaContributor(RowWiseContributor):
    def __init__(self, directory_name: str = "stanza", **kwargs: Any) -> None:
        super().__init__(
            column_name="stanza",
            required_columns=["text_raw", "language"],
            flush_after_each_row=True,
            **kwargs,
        )
        self.parsers: Dict[str, stanza.Pipeline] = {}
        self.directory_name = directory_name

    def calculate_row(self, row: pd.Series) -> pd.Series:
        lang = row["language"]
        input_filename = row["text_raw"]
        stanza_dir = os.path.join(self.base_dir, self.directory_name)
        if not os.path.isdir(stanza_dir):
            os.makedirs(stanza_dir)
        out_filename = os.path.splitext(os.path.basename(input_filename))[0] + ".pckl"
        out_filepath = os.path.join(self.directory_name, out_filename)
        full_out_filepath = os.path.join(self.base_dir, out_filepath)

        if not os.path.isfile(full_out_filepath) or self.overwrite:
            text = self.read_subdir_file(input_filename)
            if lang not in self.parsers:
                self.parsers[lang] = stanza.Pipeline(
                    lang=lang, use_gpu=False, processors="tokenize,pos,depparse,lemma"
                )
            document = self.parsers[lang](text)
            self.write_subdir_file(out_filepath, document, "pickle")
        row[self.column_name] = out_filepath
        return row


class LanguageDetectionContributor(RowWiseContributor):
    def __init__(self, min_lang_prob: float = 0.99) -> None:
        super().__init__(column_name="language", required_columns=["text_raw"])
        self.min_lang_prob = min_lang_prob

    def calculate_row(self, row: pd.Series) -> pd.Series:
        text = self.read_subdir_file(row["text_raw"])
        langdetect.detect_langs(text)
        language_scores = sorted(
            list(langdetect.detect_langs(text)), key=lambda x: x.prob, reverse=True
        )
        scores = [x.prob for x in language_scores]
        langs = [x.lang for x in language_scores]
        if scores[0] > self.min_lang_prob:
            row[self.column_name] = langs[0]
        else:
            row[self.column_name] = None
        return row


class CounterContributor(RowWiseContributor):
    def __init__(
        self,
        column_name: str = "dtgram_counter",
        directory_name: str = "dtgram_counters",
        **kwargs: Any,
    ) -> None:
        super().__init__(column_name=column_name, required_columns=["stanza"], **kwargs)
        self.column_name = column_name
        self.directory_name = directory_name
        self.dtgram_pipeline = make_pipeline(
            StanzaToNltkTreesTransformer(),
            TreeGramExtractor(),
        )

    def calculate_row(self, row: pd.Series) -> pd.Series:
        stanza_document = self.read_subdir_file(row["stanza"], mode="pickle")

        counter_dir = os.path.join(self.base_dir, self.directory_name)
        if not os.path.isdir(counter_dir):
            os.makedirs(counter_dir)
        out_filename = os.path.splitext(os.path.basename(row["stanza"]))[0] + ".pckl"
        out_filepath = os.path.join(self.directory_name, out_filename)
        full_out_filepath = os.path.join(self.base_dir, out_filepath)

        if not os.path.isfile(full_out_filepath) or self.overwrite:
            dt_grams = self.dtgram_pipeline.transform([stanza_document])[0]
            counter: Counter = Counter(dt_grams)
            self.write_subdir_file(out_filepath, counter, mode="pickle")

        row[self.column_name] = out_filepath
        return row


class ConstantContributor(Contributor):
    def __init__(self, column_name: str, value: Any) -> None:
        super().__init__(column_name=column_name, required_columns=[])
        self.column_name = column_name
        self.value = value

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df[self.column_name] = [self.value] * df.shape[0]
        return df
