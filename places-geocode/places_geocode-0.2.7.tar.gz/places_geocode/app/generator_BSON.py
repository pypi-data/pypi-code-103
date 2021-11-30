import time
import sys
import pymongo
import ssl
import collections
from typing import Callable, Any
sys.path.append('/places_geocode')
sys.path.append('/places_geocode/app/models')
from places_geocode.app.models.generator_model import *


class HandleArray:
    """handle iterable types with iterable/generator decision tree"""

    def __init__(self, array):
        self.array = array
        self.generator_arr = collections.deque([])
        self.iterable_arr = []

    def __repr__(self):
        return str(self.iterable_arr)

    def __len__(self):
        return len(self.array)

    def __iter__(self):
        return iter(self.array)

    def __add__(self, arr, **kwargs):
        if len(kwargs) > 0:
            if kwargs['option'] == 'GEN':
                if isinstance(arr, list) or isinstance(arr, dict):
                    self.generator_arr.append(arr)
                else:
                    raise Exception('Error Occurred in Generator BSON conversion')
            else:
                if isinstance(arr, list) or isinstance(arr, dict):
                    self.iterable_arr.append(arr)
                else:
                    raise Exception('Error Occurred in Iterator BSON conversion')
        else:
            if isinstance(arr, list) or isinstance(arr, dict):
                self.iterable_arr.append(arr)
            else:
                raise Exception('Error Occurred in Iterator BSON conversion')

    def __get__(self):
        return self.iterable_arr

    def get_iter_array(self):
        """return the iterable array"""
        return self.iterable_arr

    @staticmethod
    def _generator(array):
        """generator core internals"""
        for doc in array:
            yield doc

    @staticmethod
    def format_address(document):
        """format the address returned from iterator or generator"""
        document = document['properties']
        if document['unit'] == '':
            primary_address_search = document['number'] + ' ' + document['street'] + ', ' + document['region'] + ', ' + \
                                     document['postcode']
        else:
            primary_address_search = document['number'] + ' ' + document['street'] + ', ' + document['region'] + ', ' + \
                                     document['postcode'] + ', ' + document['unit']

        return primary_address_search

    def run_generator(self, strategy: Callable, parser: Callable):
        """run generator function"""

        # create the BSON-generator object
        BSON_obj = self._generator(self.array)

        # run the generator model based on the strategies in generator_models.py
        return run_generator(BSON_obj, strategy, parser)

    def run_iterator(self, strategy: Callable, parser: Callable):
        """run iterator function, considering strategy chosen"""
        return run_iterator(self.array, strategy, parser)


def handler_func(array, strategy: Any, parser: Callable, **kwargs):
    """director function for the generator algorithms"""

    # start the timer for runtime analysis
    start = time.perf_counter()

    # init the handler
    handler = HandleArray(array)

    try:
        # generator
        if kwargs['option'] == 0:
            # run handler generator function with current strategy
            return handler.run_generator(strategy, parser)

        # iterator
        elif kwargs['option'] == 1:
            # run iterator
            return handler.run_iterator(strategy, parser)

    except AttributeError:
        raise Exception("Incompatible Strategy Chosen")


# testing function for the generator functionality
def test_function():
    client = pymongo.MongoClient(
        'mongodb+srv://martin_mashalov:Barca2004!@locationpoints.wi1dk.mongodb.net/test', maxPoolSize=125,
        ssl_cert_reqs=ssl.CERT_NONE)
    db = client['PeekDB']
    geoCoords = db['propLocations']

    query = geoCoords.find({})[:180]

    try:
        return handler_func(query, RegularIterator(), option=0)
    except AttributeError:
        raise Exception("Incompatible Strategy Chosen")
