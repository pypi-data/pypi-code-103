from typing import List, Set, Union

import dask.dataframe as dd
import nltk
import pandas as pd
import spacy
from qdk.transform.base import TransformComponent
from qdk.utils.text import clean_text


class NounPhraseComponent(TransformComponent):
    replace_pos = {
        "ADJ": "JJ",
        "NOUN": "NN",
        # "PROPN": "NN",
    }
    noun_phrase_regex = "NP: {<NN.*|JJ>*<NN.*>}"

    @classmethod
    def extract_noun_phrases(cls, text: str, nlp: spacy.Language) -> List[str]:
        """This function takes a string as input and outputs a list of
        noun phrase candidates:

        "Dit is een zin met tekst" -> {"zin", "tekst"}

        Args:
            text (str): The text you would like to transform.
            nlp (spacy.Language): A spacy language model. Used for POS tagging.

        Returns:
            List[str]: The noun phrases found in the text.
        """
        # Clean the text before extracting phrases
        cleaned_text = clean_text(text=text)

        # Use spacy to parse and tokenize the text
        # Possibly replace pos tags
        doc = nlp(cleaned_text)
        doc = [
            (token.text.lower(), cls.replace_pos.get(token.pos_, token.pos_))
            for token in doc
        ]

        # Use the nltk regex parser to find all noun phrases
        parser = nltk.RegexpParser(cls.noun_phrase_regex)
        trees = parser.parse_sents([doc])

        # Storage for all key phrase candidates
        noun_phrases = []

        for tree in trees:
            for subtree in tree.subtrees(
                filter=lambda t: t.label() == "NP"
            ):  # For each nounphrase
                # Concatenate the token with a space
                noun_phrases.append(" ".join(word for word, _ in subtree.leaves()))

        # Filter out keyphrases that have more than 5 tokens
        noun_phrases = [
            noun_phrase for noun_phrase in noun_phrases if len(noun_phrase.split()) <= 5
        ]

        return noun_phrases

    @classmethod
    def transform(
        cls,
        df: Union[pd.DataFrame, dd.DataFrame],
        text_columns: List[str] = ["text"],
        spacy_model: str = "nl_core_news_lg",
    ) -> Union[pd.DataFrame, dd.DataFrame]:
        nlp = spacy.load(
            spacy_model,
            disable=[
                "parser",
                "ner",
                "lemmatizer",
                "textcat",
            ],
        )

        # Use dask to parallelize the keyword extraction over the workers
        if type(df) == dd.DataFrame:
            for text_column in text_columns:
                df[f"_nouns_{text_column}"] = df.map_partitions(
                    lambda _df: _df[text_column].apply(
                        cls.extract_noun_phrases, args=(nlp,)
                    )
                )
        # Pandas apply function
        else:
            for text_column in text_columns:
                df[f"_nouns_{text_column}"] = df[text_column].apply(
                    cls.extract_noun_phrases, args=(nlp,)
                )

        # Return the dataframe with the keywords
        return df
