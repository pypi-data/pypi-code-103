from pydantic import BaseModel, validator
from typing import List, Optional, Union, Type, Tuple, Any, Callable, Dict
from abc import ABC, abstractmethod
import sys
import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import threading
# from keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
import re
import joblib
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pickle import dump, load, HIGHEST_PROTOCOL
import json
import usaddress


# global utility
def clean_street(street):
    """clean out common subphrases that confuse similarity ML model"""
    refined_street_string = ''

    # expect parsed input of street
    for word in street:
        # check in the dataclass model for the common word match
        if word.lower() not in ForwardGeocodingSchema.common_streets:
            if street.index(word) == 0:
                refined_street_string += word
            else:
                refined_street_string += " " + word
        else:
            continue

    # give the refined street string without the common words or such
    return refined_street_string


# noinspection PyCompatibility,PyMissingOrEmptyDocstring
class AddressPartsModel(BaseModel):
    street: Union[str, None]
    unit: Optional[str] = ''
    number: Union[str, int]
    postcode: Union[str, int]
    region: Union[str, None]
    city: Union[str, None]


# noinspection PyCompatibility
class ForwardGeocodingSchema(BaseModel):
    """store data model for forward geocoding functionality"""

    earth_radius: Optional[Union[float, int]] = 6378.1 * 1000
    radius: Union[List, List[List], int, float]
    common_streets: Optional[List[str]] = ['road', 'street', 'avenue', 'drive', 'lane', 'route', 'court', 'west',
                                           'east', 'north',
                                           'south', 'place', 'state', 'boulevard', 'county', 'way', 'square']
    batch_spreadsheet_count: Optional[int] = 0
    stopwords_index: Optional[str] = 'english'


"""-------------------------------Pydantic Error Models ---------------------------------"""


# noinspection PyCompatibility
class IncorrectLengthError(Exception):
    """error class in case parsing length is too short"""

    def __init__(self, length: int, message: str, status_code: int) -> None:
        self.length = length
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# noinspection PyCompatibility
class UnitCheckError(Exception):
    """custom exception class for unit checking errors"""

    def __init__(self, unit_check: bool, message: str, status_code: int) -> None:
        self.unit_check = unit_check
        self.message = message
        self.status_code = status_code
        super().__init__(message)


""""-------------------------------parsing models ----------------------------------------"""


# noinspection PyCompatibility,PyMissingOrEmptyDocstring
class AddressParseModel(BaseModel):
    street: Optional[str]
    postcode: Optional[Union[int, str]]
    number: Optional[Union[int, str]]
    region: Optional[str]
    unit: Optional[Union[None, str]]
    city: Optional[str]

    decode_vocabulary = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h', 9: 'i', 10: 'j', 11: 'k',
                       12: 'l', 13: 'm', 14: 'n', 15: 'o',
                       16: 'p', 17: 'q', 18: 'r', 19: 's', 20: 't', 21: 'u', 22: 'v', 23: 'w', 24: 'x', 25: 'y',
                       26: 'z', 27: '1', 28: '2',
                       29: '3', 30: '4', 31: '5', 32: '6', 33: '7', 34: '8', 35: '9', 36: '0', 37: '-', 38: ' ',
                       39: '/', 40: "'"}
    vocabulary = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9, 'j': 10, 'k': 11, 'l': 12, 'm': 13, 'n': 14, 'o': 15, 'p': 16, 'q': 17, 'r': 18, 's': 19, 't': 20, 'u': 21, 'v': 22, 'w': 23, 'x': 24, 'y': 25, 'z': 26, '1': 27, '2': 28, '3': 29, '4': 30, '5': 31, '6': 32, '7': 33, '8': 34, '9': 35, '0': 36, '-': 37, ' ': 38, '/': 39, "'": 40}


# noinspection PyCompatibility
class SimilarityAddressParser(BaseModel):
    """base model for new similarity parser"""
    state_new: str
    postcode_new: str
    number_new: str
    city_new: str
    unit_new: str


"""-------------------------------parsing strategy-----------------------------------------"""


class ParsingStrategy(ABC):
    @abstractmethod
    def parsing_strategy(self, address: str) -> str:
        """"address parsing models here"""
        pass


class StreetStrategy(ParsingStrategy):
    def parsing_strategy(self, address: str) -> str:
        street = (address.split(',')[0]).split(' ')[1:]
        return ' '.join(street)


class PostcodeStrategy(ParsingStrategy):
    def parsing_strategy(self, address: str, *args) -> str:
        parsed_address = address.split(',')[3]
        model_in = ''.join(list(parsed_address)[1:])
        return model_in


class NumberStrategy(ParsingStrategy):
    def parsing_strategy(self, address: str, *args) -> str:
        parsed_number = address.split(',')[0].split(' ')[0]
        return parsed_number


class UnitStrategy(ParsingStrategy):
    def parsing_strategy(self, address: str, *args) -> str:
        unit_check = args[0]
        try:
            if unit_check:
                parsed_address = address.split(',')[-1]
                model_in = ''.join(list(parsed_address)[1:])
                return model_in
            else:
                return ''
        except IndexError or TypeError:
            raise UnitCheckError


class RegionStrategy(ParsingStrategy):
    def parsing_strategy(self, address: str, *args) -> str:
        region = address.split(',')[2]
        model_in = ''.join(list(region[1:]))
        return model_in


class CityStrategy(ParsingStrategy):
    def parsing_strategy(self, address: str, *args) -> str:
        model_in = ''.join(list(address.split(',')[1])[1:])
        return model_in


def strategy_builder(address: str, *args) -> list:
    """director function for organizing parsing strategies"""

    # get the address length
    address_length = list(address).count(',')

    # create the pydantic local dataclass
    try:
        parse_model = AddressParseModel(address_length=address_length)

        # builder steps
        parse_model.street = StreetStrategy().parsing_strategy(address)
        parse_model.number = int(NumberStrategy().parsing_strategy(address))
        parse_model.postcode = int(PostcodeStrategy().parsing_strategy(address))
        parse_model.region = RegionStrategy().parsing_strategy(address)
        parse_model.city = CityStrategy().parsing_strategy(address)

        try:
            parse_model.unit = UnitStrategy().parsing_strategy(address, args[0])
        except UnitCheckError:
            raise ValueError

        # return model as dictionary type
        return list(parse_model.dict().values())

    except IncorrectLengthError or UnitCheckError:
        raise ValueError


"""-------------------------------------- DEEP LEARNING PARSER----------------------------------------"""


class Lemmatize(BaseEstimator, TransformerMixin):

    """lemmatize the input text"""

    def __init__(self, lemmatize=False):
        self.lemmatize = lemmatize
        self.stop_words = stopwords.words("english")
        self.wnl = WordNetLemmatizer()

    def lemmatizer_func(self, text, cores=3):
        """lemmatize text with multiprocessing pool"""
        with Pool(processes=cores) as pool:
            result = pool.map(self.wnl.lemmatize, text)
        return result

    def fit(self, address):
        return self

    def transform(self, address):
        # lemmatize the text to remove stopwords
        text = re.sub("@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+", ' ', str(address).lower()).strip()
        if self.lemmatize:
            start3 = perf_counter()
            text = ' '.join([self.wnl.lemmatize(i) for i in text.split(' ') if i not in self.stop_words])
            print(perf_counter() - start3, 'lemmatize time')

        return text


class RemoveStops(BaseEstimator, TransformerMixin):

    """remove symbols and OOVs from input vector"""

    def __init__(self, remove_spaces=False):
        self.remove_spaces = remove_spaces
        # create the vocabulary embedding index
        self.vocabulary = AddressParseModel().vocabulary
        self.vocab_set = set(self.vocabulary.keys())

    def fit(self, address):
        return self

    def transform(self, address):
        # convert address string to set
        address_set = set(address)

        # find different characters
        char_diff = address_set.difference(self.vocab_set)

        # remove those char stopages from input string
        for char in char_diff:
            address = address.replace(char, '')

        return address


class CharEmbedding(BaseEstimator, TransformerMixin):

    """embed the input address string with either one-hot encoding or custom label autoencoder"""

    def __init__(self, one_hot=False, label_encode=True):
        super().__init__()
        self.one_hot = one_hot
        self.label_encode = label_encode
        self.vocabulary = AddressParseModel().vocabulary

    def label_encoder_labels(self, word):
        vectors = []
        for w in word:
            vector = [self.vocabulary[char] for char in list(w)]
            vectors.append(vector)
        return vectors

    def fit(self, address):
        return self

    def transform(self, address):
        # perform char embedding autoencoding on the input address string
        addresses = pad_sequences(self.label_encoder_labels([address]), padding="post", maxlen=73)  # pad sequences

        # convert to list
        address_pre_arr = [list(address) for address in addresses]

        # translate to numpy array
        return np.array(address_pre_arr)


class PipelineModel(BaseModel):
    full_pipe = Pipeline([
        ("lemmatize", Lemmatize()),
        ("symb", RemoveStops()),
        ("embedchar", CharEmbedding())
    ])

    class Config:
        def __init__(self):
            pass

        arbitrary_types_allowed = True


class CustomPredictFull:

    """custom prediction method for all component models"""

    def __init__(self, address):
        self.address = address
        self.cleaned_address = None
        self.pipeline = PipelineModel().full_pipe
        self.decode_vocab = AddressParseModel().decode_vocabulary
        self.finished_predicts = {}

    def decode_sequence(self, ex_seq):
        """decode the numpy address sequences"""
        address = ''
        for i in ex_seq:
            if i != 0:
                address += self.decode_vocab[i]
        return address

    @staticmethod
    def make_prediction(address: Any):
        """make prediction on address"""
        return usaddress.parse(address)

    def predict(self):
        """make predictions for each component class in address"""
        # make prediction
        prediction = self.make_prediction(self.address)

        # temporary vars
        components = {"street": '', "postcode": '', "number": '', "region": '', "unit": '', "city": ''}

        # create address component packet
        for comp_tup in prediction:
            if comp_tup[1] == "AddressNumber":
                sub_comp = comp_tup[0].replace(",", "")
                sub_comp = sub_comp.replace(" ", "")
                components['number'] += f'{sub_comp}'
            elif "StreetName" in comp_tup[1]:
                sub_comp = comp_tup[0].replace(",", "")
                sub_comp = sub_comp.replace(" ", "")
                components['street'] += f'{sub_comp} '
            elif "PlaceName" in comp_tup[1]:
                sub_comp = comp_tup[0].replace(",", "")
                sub_comp = sub_comp.replace(" ", "")
                components['city'] += f'{sub_comp} '
            elif comp_tup[1] == 'StateName':
                sub_comp = comp_tup[0].replace(",", "")
                sub_comp = sub_comp.replace(" ", "")
                components['region'] += f'{sub_comp}'
            elif comp_tup[1] == 'AddressNumberSuffix' or comp_tup[1] == 'AddressNumberPrefix':
                sub_comp = comp_tup[0].replace(",", "")
                sub_comp = sub_comp.replace(" ", "")
                components['unit'] += f'{sub_comp}'
            elif comp_tup[1] == 'ZipCode':
                sub_comp = comp_tup[0].replace(",", "")
                sub_comp = sub_comp.replace(" ", "")
                components['postcode'] += f'{sub_comp}'

        return list(components.values())

    def correct_predictions(self):
        """correct the predictions by TFIDF text similarity"""

        self.finished_predicts = self.predict()

        for prediction in self.finished_predicts.keys():
            # get length of prediction and set up similarity index
            pred_len: int = len(self.finished_predicts[prediction].split(' '))

            similarity_scores: list = []

            # split original address into n parts where n = pred_len
            address_arr: list = self.cleaned_address.split(' ')

            # iterate through address arr
            for i in range(0, len(address_arr)-pred_len):
                # comparison strings
                comparison_comps = ' '.join(address_arr[i:i+pred_len])

                # find similarity and append tuple packet
                similarity = float(SequenceMatcher(None, comparison_comps, self.finished_predicts[prediction]).ratio())
                similarity_scores.append((similarity, comparison_comps))

            # get the most similar string
            similarity_scores.sort()
            self.finished_predicts[prediction] = similarity_scores[-1][1]

        return self.finished_predicts


class LearnParse(ABC):
    """deep learning strategy base model"""

    @abstractmethod
    def parsing_strategy(self, address: str) -> str:
        """"address parsing models here"""
        pass


class MLStrategy(LearnParse):

    @staticmethod
    def parsing_strategy(address: str) -> dict:
        """call predict method in prediction class"""
        strat_obj = CustomPredictFull(address)
        return strat_obj.predict()


"""-------------------------------------- Response Packet Strategy ------------------------------------"""


# noinspection PyCompatibility
class ResponsePacketDataClass(BaseModel):
    """sub-response storage data model"""
    response_packet: Optional[List] = []
    supplied_packet: Optional[List] = []


class ResponseFormStrategy(ABC):
    """response form strategy abstract base class"""

    @abstractmethod
    def response_packet_strategy(self, address_parts: Dict, address: Union[str, None],
                                 coordinates: List[Union[int, float]], accuracy: Union[int, float]) -> dict:
        """define response packet polymorphism method"""
        pass


class SuccessPacket(ResponseFormStrategy):
    """successful return packet"""

    def response_packet_strategy(self, address_parts: Dict, address: Union[str, None],
                                 coordinates: List[Union[int, float]], accuracy: Union[int, float]) -> dict:
        """
        :param address_parts:
        :param address:
        :param coordinates:
        :param accuracy:
        """

        local_response_model = ResponsePacketDataClass()

        response = {'address_parts': address_parts, 'address': address,
                    'coordinates': coordinates, 'accuracy': accuracy}
        supplied = {'address': address_parts, 'formatted_address': address}

        local_response_model.response_packet.append(response)
        local_response_model.supplied_packet.append(supplied)

        return local_response_model.dict()


class EmptyGeocodingCase(ResponseFormStrategy):
    """empty forward geocoding (no query output)"""

    def response_packet_strategy(self, address_parts: Dict, address: Union[str, None],
                                 coordinates: List[Union[int, float]], accuracy: Union[int, float]) -> dict:
        """create an empty geocode response for error cases"""

        local_response_model = ResponsePacketDataClass()

        response = {'address_parts': address_parts, 'address': address,
                    'coordinates': [], 'accuracy': accuracy}
        supplied = {'address': address_parts, 'formatted_address': address}

        local_response_model.response_packet.append(response)
        local_response_model.supplied_packet.append(supplied)

        return local_response_model.dict()


class ErrorCase(ResponseFormStrategy):
    """error case (query returns 505 internal error"""

    def response_packet_strategy(self, address_parts: Dict, address: Union[str, None],
                                 coordinates: List[Union[int, float]], accuracy: Union[int, float]) -> dict:
        """Internal Server Error response cases"""

        local_response_model = ResponsePacketDataClass()

        response = {'address_parts': address_parts, 'address': 'Address Formatting Error',
                    'coordinates': [], 'accuracy': accuracy}
        supplied = {'address': address_parts, 'formatted_address': address}

        local_response_model.response_packet.append(response)
        local_response_model.supplied_packet.append(supplied)

        return local_response_model.dict()


def DataPacketHandler(strategy: ResponseFormStrategy, address_parts: Dict, address: Union[str, None],
                      coordinates: List[Union[int, float]], accuracy: Union[int, float]) -> dict:
    """handle data packet creation"""
    return strategy.response_packet_strategy(address_parts, address, coordinates, accuracy)


class BatchPackets:

    """handle all the batch packaging for batch endpoints"""

    def __init__(self):
        self.global_batch_response_model = ResponsePacketDataClass()

    def BatchPacketHandler(self, response_packet: Union[List, None], supplied_packet: Union[List, None]) -> dict:
        """handle the batch packets and extend to response/supplied models"""

        self.global_batch_response_model.response_packet.extend(response_packet)
        self.global_batch_response_model.supplied_packet.extend(supplied_packet)

        return self.global_batch_response_model.dict()


"""---------------------------------------Spreadsheet Batch Strategy------------------------------------------------"""


class BatchStrategy(ABC):
    """batch strategy abstract base class"""

    @abstractmethod
    def batch_strategy(self) -> None:
        """polymorphism method init"""
        pass


class SpreadsheetStrategy(BatchStrategy):
    """spreadsheet"""

    def batch_strategy(self) -> None:
        """batch strategy func"""
        pass


class BatchEndpointStrategy(BatchStrategy):
    """batch"""

    def batch_strategy(self) -> None:
        """batch strategy func"""
        pass


class SingularEndpointStrategy(BatchStrategy):
    """regular/singular"""

    def batch_strategy(self) -> None:
        """batch strategy func"""
        pass
