import pydantic
from typing import List, Dict, Iterable, Optional, Any, Union, Callable
import collections
from abc import ABC, abstractmethod


"""---------------------Generator and Iterator Handler-----------------"""


# noinspection PyCompatibility
class GeneratorStorage(pydantic.BaseModel):
    """general object dataclass for generators"""
    generator_arr: Optional[Any] = collections.deque([])
    iterable_arr: Optional[List] = []


GeneratorStorage = GeneratorStorage()


def format_address(document: Dict) -> Union[str, None]:
    """format address based on US standards"""
    if document['unit'] == '':
        primary_address_search = document['number'] + ' ' + document['street'] + ', ' + document['region'] + ', ' + \
                                 document['postcode']
    else:
        primary_address_search = document['number'] + ' ' + document['street'] + ', ' + document['region'] + ', ' + \
                                 document['postcode'] + ', ' + document['unit']

    return primary_address_search


def clean_document(document: Dict) -> dict:
    """clean the document from elasticsearch or pymongo"""
    try:
        return document['_source']
    except KeyError:
        return document

"""------------------------Generator strategy handlers-----------------------"""


class GeneratorInternalStrategy(ABC):
    """abstract base class for generator/iterator strategy pattern"""
    @abstractmethod
    def generator_runner(self, iterable: Iterable, parser: Callable) -> List:
        """run generator"""
        pass


class RegularGenerator(GeneratorInternalStrategy):
    """ordinary generator algorithm"""

    def generator_runner(self, iterable: Iterable, parser: Callable) -> List:
        """run generator function"""

        # clear the generator storage first
        GeneratorStorage.generator_arr.clear()

        for document in iterable:
            # clean document
            document = clean_document(document)

            # coordinate parsing
            longitude, latitude = parser(document)

            # avoid blank street names
            if document['properties']['street'] != '' and document['properties']['number'] != '':
                address = format_address(document['properties'])
                micro_packet = {"address": address, "latitude": latitude, "longitude": longitude}

                # add to generator iterable
                GeneratorStorage.generator_arr.append(micro_packet)

            else:
                continue

        return GeneratorStorage.generator_arr


class SpecializedGeneratorPN32(GeneratorInternalStrategy):
    """Specialized Generator for other output types"""

    def generator_runner(self, iterable: Iterable, parser: Callable) -> List:
        """run specialized generator with diff. formatting"""

        # clear the generator first
        GeneratorStorage.generator_arr.clear()

        for packet in iterable:
            # clean packet
            packet = clean_document(packet)

            # make sure there are no blank streets
            if packet['properties']['street'] != '' and packet['properties']['number'] != '':

                # get coordinates from encapsulated parser callable
                latitude, longitude = parser(packet)

                # create the data packet with the pydantic model base
                data_packet = {'property_details': {'number': packet['properties']['number'],
                                                    'street': packet['properties']['street'],
                                                    'district': packet['properties']['district'],
                                                    'state': packet['properties']['region'],
                                                    'postcode': packet['properties']['postcode']},
                               'location': dict(zip(['latitude', 'longitude'], [latitude, longitude]))}

                # add to generator iterable
                GeneratorStorage.generator_arr.append(data_packet)

            else:
                continue

        return GeneratorStorage.generator_arr


class SpecializedGeneratorDN32(GeneratorInternalStrategy):
    """generator strategy for DN32 setting (density query)"""

    def generator_runner(self, iterable: Iterable, parser: Callable) -> List:
        """DN32 generator function"""

        # clear first
        GeneratorStorage.generator_arr.clear()

        for packet in iterable:
            # clean document from BSON blob
            packet = clean_document(packet)

            # append only coordinates for density search
            GeneratorStorage.generator_arr.append(parser(packet))

        return GeneratorStorage.generator_arr


"""iterator strategies here: regular and PR32 method"""


class IteratorInternalStrategies(ABC):
    """abstract base class for iterator strategy pattern"""
    @abstractmethod
    def iterator_parse(self, handler_obj: Any, parser: Callable) -> List:
        """base function for iterator strategies"""
        pass


class RegularIterator(IteratorInternalStrategies):
    """inherited subclass for regular iterator"""
    def iterator_parse(self, handler_obj: Any, parser: Callable) -> List:
        """regular iterator function"""

        # clear storages
        GeneratorStorage.iterable_arr.clear()
        GeneratorStorage.generator_arr.clear()

        for document in handler_obj:

            # clean document
            document = clean_document(document)

            # make sure there are no empty street or numbers
            if document['properties']['street'] != '' and document['properties']['number'] != '':
                # format the address
                address = format_address(document['properties'])

                # extract coordinates
                latitude, longitude = parser(document)

                # create data packet for append purposes
                micro_packet = {"address": address, "latitude": latitude, "longitude": longitude}

                # dataclass storage iterable_arr append method
                GeneratorStorage.iterable_arr.append(micro_packet)
            else:
                continue

        return GeneratorStorage.iterable_arr


class IteratorStrategyPR32(IteratorInternalStrategies):
    """specialized iterator method"""

    def iterator_parse(self, handler_obj: Any, parser: Callable) -> List:
        """PR32 iterator function"""

        # clear storages
        GeneratorStorage.iterable_arr.clear()
        GeneratorStorage.generator_arr.clear()

        for packet in handler_obj:
            # clean packet
            packet = clean_document(packet)

            # create data packet
            data_packet = {'property_details': {'number': packet['properties']['number'],
                                                'street': packet['properties']['street'],
                                                'district': packet['properties']['district'],
                                                'state': packet['properties']['region'],
                                                'postcode': packet['properties']['postcode']},
                           'location': dict(zip(['latitude', 'longitude'], parser(packet)))}

            GeneratorStorage.iterable_arr.append(data_packet)

        return GeneratorStorage.iterable_arr


"""----------------------------manage the generator and iterator methods------------------------------"""


class RunStrategy:
    """generator director class"""

    def __init__(self, parser, *args):
        self.parser = parser
        self.generator_strategy = args[0]
        self.iterator_strategy = args[1]

    def run_generator_internal(self, BSON_obj: Iterable) -> List:
        """run the generator, integrated strategy"""
        generator_output = self.generator_strategy.generator_runner(BSON_obj, self.parser)
        return generator_output

    def run_iterator_internal(self, BSON_obj: Iterable) -> List:
        """run iterator integrated strategy"""
        iterable_output = self.iterator_strategy.iterator_parse(BSON_obj, self.parser)
        return iterable_output


def run_generator(BSON_obj: Iterable, strategy, parser: Callable) -> List:
    """generator runner"""
    RG = RunStrategy(parser, strategy, None)
    return RG.run_generator_internal(BSON_obj)


def run_iterator(BSON_obj: Iterable, strategy, parser: Callable) -> List:
    """iterator runner"""
    RG = RunStrategy(parser, None, strategy)
    return RG.run_iterator_internal(BSON_obj)
