"""backend functionality to PeekGeo"""
from abc import ABCMeta, abstractmethod
# from enum import Enum
from pydantic import BaseModel
import sys
sys.path.append("app/")
import pymongo
from pymongo.errors import OperationFailure
from typing import List, Union, Any, Type, Dict, Tuple, Optional, Callable, Iterable
import ssl
from bson import BSON

# elasticsearch imports
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError, RequestError
from configparser import ConfigParser

# scientific packages
import numpy as np
from scipy.spatial import ConvexHull

# common built-ins
from places_geocode.app.generator_BSON import handler_func
# noinspection PyCompatibility
import asyncio
# noinspection PyCompatibility
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from math import pi, sin, cos, sqrt, atan2, radians
import sys
from threading import Thread
from collections import OrderedDict

# data model imports
from places_geocode.app.models import density_models, common_models, reverse_models, forward_models, generator_model, certainty_models, \
    unit_conversion_model, correction_parse_models

# cython modules import
from places_geocode.app.CythonOperations import spreadsheet_c, \
    reverse_spreadsheet, \
    TFIDF_max, \
    null_parameters, \
    certainty_search, \
    radius_arr, TFIDF_max_elastic


# ----------------------DataClasses Here---------------------


# noinspection PyTypeChecker
class BuildObjs:
    """builder for the mongo objects"""

    def __init__(self):
        self.set_up_objs = dict(database=None, common_model=None, client=None)

    @staticmethod
    def _create_max_size_model(max_size: int):
        """add max_size_model to the common models object dataclass"""
        common_model = common_models.ObjModel(maxSize=max_size)
        return common_model

    @staticmethod
    def _create_client(max_size: int):
        """make the mongo client"""
        client = pymongo.MongoClient("mongodb+srv://martin_mashalov:Barca2004!@locationpoints.wi1dk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority&authSource=admin")
        return client

    @staticmethod
    def _create_connection(database, collection, client):
        """create the database connection to the collection specified"""
        db = client[database]
        collection = db[collection]

        return db, collection

    def set_max_size(self, *args):
        """set the max_size in the dataclass model"""

        # set the maxsize and create common model
        self.set_up_objs['common_model'] = self._create_max_size_model(args[0])

    def set_client(self):
        """set the client object"""

        # get the client object
        self.set_up_objs['client'] = self._create_client(self._create_max_size_model(100).maxSize)

    def build_connection(self, database, collection):
        """build the database connection with the builder pattern"""

        # get the database, collection objects, using client
        self.set_up_objs['database'], self.set_up_objs[collection] = self._create_connection(database, collection,
                                                                                             self.set_up_objs['client'])


def DirectorGeneralObjs(database: str, collections: Tuple[str], *args) -> Dict:
    """direct the building process for mongodb object creation"""
    builder_direct = BuildObjs()

    # set for building mongo object
    builder_direct.set_max_size(args[0])
    builder_direct.set_client()
    builder_direct.build_connection(database, collections[0])
    builder_direct.build_connection(database, collections[1])
    return builder_direct.set_up_objs


# noinspection PyTypeChecker
class BuildElasticSearch:
    """build elasticsearch objects"""

    def __init__(self):
        self.elastic_settings = ElasticModel()
        self.set_up_objs = dict(connection=None)
        self.config = ConfigParser()
        self.config.read('places_geocode/app/example.ini')

    def create_connection(self):
        """create the connection for locations"""
        elastic_con = Elasticsearch(
            cloud_id=self.config['ELASTIC']['cloud_id'],
            http_auth=(self.config['ELASTIC']['user'], self.config['ELASTIC']['password'])
        )
        self.set_up_objs['connection'] = elastic_con


def ElasticBuildDirector(*opt):
    """elasticsearch connection/object builder"""
    builder = BuildElasticSearch()
    builder.create_connection()
    return builder.set_up_objs


class ThreadWithReturnValue(Thread):
    """manual implementation of threading for multiple functions made simple"""

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        if kwargs is None:
            kwargs = {}
        self._return = None

    def run(self):
        """run the thread functionality"""
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, *args):
        """thread join method"""
        Thread.join(self, *args)
        return self._return


"""--------------------------------Forward Geocoding Data Model------------------------------------"""


# noinspection PyCompatibility
class LocalDataClass(BaseModel):
    """basic parameters for the forward geocoding functionality"""
    dflib_hyperparameter: Optional[int] = 1
    similarity_threshold: Optional[float] = 0.5
    batch_size: Optional[int] = 125
    small_batch_maximum: Optional[int] = 4
    spreadsheet_batch_size: Optional[int] = 10000
    optimal_radius: Optional[int] = 10
    common_streets: Optional[List[str]] = ['road', 'street', 'avenue', 'drive', 'lane', 'route', 'court', 'west',
                                           'east', 'north', 'south', 'place', 'state', 'boulevard', 'county', 'way',
                                           'square', 'pl', 'dr', 'bl']
    forward_geocode_street_method: Optional[Callable] = lambda street: street.upper()
    confidence_index: Optional[Dict[float, float]] = {0.0: 1.0, 1.0: 1.0, 10.0: 0.9, 100.0: 0.8, 250.0: 0.7,
                                                      1000.0: 0.6, 1000.99: 0.5}
    confidence_algorithm: Optional[Callable] = certainty_search
    default_autocomplete_algorithm: Optional[Callable] = None
    radius_delta_null: Optional[float] = 0.001

    # assign builder
    builder_utility: Optional[Callable] = ElasticBuildDirector


class RunModel(BaseModel):
    """pydantic model for running specifics"""
    engine: Optional[str] = 'elastic'


class ElasticModel(BaseModel):
    """elasticsearch base model for storing settings"""
    elastic_index_poi: Optional[str] = 'proplocations'
    elastic_index_users: Optional[str] = 'apiusers'
    uri: Optional[str] = 'PlacesDB:ZWFzdHVzMi5henVyZS5lbGFzdGljLWNsb3VkLmNvbTo5MjQzJGU3NDhmMjYwOTUzNTQ1NGI5ZjkxYTBjM2ViZjg0NGUyJGMyZjRiYTg1NjdkMjQ5NjE4NGJjODg4NjJlYmM5NjY5'


# ---------------------Functional Classes Here --------------------------


class CommonUtilities:
    """generic utilities used throughout entire backend script placed here"""

    # generic conversion functions including distance to radians conversion
    utility_model = common_models.CommonUtilityModel()
    feet_meter = lambda self, x: x * 0.3048
    feet_mi = lambda self, x: x / 5280
    feet_yd = lambda self, x: x / 3
    feet_km = lambda self, x: x * 0.0003048
    meter_feet = lambda self, x: x * 3.28084
    meter_km = lambda self, x: x / 1000
    km_meter = lambda self, x: x * 1000
    distance_radians = lambda self, x: x / self.utility_model.earth_radius
    mi_feet = lambda self, x: x * 5280
    proportion_prop_measurement = lambda self, x: (500 * self.radius) // x

    # generator tools/hash mapping
    generator_mapping = {'pymongo': common_models.parse_coordinates_pymongo,
                         'elastic': common_models.parse_coordinates_elastic}

    @staticmethod
    def determine_batch_size(arr: List[Any]) -> int:
        """determine batch size of concurrency operation"""

        if len(arr) == 0:
            return 0
        elif len(arr) == 1:
            return 1
        else:
            if 1 < len(arr) <= 5:
                return 3
            elif 5 < len(arr) < 10:
                return 5
            elif 10 <= len(arr) < 20:
                return 5
            else:
                return 10

    @staticmethod
    def divide_arr(arr: List[Any], n: int) -> Any:
        """divide an arr into n different subarrays"""

        k, m = divmod(len(arr), n)

        # division of array is done at this stage, multiple nested array, dim(arr)=2
        return (arr[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

    @staticmethod
    def format_date(date):
        """format string dates"""

        # parse the date string here
        date_info = date.split(' ')
        final_date = date_info[0]
        time_info = date.split(' ')
        final_time = time_info[1]

        # return the final_date, final_time pair in one list obj
        return [final_date, final_time]

    @staticmethod
    def _format_address(unit, street, number, state, postcode, city, single):
        """format the address properly according to US Census regulations"""

        # if there is not unit
        if single:
            # return the singular home response here
            address = f"{number} {street}, {city}, {state}, {postcode}"
        else:
            # if there is a unit, structure differently
            address = f"{number} {street}, {city}, {state}, {postcode}, {unit}"
        return address

    @staticmethod
    def convex_hull(points: List[List[Union[float, int]]]) -> Union[float, int]:
        """calculate the convex hull of a set of points"""

        # type checker for points to avoid runtime errors
        convex_hull_model = common_models.PointsModel(coordinates=points)

        # find the hull and calculate the area
        hull = ConvexHull(convex_hull_model.coordinates)
        return hull.area

    def process_iterable(self, results: Any, first_strategy: Callable, second_strategy: Callable) -> List:
        """process generator output based on the threshold specified in the Base pydantic data model"""
        start = time.perf_counter()

        # get the length of the results
        try:
            # pymongo version
            result_len = len(list(results.clone()))
        except AttributeError:
            # elastic version
            result_len = len(results)

        if result_len > common_models.CommonUtilityModel().generator_threshold:
            # generator
            return handler_func(results, first_strategy(), self.generator_mapping[RunModel().engine], option=0)
        else:
            # iterator
            return handler_func(results, second_strategy(), self.generator_mapping[RunModel().engine], option=1)

    @staticmethod
    def clean_properties_collection(properties: dict) -> dict:
        """clean out unnecessary parts of the address properties index"""

        # remove unnecessary keys
        try:
            for key in ['hash', 'Realtor_ID', 'id', 'district']:
                del properties[key]

            # preserve the order for later iteration
            return OrderedDict(properties)
        except KeyError:
            for key in ['id', 'district']:
                del properties[key]
            return OrderedDict(properties)

    # noinspection PyTypeChecker
    def calc_distance(self, document, end: list, setting: str) -> Union[float, int]:
        """calculate distance between two coordinates"""

        try:
            start = document['location']['coordinates']
        except TypeError:
            start = self.generator_mapping[setting](document)

        lat1, lon1 = start
        lat2, lon2 = end

        lat1, lon1 = radians(lat1), radians(lon1)
        lat2, lon2 = radians(lat2), radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return self.utility_model.earth_radius * c


# noinspection PyCompatibility
class ManageDatabaseGeneral(BuildObjs):
    """general database management functionality, especially for code clean up"""

    def __init__(self, database: str, collections: Tuple) -> None:
        super().__init__()
        self.database_objs = DirectorGeneralObjs(database, collections, 100)

    def add_search_index(self):
        """index creation function, add all other indexes here"""
        self.database_objs[common_models.ObjModel.current_geographic_collection].create_index(
            [('location.coordinates.0', 1)])
        self.database_objs[common_models.ObjModel.current_geographic_collection].create_index(
            [('location.coordinates.1', 1)])

        # print the existing indexes
        self._manage_indexes()

    # manage the indexes of the main properties dataset
    def _manage_indexes(self):
        # get the indexes on the database
        indexes = self.database_objs[common_models.ObjModel.current_geographic_collection].list_indexes()
        # print them here for debugging purposes
        for index in list(indexes):
            print(index)


# noinspection PyCompatibility,PyUnresolvedReferences
class DensityRadius(BuildObjs, CommonUtilities):
    """density backend functionality and database querying algorithms"""

    def __init__(self, database, collection):
        super().__init__()

        # create global runner model
        self.runner_model = RunModel()
        self.global_settings = LocalDataClass()

        # call the builder/director function for SetUpObjs, make the geoCoords collection available, max_size=100
        self.database_objs = self.global_settings.builder_utility(database, collection, 100)

        # initialize basic schema for density computations
        self.density_schema = density_models.DensitySchema()

        # unit conversion algorithms collection here
        self.unit_algo_index_input: dict = dict(zip(['ft', 'mi', 'm', 'yd', 'km'],
                                                    [None, self.mi_feet, self.meter_feet, None,
                                                     *[self.km_meter, self.meter_feet]]))
        self.unit_algo_index_output: dict = dict(zip(['ft', 'mi', 'm', 'yd', 'km'],
                                                     [None, self.feet_mi, self.feet_meter, self.feet_yd, self.feet_km]))

    @staticmethod
    def compute_area(radius: Union[int, float]) -> Union[float, int]:
        """compute area of a given area (simple formula)"""
        area = pi * (radius ** 2)
        return area

    def _iterative_calc(self, nearest: List, radius: Union[int, float]) -> Union[int, float]:
        """iterative density calculator"""
        density_schema = density_models.DensitySchema(radius=radius, region_area=self.compute_area(radius))
        for _ in nearest:
            density_schema.iterative_counter += 1 / density_schema.region_area

        return density_schema.iterative_counter

    def _convert_units(self, unit_input: str, radius: Union[float, int], **input_type) -> Union[float, int]:
        """Convert input units to feet to standardize"""

        # create the state machine object
        conversion_state_machine = unit_conversion_model.UnitConversionsToFeet(radius)

        # unit conversion events defined here
        unit_conversion_index_input: dict = dict(
            zip(['ft', 'mi', 'm', 'yd', 'km'], [conversion_state_machine.to_ft,
                                                conversion_state_machine.to_mi,
                                                conversion_state_machine.to_m,
                                                conversion_state_machine.to_yd,
                                                conversion_state_machine.to_km]))

        unit_conversion_index_output: dict = dict(
            zip(['ft', 'mi', 'm', 'yd', 'km'], [conversion_state_machine.to_ft_output,
                                                conversion_state_machine.to_mi_output,
                                                conversion_state_machine.to_m_output,
                                                conversion_state_machine.to_yd_output,
                                                conversion_state_machine.to_km_output]))

        # compute conversion of unit types
        try:
            # decide between input/output type
            if input_type['input'] == 'input':
                return unit_conversion_model.state_machine_conversion_controller(
                    unit_conversion_index_input[unit_input],
                    conversion_state_machine,
                    self.unit_algo_index_input[unit_input]
                )
            elif input_type['input'] == 'output':
                return unit_conversion_model.state_machine_conversion_controller(
                    unit_conversion_index_output[unit_input],
                    conversion_state_machine,
                    self.unit_algo_index_output[unit_input]
                )
        except (KeyError, BufferError):
            raise BrokenPipeError

    def run_2dSphere(self, start: List[float], radius: Union[float, int], unit='m') -> List:
        """Handle 2dSphere queries in MongoDB for GIS object counting"""
        # using 2dSphere index

        try:
            # find connection to elasticsearch index
            elastic_connection = self.database_objs['connection']

            # create query request body
            body = {
                "size": 1000,
                "query": {
                    "bool": {
                        "filter": {
                            "geo_distance": {
                                "distance": f"{radius+self.global_settings.radius_delta_null}{unit}",
                                "location": f"{start[0]}, {start[1]}"
                            }
                        }
                    }
                },
                "sort": {
                    "_geo_distance": {
                        "location": f"{start[0]}, {start[1]}",
                        "order": "asc"
                    }
                }
            }

            try:
                nearest = elastic_connection.search(index=common_models.ObjModel().current_geographic_collection,
                                                              body=body)['hits']['hits']
            except (NotFoundError, RequestError):
                raise BrokenPipeError

        except KeyError:
            nearest = self.database_objs[common_models.ObjModel().current_geographic_collection].find({"location": {
                "$geoWithin": {
                    "$centerSphere": [start, self.distance_radians(self.feet_meter(radius))]}}})

        return nearest

    async def load_radius(self, start: List[float], radius: int) -> List:
        """load radius backend functionality"""
        try:
            nearest_poi: Any = self.run_2dSphere(start, radius)
            array = self.process_iterable(nearest_poi, generator_model.RegularGenerator,
                                          generator_model.RegularIterator)
            return array
        except OperationFailure:
            raise BrokenPipeError

    def manual_identify_density(self, coordinates: List[float], radius: Union[float, int], unit_in: str) -> Union[float, int]:

        """Identify density with 2dSphere technique"""

        # convert to feet first
        radius_processed: float = self._convert_units(unit_in, radius, input='input')

        # handle radius object for density gathering
        try:
            radius_task: Any = self.run_2dSphere(coordinates, radius_processed, 'ft')
        except OperationFailure:
            raise BrokenPipeError

        # get the density comp
        return self._iterative_calc(radius_task, radius)

    def _custom_density_query(self, query_value, strategy, generator_option):
        """create the custom density query"""
        try:
            # elastic version
            elastic_connection = self.database_objs['connection']
            points, point_count = density_models.strategies_main(common_models.ObjModel().current_geographic_collection,
                                                                 query_value, strategy,
                                                                 generator_option,
                                                                 self.generator_mapping[self.runner_model.engine],
                                                                 elastic_connection)

        except (IndexError, KeyError):
            # pymongo version
            points, point_count = density_models.strategies_main(
                self.database_objs[common_models.ObjModel().current_geographic_collection], query_value, strategy,
                generator_option, self.generator_mapping[self.runner_model.engine]
            )

        return points, point_count

    def custom_density(self, strategy, query_value):
        """get density based on custom metrics such as postcode, city, and region/state"""

        # get points and point counts by inputting correct density strategy (state, postcode, city)
        points, point_count = self._custom_density_query(query_value, strategy,
                                                         generator_model.SpecializedGeneratorDN32)

        if point_count > 0:
            # convex hull results
            area = self.convex_hull(points)

            # calculate density
            density = point_count / area
            return density
        else:
            return 0

    async def density_factory(self, decision_parameter: Union[str, None], **kwargs):
        """factory method for separating objects for custom density and generic density computations"""
        if decision_parameter == 'custom':
            # get relevant data for custom method
            strategy = kwargs['strategy']
            query_value: Any = kwargs['query_value']

            # create the coroutine object
            custom_density_result = self.custom_density(strategy, query_value)
            return custom_density_result
        else:
            # get relevant data for manual/generic density search
            coordinates: List[float] = kwargs['coordinates']
            radius: Union[int, float] = kwargs['radius']
            unit_in: str = kwargs['unit_in']

            # create and handle coroutines for generic method
            generic_density_result = self.manual_identify_density(coordinates, radius, unit_in)

            return generic_density_result


# noinspection PyCompatibility,PyUnresolvedReferences
class Convex(BuildObjs, CommonUtilities):
    """convex searches implementation"""

    def __init__(self, database, collection):
        super().__init__()

        # create global settings models
        self.runner_model = RunModel()
        self.global_settings = LocalDataClass()

        # builder/director function for general objects
        self.database_objs: dict = self.global_settings.builder_utility(database, collection, 100)

    @staticmethod
    def get_polygon_area(lats, longs):
        """find the area of the polygon involved"""
        return (0.5 * np.abs(np.dot(lats, np.roll(longs, 1)) - np.dot(longs, np.roll(lats, 1)))) * 6371

    @staticmethod
    def _fix_elastic_edges(edges):
        """correct edges for elasticsearch geo-shape query purposes"""

        # create edges container
        rev_edges: list = []

        for edge in edges[0]:
            rev_edges.append(f"{edge[0]}, {edge[1]}")

        return rev_edges

    async def _polygon_search(self, edges: List) -> Any:
        """polygon/convex search"""
        try:
            try:
                # pymongo version
                query = self.database_objs[common_models.ObjModel().current_geographic_collection].find(
                    {'location': {'$geoWithin': {'$geometry': {'location.type': 'Point', "coordinates": edges}}}})
            except (KeyError, AttributeError):
                # elastic search version

                body = {
                    "size": 5000,
                    "query": {
                        "bool": {
                            "must": {
                                "match_all": {}
                            },
                            "filter": {
                                "geo_polygon": {
                                    "location": {
                                        "points": self._fix_elastic_edges(edges)
                                    }
                                }
                            }
                        }
                    }
                }

                query = self.database_objs['connection'].search(index=common_models.ObjModel().current_geographic_collection,
                                                                body=body)['hits']['hits']

            return query
        except OperationFailure:
            raise BrokenPipeError

    async def convex_director(self, edges: List) -> List:
        """handle polygon/convex search strategy"""

        # create the connection branch
        convex_task = asyncio.create_task(self._polygon_search(edges))

        try:
            results = await convex_task

            # process the results
            processed_results: list = self.process_iterable(results, generator_model.SpecializedGeneratorPN32,
                                                            generator_model.IteratorStrategyPR32)

            return processed_results

        except OperationFailure:
            raise BrokenPipeError('Edges Crossed')


"""---------------------------------Custom Exceptions----------------------------------------------------------------"""


# noinspection PyCompatibility
class CallLimitExceeded(Exception):
    """call limit exception custom class"""

    def __init__(self, batch_size: int, message: str, status_code: int) -> None:
        self.batch_size = batch_size
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# noinspection PyCompatibility
class SpreadSheetLimit(Exception):
    """spreadsheet call limit class"""

    def __init__(self, batch_size: int, message: str, status_code: int) -> None:
        self.batch_size = batch_size
        self.message = message
        self.status_code = status_code
        super().__init__(message)


"""---------------------------------Forward Geocoding Functionality--------------------------------------------------"""


# noinspection PyCompatibility,PyUnresolvedReferences
class ForwardGeocoding(BuildObjs, CommonUtilities):
    """forward geocoding backend functionality"""

    def __init__(self, database, collections):
        super().__init__()

        # create background data models for forward geocoding and global settings
        self.threshold_model = LocalDataClass()
        self.runner_model = RunModel()
        self.forward_model = forward_models.ForwardGeocodingSchema(radius=self.threshold_model.optimal_radius)
        self.batch_handler = forward_models.BatchPackets()

        # create database objects with encapsulated builder pattern
        self.database_objs = self.threshold_model.builder_utility(database, collections, 100)

        # response and supply packet init here
        self.response_packet = []
        self.supplied_packet = []

        # geocoding ML model mapping
        self.forward_ml_model_mapping = {'pymongo': TFIDF_max, 'elastic': TFIDF_max_elastic}
        self.forward_coordinate_parse_mapping = {'pymongo': common_models.parse_coordinates_pymongo,
                                                 'elastic': common_models.parse_coordinates_elastic}

    @staticmethod
    def unit_check(address: Union[str, dict], address_type) -> bool:
        """check if it is a singular/multiple unit property"""

        if address_type == 1:
            unit_arr = address.split(',')
            return not not unit_arr == 5
        else:
            return not not len(address.keys()) == 5 or not not len(address.keys()) == 6

    @staticmethod
    def threading_utility(arguments: List[Union[float, str, int, List[Any]]], *functions) -> List[Any]:
        """provide threading functionality for arbitrary number of functions"""

        # set up max workers and submission storage array
        max_workers: int = len(functions)
        submission_arr: List[Any] = []
        output_concurrent: List[Any] = []

        # run concurrency algorithm
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for function, arg in zip(functions, arguments):
                submission = executor.submit(function, *arg)
                submission_arr.append(submission)

            # unpack the future objects, and map to names input, .result()
            for future_obj in as_completed(submission_arr):
                output_concurrent.append(future_obj.result())

        return output_concurrent

    # noinspection PyArgumentEqualDefault
    def _similarity_TFIDF(self, street_query: str, result: BSON) -> Tuple[Union[int, float], Optional[Any], Any]:
        """TFIDF similarity algorithm for geocode search"""

        return self.forward_ml_model_mapping[self.runner_model.engine].find_max_similarity(street_query, result)

    @staticmethod
    def _backsubstitute_null_parameters(original: Any, new_comparison: Any) -> Any:
        """substitute back parameters if there are nulls, with numpy arrays as inputs"""
        try:
            return null_parameters.minimize_nulls(original, new_comparison)
        except IndexError or ValueError:
            raise ValueError

    @staticmethod
    def create_dictionary(parsed_array, custom_street) -> Dict:
        """create address packet dictionary"""

        return {
            'postcode': parsed_array[1],
            'street': LocalDataClass().forward_geocode_street_method(custom_street),
            'number': parsed_array[2],
            'state': parsed_array[3],
            'unit': parsed_array[4],
            'city': parsed_array[-1]
        }

    @staticmethod
    def create_null_dictionary(original_parsed_array: Any):
        """create null address packet"""
        return {
            'postcode': original_parsed_array[1],
            'street': original_parsed_array[0],
            'number': original_parsed_array[2],
            'state': original_parsed_array[3],
            'unit': original_parsed_array[4],
            'city': original_parsed_array[-1]
        }

    def _layered_geocoder_concurrency(self, function: Callable, addresses: List[Union[List[str], str, None]]) -> List[list]:
        """higher level concurrency method that geocodes the individual address batches"""

        # map the results to the executor based on batch_size expressed in address and radius arr sizes
        with ThreadPoolExecutor() as executor:
            executor.map(function, addresses)
        return self.batch_handler.global_batch_response_model.dict()

    def _validate_batch_size_api(self, batch_size: int, strategy: Callable) -> Any:
        if strategy is not forward_models.SpreadsheetStrategy() and batch_size > self.threshold_model.batch_size:
            raise CallLimitExceeded(
                message="API Limit Exceeded",
                status_code=505,
                batch_size=batch_size
            )

    def _validate_spreadsheet_size(self, batch_size: int, strategy: Callable) -> Any:
        if strategy is forward_models.SpreadsheetStrategy() and batch_size > self.threshold_model.spreadsheet_batch_size:
            raise SpreadSheetLimit(
                message="Spreadsheet API Limit Exceeded",
                status_code=500,
                batch_size=batch_size
            )

    def _create_new_string_parse(self, original: Any, BSON_obj: Dict) -> Any:
        """parse the new address for later comparison"""
        try:
            # parse the property details
            try:
                # for pymongo
                property_details: dict = self.clean_properties_collection(BSON_obj['properties'])
            except KeyError:
                # for elasticsearch
                property_details: dict = self.clean_properties_collection(BSON_obj['_source']['properties'])

            # unpack address components from OrderedDict
            unit, number, street, city, region, postcode = property_details.values()

        except TypeError:
            raise BrokenPipeError

        # if ValueError is encountered from back-substitution, then return the original
        try:
            return self._backsubstitute_null_parameters(
                original,
                [street, postcode, number, region, unit, city]
            )

        except ValueError:
            return [street, postcode, number, region, unit, city]

    def _process_street_generic(self, street: str) -> str:
        """remove generic subphrases from street name"""
        new_street_tokens = [word for word in street if word not in self.threshold_model.common_streets]
        return ''.join(new_street_tokens)

    def _address_general_region_query(self, number: str, postcode: str) -> Any:
        """query based only on required number and postcode parameters"""

        try: # elasticsearch
            # find connection in database object map
            elastic_connection = self.database_objs['connection']

            # create query body
            body = {
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"properties.number": number}},
                            {"term": {"properties.postcode": postcode}}
                        ]
                    }
                }
            }

            # find search with multilayered -must query
            result = elastic_connection.search(index=common_models.ObjModel().current_geographic_collection, body=body)['hits']['hits']
        except (IndexError, KeyError):
            # pymongo search (and) query
            result = self.database_objs[common_models.ObjModel().current_geographic_collection].find(
                {'$and': [{'properties.number': str(number)}, {'properties.postcode': str(postcode)}]})

        return result

    def parse_addresses(self, address, **options) -> Union[list, Type[list], Tuple[str, str, str, str, str, str]]:
        """parse address into individual pieces based on US address convention"""

        unit_check = self.unit_check(address, options['parsing'])

        # parsed just cleans up the strings and returns them below
        if options['parsing'] == 0:
            return [address['street'], address['postcode'], address['number'], address['state'], address['unit'],
                    address['city']]

        # otherwise, a parsing is needed to separate them
        elif options['parsing'] == 1:
            try:
                return forward_models.MLStrategy.parsing_strategy(address)
            except ValueError:
                return ['', '', '', '', '', '']
        else:
            return ['', '', '', '', '', '']

    # DEPRECATED
    def _legacy_geocoding(self, address: str) -> Any:
        """legacy geocoder that works with direct Regex, currently out of production"""

        parser = self.parse_addresses(address, parsing='n')
        address_parts = {'postcode': parser[3], 'number': parser[4], 'region': parser[1], 'street': parser[0],
                         'unit': parser[-1], 'city': parser[2]}

        if address_parts['unit'] == 'Singular Home':
            address_parts = {'postcode': int(parser[3]), 'number': int(parser[4]), 'region': parser[1],
                             'street': parser[0], 'unit': '', 'city': parser[2]}

        postcode = address_parts['postcode']
        number = address_parts['number']
        region = address_parts['region']
        street = address_parts['street']
        unit = address_parts['unit']
        city = address_parts['city']

        def update_street(street, index):

            components = street.split(' ')

            components.pop()

            return ' '.join(components)

        def manual_debug_queries():
            filtered_collection = self.geoCoords.aggregate([{'$match': {
                '$and': [
                    {'postcode': postcode},
                    {'number': number},
                    {'region': region},
                    {'street': street},
                    {'unit': unit}
                ]}}])

            filtered_collection = self.geoCoords.aggregate([{'$match': {
                '$and': [
                    {'postcode': postcode},
                    {'number': number},
                    {'region': region},
                    {'street': street}]
            }}])

        # ------------------------------------------------------------------------------------------

        packed_query = self.geoCoords.aggregate([{
            '$facet': {
                'Query(1)': [{'$match': {'$and': [
                    {'postcode': postcode},
                    {'number': number},
                    {'region': region},
                    {'street': street},
                    {'unit': unit}
                ]}}],
                'Query(2)': [{'$match': {'$and': [
                    {'postcode': postcode},
                    {'number': number},
                    {'region': region},
                    {'street': street}]
                }}]
            }
        }])

        packed_query = [i for i in packed_query]

        if len(packed_query[0]['Query(1)']) == 0:
            if len(packed_query[0]['Query(2)']) == 0:
                packed_collection_check = 0
                filtered_collection = 0

            elif len(packed_query[0]['Query(2)']) != 0:
                packed_collection_check = 2
                filtered_collection = 1
            else:
                packed_collection_check = 0
                filtered_collection = 0

        else:
            packed_collection_check = 1
            filtered_collection = 1

        if packed_collection_check == 0:

            index = 1
            filtered_query = []

            while filtered_collection == 0 and street != '':
                street = update_street(street, index)

                filtered_query = self.geoCoords.aggregate([{'$match': {
                    '$and': [{'postcode': postcode}, {'number': number}, {'region': region}, {'street': street}]}}])

                filtered_collection = len([i for i in filtered_query])
                index += 1

            return [i for i in filtered_query]

        else:
            return [i for i in packed_query[0]['Query({})'.format(packed_collection_check)]]

        # faceted_array.append([{'$match': {'$and': [{'postcode': postcode}, {'number': number}, {'region': region}]}}])

    def updated_geocoding(self, address: str, address_type: int) -> dict:
        """FULL: 1, PARSED: 0 ---- address type decision index"""

        # list[street, postcode, number, region, unit, city]
        original_array = self.parse_addresses(address, parsing=address_type)

        try:
            # preliminary query results here
            street, result = self.threading_utility([[original_array[0]], [original_array[2], original_array[1]]],
                                                    self._process_street_generic,
                                                    self._address_general_region_query)

            # remove null output ex. street = '': to save runtime
            if street == '':
                raise ValueError

            # similarity from TFIDF-ML algorithm
            similarity, results_bson, new_street = self._similarity_TFIDF(street, result)

            # get the new address parsed array based on empty facets
            new_array = self._create_new_string_parse(original_array, results_bson)

            # create address data packet based on similarity
            if similarity > self.threshold_model.similarity_threshold:
                street_param: str = new_street
            else:
                street_param: str = street

            # create the new address parts dict() model
            address_parts_new = self.create_dictionary(new_array, street_param)

            # get coordinates
            coordinates = self.forward_coordinate_parse_mapping[self.runner_model.engine](results_bson)

            # [coordinates, address_parts, similarity measurement, strategy]
            return forward_models.DataPacketHandler(forward_models.SuccessPacket(), address_parts_new, address,
                coordinates, similarity)

        # address formatting is done incorrectly
        except ValueError:
            address_parts_new = self.create_null_dictionary(original_array)
            return forward_models.DataPacketHandler(forward_models.EmptyGeocodingCase(), address_parts_new, address, [],
                                                    0)

    def _batch_geocoding_inner(self, addresses: List[str]) -> None:

        """secondary layer to geocoding (used for concurrency), iterates over addresses"""

        # iterate through addresses
        model = None
        for address in addresses:
            # get data from updated_geocoding
            data: Any = self.updated_geocoding(address, 1)

            # find response and supplied packets
            response, supplied = data['response_packet'], data['supplied_packet']

            # extend the forward model response/supplied packet data model
            model = self.batch_handler.BatchPacketHandler(response, supplied)

        return model

    def batch_geocode(self, geo_arr: List[Any], batch_strategy: Callable) -> Any:

        """central method to batch geocoding"""

        # get batch size
        batch_size = len(geo_arr)

        # validate the batch size and return custom HTTP exception if necessary
        try:
            self._validate_batch_size_api(batch_size, strategy=batch_strategy)
        except CallLimitExceeded:
            raise BufferError

        # condition where batch size is small to just run the iterator
        if batch_size <= self.threshold_model.small_batch_maximum:
            return self._batch_geocoding_inner(geo_arr)

        # split the addresses into appropriate packets for concurrency operation
        else:
            addresses: List[Any] = list(self.divide_arr(geo_arr, self.determine_batch_size(geo_arr)))

            # extract geocoded result from layered geocoder with cython backend
            return self._layered_geocoder_concurrency(self._batch_geocoding_inner, addresses)

    def spreadsheet_geocoding(self, geo_arr: List[Any], radius: Union[int, float], batch_strategy: Callable) -> None:
        """spreadsheet geocoding backend feature, handles concurrency operations and output validation"""
        batch_size: int = len(geo_arr)

        try:
            self._validate_spreadsheet_size(batch_size, strategy=batch_strategy)
        except SpreadSheetLimit:
            raise BufferError

        addresses: List[Any] = list(self.divide_arr(geo_arr, self.determine_batch_size(geo_arr)))

        results: list = self._layered_geocoder_concurrency(self._batch_geocoding_inner, addresses)

        spreadsheet_c.write_csv("app/export.csv", 'w+', results)


def factory_geocode_backend_class(database: str, collection: str) -> Any:
    """factory method for creating geocoding facade"""

    obj = ForwardGeocoding(database, collection)
    # State = Enum("State", "Singular Batch Spreadsheet")
    return obj


# noinspection PyCompatibility
class ForwardGeocoderManager(metaclass=ABCMeta):
    """implement facade pattern for the geocoding options, obscure database and ML model settings from client code"""

    @abstractmethod
    def __init__(self):
        pass

    def __str__(self):
        return self.name

    @abstractmethod
    def activation_confirmation(self, request: str) -> str:
        """confirm endpoint activation function fired"""
        pass

    @abstractmethod
    def kill(self):
        """kill the endpoint activation after running cycle"""
        pass


class SingularGeocode(ForwardGeocoderManager):
    """singular endpoint response facade class"""

    def __init__(self, class_obj):
        self.geocoding_obj = class_obj
        self.name = 'Endpoint Geocoder (Regular)'

    def activation_confirmation(self, requests: str) -> str:
        """activate geocoding subprocesses in request packet"""
        return requests

    def kill(self) -> None:
        """kill processes (currently empty"""
        pass

    def process_geocoder(self, address: str, address_type: int) -> Tuple[Any, Any, Any, Any]:
        """process the singular geocoding request from client code"""
        response_data = self.geocoding_obj.updated_geocoding(address, address_type)
        return response_data


class BatchGeocode(ForwardGeocoderManager):
    """batch geocoding facade class"""

    def __init__(self, class_obj: Any):
        self.geocoding_obj = class_obj
        self.name = "Batch Geocoder (Regular)"

    def activation_confirmation(self, requests: str) -> str:
        """confirm process act."""
        return requests

    def kill(self) -> None:
        """kill processes (passed)"""
        pass

    def process_batch(self, addresses: List[str]) -> Any:
        """process the batch (common method)"""
        response_data = self.geocoding_obj.batch_geocode(addresses, forward_models.BatchEndpointStrategy())
        return response_data


class SpreadsheetGeocode(ForwardGeocoderManager):
    """spreadsheet facade class"""

    def __init__(self, class_obj):
        self.name = "Spreadsheet Geocoder (Regular)"
        self.geocoding_obj = class_obj

    def activation_confirmation(self, requests: str) -> str:
        """confirm the activation function was called"""
        return requests

    def kill(self) -> None:
        """kill the script"""
        pass

    def process_batch(self, addresses: List[str], radius: Union[float, int]) -> None:
        """process the batch for geocoding"""
        self.geocoding_obj.spreadsheet_geocoding(addresses, radius,
                                                 forward_models.SpreadsheetStrategy())


class GeneralGeocodingManager:
    """the facade class for the geocoding options"""

    def __init__(self, database: str, collection: str) -> None:
        # create the factory class object method
        self.class_obj = factory_geocode_backend_class(database, collection)

        # create the visible methods for client code
        self.single, self.batch, self.spreadsheet = SingularGeocode(self.class_obj), \
                                                    BatchGeocode(self.class_obj), \
                                                    SpreadsheetGeocode(self.class_obj)

        # get database client for frontend needs
        self.database_objs = self.class_obj.database_objs

    def start_search_process(self):
        """start the searching processes"""
        methods = [self.single.activation_confirmation("Backend Geocoder"),
                   self.batch.activation_confirmation("Backend Geocoder"),
                   self.spreadsheet.activation_confirmation("Backend Geocoder")]
        [print(i) for i in methods]

    def singular_geocode(self, address: str, address_type: int) -> Any:
        """singular geocoding functionality"""
        return self.single.process_geocoder(address, address_type)

    def batch_geocode(self, addresses: List[str]) -> Any:
        """batch geocoding functionality"""
        try:
            return self.batch.process_batch(addresses)
        except BufferError:
            raise BrokenPipeError

    def spreadsheet_geocode(self, addresses: List[str]) -> Any:
        """spreadsheet geocoding functionality"""
        self.spreadsheet.process_batch(addresses, self.class_obj.threshold_model.optimal_radius)


"""---------------------------------------Reverse Geocoding Functionality--------------------------------------------"""


# noinspection PyCompatibility
class AddressComponents(BaseModel):
    """address component model"""

    unit: Optional[str] = None
    street: Optional[str] = None
    number: Optional[Union[int, str]] = None
    region: Optional[str] = None
    postcode: Optional[Union[int, str]] = None
    city: Optional[str] = None


# noinspection PyCompatibility
class AddressPacket(BaseModel):
    """specific address packet to prevent clashes in frontend api"""

    address_parts: AddressComponents
    certainty: str
    format_address: str
    coordinates: List[Union[float, int]]
    accuracy: float
    address_validation: bool


# noinspection PyCompatibility,PyUnresolvedReferences
class ReverseGeocoding(BuildObjs, CommonUtilities):
    """class handling reverse geocoding methods and techniques for frontend API"""

    def __init__(self, database, collection):
        super().__init__()

        # run director builder method
        self.threshold_model = LocalDataClass()
        self.runner_model = RunModel()
        self.database_objs = self.threshold_model.builder_utility(database, collection, 100)

        # create the geocoding model scheme, with radius of search 10
        self.forward_model = forward_models.ForwardGeocodingSchema(radius=self.threshold_model.optimal_radius)
        self.reverse_geocoding_array = []

    @staticmethod
    def _split_coords(coords, *args):
        if len(args) == 0:
            return coords
        else:
            return coords[::-1]

    def _create_address_packet(self, JSON: Dict) -> Tuple[dict, str]:
        property_details: dict = self.clean_properties_collection(JSON['properties'])
        model: AddressComponents = AddressComponents(**property_details)

        return model.dict(), model.unit

    @staticmethod
    def _create_threaded_radius(radius: Union[float, int], iterations: int) -> list:
        """create radius thread"""
        return radius_arr.construct_radius_arr(radius, iterations)

    @staticmethod
    def _create_batch_inner_packet(address_components: dict, formatted_address: str,
                                   coordinate: List[Union[float, int, None]], confidence: float):

        if common_models.poi_not_found_check(formatted_address):
            accuracy: float = 0.0
            address_val: bool = False
        else:
            accuracy: float = 1.0
            address_val: bool = True

        return {'address_parts': address_components,
                'confidence': confidence,
                'coordinates': coordinate,
                'format_address': formatted_address,
                'accuracy': accuracy,
                'address_validation': address_val
                }

    # DEPRECATED
    def _address_search(self, coords: List[list]) -> Any:

        """obtain the document using reverse mapping technique, currently unused"""

        # basic query, direct coordinate
        initial_doc = self.database_objs[common_models.ObjModel().current_geographic_collection].find(
            {'location.coordinates': coords})

        geocoded_point = [i for i in initial_doc][0]
        result_length = len(geocoded_point)

        # get the unit field here
        unit_field = geocoded_point['properties']['unit']
        street = geocoded_point['properties']['street']

        try:
            number = int(geocoded_point['properties']['number'])
        except ValueError:
            number = geocoded_point['properties']['number']

        city = geocoded_point['properties']['city']
        postcode = int(geocoded_point['properties']['postcode'])
        state = geocoded_point['properties']['region']

        address_collection = {'unit': unit_field,
                              'street': street,
                              'number': number,
                              'state': state,
                              'postcode': postcode,
                              'city': city}

        # fix address based on unit existence condition
        if unit_field == '' or unit_field is None:
            return [self._format_address(geocoded_point, True), None, False, address_collection, result_length]
        else:
            return [self._format_address(geocoded_point, True), None, False, address_collection,
                    result_length]

    def _concurrent_reverse(self, function: Callable, coordinates: List[List[Union[float, int]]],
                            radii: List[Union[float, int, None]]) -> Iterable:

        """concurrent reverse geocoding query mapping"""

        with ThreadPoolExecutor() as executor:
            executor.map(function, coordinates, radii)

        return self.reverse_geocoding_array

    def _validate_batch_size_api(self, batch_size: int, strategy: Callable):

        """validate that the batch size was not exceeded"""

        # check batch size and existence of correct strategy, raising custom exception base class if condition met
        if strategy is reverse_models.BatchStrategy and batch_size > self.threshold_model.batch_size:
            raise CallLimitExceeded(
                message="Batch Size Limit exceeded",
                status_code=501,
                batch_size=batch_size
            )

    def _validate_spreadsheet_size(self, batch_size: int, strategy: Callable):

        """validate spreadsheet size"""

        # same as batch size validation but for spreadsheet endpoints
        if strategy() is forward_models.SpreadsheetStrategy() and batch_size > self.threshold_model.spreadsheet_batch_size:
            raise SpreadSheetLimit(
                message="Spreadsheet Size Limit Exceeded",
                status_code=501,
                batch_size=batch_size
            )

    def _coordinate_query(self, lat: float, long: float, radius=100):
        """compute coordinate query"""
        try: # elasticsearch version
            # query database dict() for elastic connection if exists
            elastic_connection = self.database_objs['connection']

            # create query body
            body = {
                "size": 10,
                "query": {
                    "bool": {
                        "filter": {
                            "geo_distance": {
                                "distance": f"{radius+self.threshold_model.radius_delta_null}m",
                                "location": f"{long}, {lat}"
                            }
                        }
                    }
                },
                "sort": {
                    "_geo_distance": {
                        "location": f"{long}, {lat}",
                        "order": "asc"
                    }
                }
            }

            # conduct elasticsearch query with desired global index setting
            try:
                nearest = elastic_connection.search(index=common_models.ObjModel().current_geographic_collection, body=body)['hits']['hits'][0]['_source']
            except (KeyError, NotFoundError, RequestError):
                raise BrokenPipeError

        except (KeyError, IndexError):
            try:
                nearest: Any = self.database_objs[common_models.ObjModel().current_geographic_collection].find(
                    {"location": {
                        "$geoWithin": {
                            "$centerSphere": [[long, lat], self.distance_radians(self.feet_meter(radius))]}}}).clone()
                try:
                    return [i for i in nearest][0]
                except IndexError:
                    # return null response without any addresses
                    return ['', AddressComponents().dict(), 0.0]

            except OperationFailure:
                raise BrokenPipeError

        return nearest

    # noinspection PyCompatibility
    def geolocation_search(self, location: List[float], radius: Union[float, int]) -> List:

        """perform reverse geocoding with 2dSphere technique"""

        # parse the coordinates here
        long, lat = self._split_coords(location)
        check_single: Callable[[Any], Union[bool, Any]] = lambda unit_str: unit_str == '' or unit_str is None

        # get the nearest on or near that coordinate
        poi_nearest = self._coordinate_query(lat, long, radius)

        # if null
        if type(poi_nearest) is list:
            return poi_nearest

        # get confidence score
        confidence: float = certainty_models.state_controller(self.threshold_model.confidence_index,
                                                              self.calc_distance(poi_nearest,
                                                                                 location, self.runner_model.engine),
                                                              certainty_search.confidence_map)
        # get the address packet
        address_packet, unit = self._create_address_packet(poi_nearest)

        # format address in single-liner variable declaration
        # noinspection PyArgumentList
        return [self._format_address(*address_packet.values(), check_single(unit)), address_packet, confidence]

    def _reverse_inner(self, arr: List[List[Union[float, int]]], geo_radius: Union[float, int]):

        """reverse inner method for computing 2dSphere operations/searches"""

        for coordinate in arr:
            formatted_address, address_components, confidence = self.geolocation_search(coordinate, geo_radius)

            # return the formatted data here with Cython/C++ support
            self.reverse_geocoding_array.append(
                self._create_batch_inner_packet(address_components, formatted_address, coordinate, confidence))

    def batch_reverse_geocoding(self, arr: List[List[Union[float, int]]], radius: Union[int, float],
                                strategy: Callable):

        """concurrent version of batch reverse geocoding"""

        # find the batch size (once)
        batch_size = len(arr)

        # validate batch load
        try:
            self._validate_batch_size_api(batch_size, strategy())
        except CallLimitExceeded:
            raise BufferError

        try:
            # separate plain iteration from concurrency approach
            if batch_size <= self.threshold_model.small_batch_maximum:
                self._reverse_inner(arr, self.threshold_model.optimal_radius)
                return self.reverse_geocoding_array

            else:
                # create the concurrent function inputs
                # noinspection PyCompatibility
                coordinates: List[Any] = list(self.divide_arr(arr, self.determine_batch_size(arr)))
                # noinspection PyCompatibility
                radius_arr: List[Union[float, int]] = self._create_threaded_radius(radius, batch_size)

                # activate the reverse utility concurrency operator
                return self._concurrent_reverse(self._reverse_inner, coordinates, radius_arr)
        except BrokenPipeError:
            raise BrokenPipeError

    def spreadsheet_reverse(self, coordinate_arr: List[List[Union[float, int]]], radius: Union[int, float],
                            strategy: Callable) -> None:

        """spreadsheet reverse geocoding method"""

        # find batch load
        # noinspection PyCompatibility
        batch_size: int = len(coordinate_arr)

        # validate batch load
        try:
            self._validate_spreadsheet_size(batch_size, strategy())
        except SpreadSheetLimit:
            raise BufferError

        # extract results and return filename
        # noinspection PyCompatibility
        results: list = self.batch_reverse_geocoding(coordinate_arr, radius, strategy())
        reverse_spreadsheet.spread_write(results, 'app/export.csv', 'w')


def factory_reverse_backend(database: str, collection: str) -> Any:
    """factory implementation for reverse geocoding facade pattern"""

    back_obj = ReverseGeocoding(database, collection)
    # state = Enum("State", "Singular Batch")
    return back_obj


# noinspection PyCompatibility
class ReverseManager(metaclass=ABCMeta):
    """metaclass manager for reverse geocoding functionality"""

    @abstractmethod
    def __init__(self):
        pass

    def __str__(self):
        return self.name

    @abstractmethod
    def show_activation(self, request: str) -> None:
        """start processes"""
        pass


class SingleReverse(ReverseManager):
    """singular reverse geocoding functional exposure"""

    def __init__(self, backend_obj):
        self.reverse = backend_obj
        self.name = "Singular Reverse"

    def show_activation(self, request: str) -> None:
        """start processes here"""
        print(request)

    def single_reverse(self, location: List[Union[float, int]], radius: Union[float, int]) -> Any:
        """singular geocoding implementation"""
        return self.reverse.geolocation_search(location, radius)


class BatchReverse(ReverseManager):
    """batch geocoding functional exposure"""

    def __init__(self, backend_obj):
        self.reverse = backend_obj
        self.name = "Batch Reverse"

    def show_activation(self, request: str) -> None:
        """start processes here"""
        print(request)

    def batch_reverse(self, coordinates_arr: List[List[Union[int, float, None]]],
                      radius: Union[int, float, None]) -> Any:
        """batch revere geocoding implementation"""
        return self.reverse.batch_reverse_geocoding(coordinates_arr, radius, reverse_models.BatchStrategy)


class SpreadsheetReverse(ReverseManager):
    """spreadsheet functional exposure"""

    def __init__(self, backend_obj):
        self.reverse = backend_obj
        self.name = "Spreadsheet Reverse"

    def show_activation(self, request: str) -> None:
        """start processes"""
        print(request)

    def spread_reverse(self, coordinate_arr: List[List[Union[float, int]]], radius: Union[int, float]) -> None:
        """spreadsheet reverse geocoding implementation"""
        self.reverse.spreadsheet_reverse(coordinate_arr, radius, reverse_models.SpreadsheetStrategy)


class GeneralReverseManager:
    """general reverse geocoding coordinator class"""

    def __init__(self, database: str, collection: str) -> None:
        backend_obj = factory_reverse_backend(database, collection)
        self.single, self.batch, self.spread = SingleReverse(backend_obj), \
                                               BatchReverse(backend_obj), \
                                               SpreadsheetReverse(backend_obj)
        self.database_objs = backend_obj.database_objs

    def activate_processes(self) -> None:
        """activate the processes here using Enum from middleware layer"""
        methods = [self.single.show_activation("Activation of Singular Reverse Geocoder"),
                   self.batch.show_activation("Activation of Batch Reverse Geocoder")]
        [print(i) for i in methods]

    def single_reverse(self, location: List[Union[float, int]], radius: Union[int, float, None]) -> Any:
        """single reverse geocoding"""
        return self.single.single_reverse(location, radius)

    def batch_reverse(self, coordinates_arr: List[List[Union[int, float, None]]],
                      radius: Union[int, float]) -> Any:
        """batch reverse geocoding"""
        return self.batch.batch_reverse(coordinates_arr, radius)

    def spread_reverse(self, coordinate_arr: List[List[Union[float, int]]], radius: Union[int, float]) -> None:
        """spreadsheet reverse geocoding"""
        self.spread.spread_reverse(coordinate_arr, radius)


class Subscription:
    """contains subscription objects and functionality"""

    def __init__(self, database: str, collection: str):
        backend_obj = factory_reverse_backend(database, collection)
        self.database_objs = backend_obj.database_objs


################################ Autocompletion ########################################


class AutocompleteParse(BuildObjs, CommonUtilities):
    """autocomplete/parsing class"""

    def __init__(self, database, collection):
        super().__init__()

        # run director builder method
        self.database_objs = DirectorGeneralObjs(database, collection, 100)

        # data models
        self.settings_model = LocalDataClass()
        self.autocomplete_model = correction_parse_models.CorrectionModel()  # change this model instantiation once functionality is added
        self.unit_check = lambda unit: True if unit == '' else False

    @staticmethod
    def _run_similarity(street_query, region, city, result):
        """find most similar street"""
        return TFIDF_max.find_max_similarity(street_query, region, city, result)

    @staticmethod
    def _generator_unpacker(BSON_obj: Any) -> dict:
        for document in BSON_obj:
            yield document

    def _address_query(self, postcode: str, number: str) -> dict:
        """find general region where postcode and number filter match"""

        # process query with find() operator
        address_query = self.database_objs[common_models.ObjModel().current_geographic_collection].find(
            {'$and': [{'properties.number': number}, {'properties.postcode': postcode}]}
        )

        # unpack using generator expression
        return address_query  # self._generator_unpacker(address_query)

    def _encode_input_address(self, full_address, **encoder_option) -> Any:
        """encode the input address numerically for model integration"""
        try:
            encoder_option = encoder_option['option']
        except KeyError:
            encoder_option = self.settings_model.default_autocomplete_algorithm

    def _parse_address_network(self, encoded_full_address) -> dict:
        """parse the address into its components for parsing facade and """
        # example output: {street: ..., postcode: ..., ...}
        return {}

    def autocomplete(self, full_address: str) -> str:
        """autocompletion facade function"""

        # encode/preprocess address
        encoded_address = self._encode_input_address(full_address)

        # parse the address parts
        number, street, city, postcode, region, unit = self._parse_address_network(encoded_address)

        # regional query computing here
        regional_results = self._address_query(postcode, number)

        # get similarity results
        street_query, city_query, region_query = self._run_similarity(street, region, city, regional_results)

        # similarity from TFIDF-ML algorithm
        similarity_street, results_bson_street, new_street = street_query
        similarity_city, results_bson_city, new_city = city_query
        similarity_region, results_bson_region, new_region = region_query

        return self._format_address(unit, new_street, number, new_region, postcode, new_city, self.unit_check(unit))

    def parse_facade(self, full_address) -> dict:
        """parsing facade"""
        encoded_address = self._encode_input_address(full_address)  # select a model, else the default is used
        return self._parse_address_network(encoded_address)
