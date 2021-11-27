"""PeekGeo API endpoint program"""

# from fastapi.responses import StreamingResponse
from fastapi import HTTPException, Depends, Query, UploadFile, File
from dependency_injector import containers, providers
from dependency_injector.wiring import inject, Provide, Provider

# dataclass modules
from typing import Optional, List, Union, Callable, Tuple, Any, Dict
from pydantic import BaseModel

# runtime utilities
import os
import sys

# noinspection PyCompatibility
from asyncio import create_task, run

# time modules
from datetime import datetime, date
from time import perf_counter
from ast import literal_eval

# elasticsearch imports
from elasticsearch.exceptions import ConflictError, RequestError

# data science/helper-methods imports
import json
import importlib

sys.path.append(".")
sys.path.append('/app')

from geocodingBackend import GeneralGeocodingManager, GeneralReverseManager, DensityRadius, \
    Convex, RunModel

# models import
from models import frontend_models, density_models, common_models, user_metrics_models as USM
from logger import log_error

# import cython files
from CythonOperations import create_convex_array, check_dups, zip_coordinate, check_lat_long_length, \
    check_address_length, zip_coordinates_elastic, create_convex_elastic, coordinate_conv_package


# noinspection PyCompatibility
class GlobalMetricManager(BaseModel):
    """global metric manager for handling metrics of each endpoint"""
    load_radius: Optional[str] = 'radius'
    convex: Optional[str] = 'convex'
    density: Optional[str] = 'density'
    reverse_single: Optional[str] = 'reverse_single'
    reverse_batch: Optional[str] = 'reverse_batch'
    single_forward: Optional[str] = 'geocode_single'
    batch_forward: Optional[str] = 'geocode_batch'
    api_call_key: Optional[str] = 'api_calls'


class SingletonType(type):
    """singleton class for singular base url instantiation"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


# noinspection PyCompatibility,PyTypeChecker
class PeekGeoUtilities(metaclass=SingletonType):
    """handle all backend object creation by creating only one backend object only when needed"""

    def __init__(self, backend_method: Any):
        # create settings models
        self.global_model: GlobalDataModel = GlobalDataModel()
        self.runner_model: RunModel = RunModel()

        # create backend objects for storing databases and functionality
        self.backend_utility = backend_method(self.global_model.database, self.global_model.collections)

        # mappings for database options
        self.coordinate_mapping: dict = {'pymongo': zip_coordinate,
                                         'elastic': zip_coordinates_elastic}
        self.convex_mapping: dict = {'pymongo': create_convex_array, 'elastic': create_convex_elastic}
        self.metric_handler_mapping: dict = {
            'pymongo': {
                'radius': USM.RadiusMetrics,
                'convex': USM.ConvexMetrics,
                'density': USM.DensityMetrics,
                'reverse_single': USM.SingleReverseMetrics,
                'reverse_batch': USM.BatchReverseMetrics,
                'forward_single': USM.SingleForwardMetrics,
                'forward_batch': USM.BatchForwardMetrics
            },
            'elastic': {
                'radius': USM.RadiusMetricsElastic,
                'convex': USM.ConvexMetricsElastic,
                'density': USM.DensityMetricsElastic,
                'reverse_single': USM.SingleReverseMetricsElastic,
                'reverse_batch': USM.BatchReverseMetricsElastic,
                'forward_single': USM.SingleForwardMetricsElastic,
                'forward_batch': USM.BatchForwardMetricsElastic
            }
        }
        self.custom_density_mapping: dict = {'pymongo': {'state': density_models.StateDensityStrategy(),
                                                         'city': density_models.CityDensityStrategy(),
                                                         'postcode': density_models.PostcodeDensityStrategy()},
                                             'elastic': {'state': density_models.StateDensityElastic(),
                                                         'city': density_models.CityDensityElastic(),
                                                         'postcode': density_models.PostcodeDensityElastic()}
                                             }

    @staticmethod
    async def background_logging(name: str, filename: str, logger_level: str, message: str) -> None:
        """conduct background logging activity"""
        try:
            log_error(name, filename, logger_level, message)
        except FileExistsError or FileNotFoundError:
            raise BrokenPipeError

    @staticmethod
    async def get_datetime_objs() -> Dict:
        """create the datetime objects"""
        date_now = str(date.today())
        time_now = str(datetime.now())
        official_timestamp = datetime.timestamp(datetime.now())
        return dict(date=date_now, time=time_now, official_timestamp=official_timestamp)

    @staticmethod
    def handle_coordinates(coordinates: List[Union[float, int]], reverse_param: bool):
        """handle reversals and such"""
        if reverse_param:
            return coordinates[::-1]
        else:
            return coordinates

    def _clean_file_batch_reverse(self, coordinate_file: Any):

        """clean the batch reverse geocoding file for elasticsearch and pymongo differentiation"""

        coord_data = json.load(coordinate_file.file)['coordinates']
        if self.runner_model.engine == 'pymongo':
            return coord_data
        else:
            stringified_coord_data = []
            for coordinate in coord_data:
                coordinate = f'{coordinate[0]}, {coordinate[1]}'
                stringified_coord_data.append(coordinate)
            return stringified_coord_data

    @staticmethod
    def handle_batch_reverse_coords(latitudes: List[Union[float, int]], longitudes: List[Union[float, int]],
                                    reverse_param: bool,
                                    coordinate_file: UploadFile = File(None)) -> Any:

        """handle the spreadsheet and batch coordinate reverse geocoding logic"""
        """FILE INPUT HAS PRIORITY"""

        if coordinate_file is not None:
            return json.load(coordinate_file.file)['coordinates']
        else:
            if latitudes is None and longitudes is None:
                raise HTTPException(
                    status_code=505,
                    detail='No Input Detected',
                    headers={"Error_Description": "Check documentation for input requirements"}
                )
            else:
                # check the length of the coordinates to not exceed batch limit
                if check_lat_long_length.check_lat_long(latitudes, longitudes, GlobalDataModel().batch_endpoint_max):
                    # return based on the database engine being run
                    return zip_coordinate.coordinate_zipped(latitudes, longitudes, reverse_param)
                else:
                    raise HTTPException(
                        status_code=505,
                        detail='Array Mapping Error Encountered',
                        headers={
                            "Error_Description": "Latitudes List length must match Longitudes List length. Maximum batch is {}".format(
                                GlobalDataModel().batch_endpoint_max)}
                    )

    @staticmethod
    def handle_convex_coordinates(latitudes, longitudes, reverse_param) -> list:
        """handle the coordinates of the convex endpoint"""

        return create_convex_array.convex_array(latitudes, longitudes, reverse_param)

    @staticmethod
    def handle_batch_reverse_addresses(addresses: List[str], address_file: UploadFile = File(None)):
        """handle the batch address calls, must have addresses as header"""
        if address_file is not None:
            # noinspection PyTypeChecker
            return json.loads(address_file.file)['addresses']
        else:
            if addresses is None:
                raise HTTPException(
                    status_code=505,
                    detail='No Address Input Detected',
                    headers={"Error_Description": "Check documentation for address input requirements"}
                )
            else:
                if check_address_length.check_batch(addresses, GlobalDataModel().batch_endpoint_max):
                    return addresses
                else:
                    raise HTTPException(
                        status_code=505,
                        detail='Batch Size Exceeded',
                        headers={
                            "Error_Description": "Maximum for batch forward geocoding was exceeded. Maximum batch is {}".format(
                                GlobalDataModel().batch_endpoint_max)}
                    )

    def close_client(self) -> None:
        """close the mongo client"""
        try:
            self.backend_utility.database_objs['client'].close()
        except KeyError:
            pass

    def background_api_call_handler(self, token: str, delta_call: int, original_calls: int, method: str) -> None:
        """all background api calls handled for website version"""
        try:
            # create the call update delta
            updated_call_count = original_calls - delta_call
            if updated_call_count < 0:
                updated_call_count = 0

            # query for updating one document from user accounts db
            try:
                # pymongo option
                self.backend_utility.database_objs[common_models.ObjModel().current_accounts_collection].update(
                    {'token': token}, {'$set': {f'{method}': updated_call_count}})
            except KeyError:
                # elasticsearch option, create query request body
                body_calls_update = {
                    "script": {
                        "inline": f"ctx._source.{method}={updated_call_count}",
                        "lang": "painless"
                    },
                    "query": {
                        "match": {
                            "token": token
                        }
                    }
                }

                # compute query of update_one document
                try:
                    self.backend_utility.database_objs['connection'].update_by_query(
                        index=common_models.ObjModel().current_accounts_collection,
                        body=body_calls_update)
                except ConflictError:
                    self.backend_utility.database_objs['connection'].indices.refresh(index=common_models.ObjModel().current_accounts_collection)
                    self.backend_utility.database_objs['connection'].update_by_query(
                        index=common_models.ObjModel().current_accounts_collection,
                        body=body_calls_update)

        except TypeError or ValueError:
            raise Exception('Background API call handler encountered error state')

    def get_user(self, username: str):
        """get the user by username, used for security when logging in with username"""
        try:
            user = list(self.backend_utility.database_objs[common_models.ObjModel().current_accounts_collection].find(
                {'username': username}))[0]
        except KeyError:
            # create outgoing body request
            body = {
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"username": username}}
                        ]
                    }
                }
            }

            # conduct elasticsearch query
            try:
                user = self.backend_utility.database_objs['connection'].search(
                    index=common_models.ObjModel().current_accounts_collection, body=body)['hits']['hits']
            except KeyError or IndexError:
                user = None

        return user

    def get_call_limit(self, token: str, method: str) -> Any:
        """get the user api call maximum"""
        try:
            try: # mongodb version
                query = list(self.backend_utility.database_objs[
                    common_models.ObjModel().current_accounts_collection
                ].find({'token': token}))[0][f'{method}']
            # create outgoing request body
            except KeyError:
                body = {
                    "query": {
                        "match": {
                            "token": token
                        }
                    }
                }

                # conduct elasticsearch query
                query = self.backend_utility.database_objs['connection'].search(
                        index=common_models.ObjModel().current_accounts_collection, body=body)['hits']['hits'][0]['_source'][f'{method}']

            return query

        except (IndexError, TypeError, RequestError):
            raise HTTPException(
                status_code=500,
                detail="Invalid API Token Encountered",
                headers={'Error_Description': "Reset token or validate current token"}
            )

    def verify_token(self, token: str) -> Union[bool, None]:
        """verify the access token to API endpoint"""

        try:
            query = len(
                list(self.backend_utility.database_objs[common_models.ObjModel().current_accounts_collection].find(
                    {'token': token})))
        except KeyError:
            # create request body
            body = {
                "query": {
                    "bool": {
                        "should": [
                            {"term": {"token": token}}
                        ]
                    }
                }
            }

            # conduct elastic search with exception for key errors upon receiving incoming request
            try:
                query = len(self.backend_utility.database_objs['connection'].search(
                    index=common_models.ObjModel().current_accounts_collection,
                    body=body)['hits']['hits'])
            except KeyError or IndexError or TypeError:
                query = 0

        return query == 0

    async def handle_user_metrics(self, metric_method: str, **kwargs):
        """handle user metrics method for recording behavior and progress of each person in account data packet"""
        date_results = create_task(self.get_datetime_objs())
        date_results = await date_results
        time_now, date_now, official_timestamp = date_results.values()

        # use the bridge pattern for the handler objects in the user_models module
        try:
            metric_handler = USM.TrackUsers(self.metric_handler_mapping[self.runner_model.engine][metric_method])
            metric_handler.handle_metrics(self.backend_utility, time_now, date_now, **kwargs)
        except KeyError:
            raise Exception("User Metrics failed")

    def account_data(self, token_query: dict, method: str) -> Tuple[int, int, float, datetime]:
        """get account data for specified token document"""

        # get the account date, pay plan from user document
        account_date, plan = str(token_query['date']), token_query['plan']

        # get account datetime object, create current object
        account_date, current_date = datetime.fromisoformat(account_date.replace("Z", "")), str(datetime.now()).replace(" ", "T")

        # compute time difference in minutes
        delta_time = datetime.fromisoformat(current_date) - account_date
        minutes = divmod(delta_time.total_seconds(), 60)[0]

        # find api calls and spreadsheet calls
        api_calls, spreadsheet_calls = self.global_model.call_pay_plans[plan]

        if minutes >= 1440:
            return api_calls, spreadsheet_calls, minutes, current_date
        else:
            if method == 'single':
                return token_query['api_calls'] - 1, token_query['spreadsheet_calls'], minutes, current_date
            else:
                return token_query['api_calls'], token_query['spreadsheet_calls'] - 1, minutes, current_date

    async def regulate_api_calls(self, token: str, method: str) -> None:
        """regulate and renew API calls"""

        # find the account using the user's oauth2 token
        try:
            # pymongo version
            token_query = list(
                self.backend_utility.database_objs[common_models.ObjModel().current_accounts_collection].find(
                    {'token': token}))[0]
        except KeyError:
            # elasticsearch version

            # create outgoing request body
            body = {
                "query": {
                    "match": {
                        'token': token
                    }
                }
            }

            # conduct elasticsearch query
            try:
                token_query = self.backend_utility.database_objs['connection'].search(
                    index=common_models.ObjModel().current_accounts_collection,
                    body=body)['hits']['hits'][0]['_source']
            except (KeyError, IndexError):
                token_query = {}

        try:
            # get account information based on token query
            api_calls, spreadsheet_calls, minutes, current_date = self.account_data(token_query, method)

            # condition for call regeneration (once every day, one minute before)
            try:
                # pymongo update one document
                self.backend_utility.database_objs[common_models.ObjModel().current_accounts_collection].update_one(
                    {'token': token}, {'$set': {'api_calls': api_calls, 'spreadsheet_calls': spreadsheet_calls,
                                                'date': current_date}})

            except KeyError:
                # create request body for elasticsearch update query
                body_api_calls = {
                    "script": {
                        "inline": f"ctx._source.api_calls={api_calls}; "
                                  f"ctx._source.spreadsheet_calls={spreadsheet_calls}; "
                                  f"ctx._source.date=ctx._source.date=new SimpleDateFormat('yyyy-MM-dd').parse('{current_date}')",
                        "lang": "painless"
                    },
                    "query": {
                        "match": {
                            "token": token
                        }
                    }
                }

                # compute update queries
                self.backend_utility.database_objs['connection'].update_by_query(
                    index=common_models.ObjModel().current_accounts_collection,
                    body=body_api_calls)

        except (IndexError, KeyError):
            raise Exception("Unidentified User")


############################# SETTINGS MODEL ###############################


# noinspection PyCompatibility
class GlobalDataModel(BaseModel):
    """global data class for common variables across all endpoints"""

    database: Optional[str] = 'PeekDB'
    collections: Optional[Tuple] = ("proplocations", "apiusers")
    convex_edge_limit: Optional[int] = 20
    convex_area_limit: Optional[int] = 250
    density_radius_limit: Optional[dict] = {'ft': 9843, 'm': 3000.146, 'mi': 1.864205, 'yd': 3281, 'km': 3.000146}
    density_strategy_table: Optional[dict] = {'state': density_models.StateDensityStrategy(),
                                              'city': density_models.CityDensityStrategy(),
                                              'postcode': density_models.PostcodeDensityStrategy()}
    batch_endpoint_max: Optional[int] = 125
    max_load_radius: Optional[int] = 2000
    token_length: Optional[int] = 12
    call_pay_plans: Optional[Dict[Union[int, str], Tuple[int, int]]] = {0: (100, 0),
                                                                        20: (13000, 20),
                                                                        60: (100000, 50),
                                                                        125: (350000, 200)}


################################## Error Response BaseClasses #####################################


# noinspection PyCompatibility
class NullResponses(BaseModel):
    """null responses for all api calls"""

    exhausted_calls: Optional[Dict] = {
        'meta': {'build': 'NO_CALLS', 'status': 404, 'matching': 0,
                 'timestamps': {'date': str(date.today()),
                                'time': str(datetime.now()),
                                'official_timestamp': datetime.timestamp(datetime.now())},
                 'geocoded_data': {}},
        'supplied_data': {},
        'source': '©OpenStreetMap contributors'
    }

    internal_error: Optional[Dict] = {'meta': {'build': 'INTERNAL_ERR', 'status': 500, 'matching': 0,
                                               'timestamps': {'date': str(date.today()),
                                                              'time': str(datetime.now()),
                                                              'official_timestamp': datetime.timestamp(
                                                                  datetime.now())},
                                               'geocoded_data': {}},
                                      'supplied_data': {},
                                      'source': '©OpenStreetMap contributors'
                                      }

    property_not_found: Optional[Dict] = {'meta': {'build': 'NULL', 'status': 200, 'matching': 0,
                                                   'timestamps': {'date': str(date.today()),
                                                                  'time': str(datetime.now()),
                                                                  'official_timestamp': datetime.timestamp(
                                                                      datetime.now())},
                                                   'geocoded_data': {},
                                                   },
                                          'supplied_data': {},
                                          'source': '©OpenStreetMap contributors'}

    edges_error: Optional[Dict] = {'meta': {'build': 'EDGE_ERROR', 'status': 404, 'matching': 0,
                                            'timestamps': {'date': str(date.today()),
                                                           'time': str(datetime.now()),
                                                           'official_timestamp': datetime.timestamp(
                                                               datetime.now())},
                                            'geocoded_data': {}},
                                   'supplied_data': {},
                                   'source': '©OpenStreetMap contributors'
                                   }


def create_dependency_instance(method: Any) -> Any:
    """create dependency through the base utilities class"""
    return PeekGeoUtilities(method)


def check_units(unit_in: str, unit_out: str):
    """check if valid units were inputted into the density model"""

    if unit_in not in density_models.DensitySchema().units:
        raise HTTPException(
            status_code=404,
            detail='Select a valid INPUT unit, one list in the documentation',
            headers={'Error_Description': 'Check Unit in Docs'}
        )
    if unit_out not in density_models.DensitySchema().units:
        raise HTTPException(
            status_code=404,
            detail='Select a valid OUTPUT unit, one list in the documentation',
            headers={'Error_Description': 'Check Unit in Docs'}
        )


################################## API ENDPOINTS BELOW #####################################


def check_radius(radius: int) -> bool:
    """check the radius and return failure response if needed"""

    if radius > GlobalDataModel().max_load_radius:
        return True
    else:
        return False


def radius_response_fail(radius: int, location: List[Union[float, int]]) -> Union[None, dict]:
    """define the failed radius response once exceeded"""
    return {'meta': {'build': 'Radius_EXC', 'status': 505, 'matching': 0,
                     'timestamps': {'date': str(date.today()),
                                    'time': str(datetime.now()),
                                    'official_timestamp': datetime.timestamp(datetime.now())},
                     'geocoded_data': {}},

            'supplied_data': {'latitude': location[0], 'longitude': location[1], 'supplied_radius': radius},
            'source': '©OpenStreetMap contributors'
            }


def success_response(date_results: dict,
                     location: List[Union[float, int]],
                     radius: int,
                     result_arr: Any):
    """success response creation"""

    return {
        'meta': {'build': 'OK', 'status': 200, 'matching': len(result_arr),
                 'timestamps': {'date': date_results['date'],
                                'time': date_results['time'],
                                'official_timestamp': date_results['official_timestamp']},
                 'geocoded_data': {'load_radius': result_arr,
                                   'certainty': 'Within 10 ft'}},
        'supplied_data': {'latitude': location[0], 'longitude': location[1],
                          'supplied_radius': radius},
        'source': '©OpenStreetMap contributors'
    }


class SetUpLoadRadius:
    """set up the load radius with get_params function"""

    def __init__(self, token: str, coordinates: List[Union[float, int]],
                 radius: Union[int, float], reverse_param: bool = False):
        self.token = token
        self.coordinates = coordinates
        self.radius = radius
        self.reverse_param = reverse_param

    # noinspection PyCompatibility
    def set_up(self):
        """set up computational objects for load radius endpoint"""

        # create backend handlers
        backend_dependency = PeekGeoUtilities(DensityRadius)
        backend_obj = backend_dependency.backend_utility

        # get the global metrics manager object
        metrics_manager = GlobalMetricManager()

        # handle the coordinate input
        location: List = backend_dependency.handle_coordinates(self.coordinates, self.reverse_param)

        # get the call limit
        call_limit = backend_dependency.get_call_limit(self.token, metrics_manager.api_call_key)

        # data packet for dependency
        return [self.radius, location, backend_obj, backend_dependency, self.token, call_limit]


class LoadRadiusContainer(containers.DeclarativeContainer):
    """load radius container"""

    config = providers.Configuration()

    loader = providers.Factory(
        SetUpLoadRadius,
        token=config.token,
        coordinates=config.coordinates,
        radius=config.radius,
        reverse_param=config.reverse_param
    )


# noinspection PyCompatibility
async def load_properties_api(class_dependency: dict) -> dict:
    """functionality/endpoint for load radius tool"""

    # create container
    container = LoadRadiusContainer()
    container.config.from_dict(class_dependency)

    # find all backend objects from dependency
    radius, location, load_radius_backend, utility_obj, token, call_limit = container.loader().set_up()

    # add background task for closing mongo client
    utility_obj.close_client()

    # create call management background task
    await utility_obj.regulate_api_calls(token, 'single')

    # user metric background task here
    await utility_obj.handle_user_metrics('radius', token=token, radius=radius)

    # check api call limit if any calls remain
    if call_limit - 1 >= 0:

        # conduct radius check so users do not exceed
        if check_radius(radius):
            return radius_response_fail(radius, location)

        try:
            # handle coroutines
            task1 = create_task(load_radius_backend.load_radius(location, radius))
            date_task = create_task(utility_obj.get_datetime_objs())

            # process coroutine results
            results = await task1
            date_results = await date_task

            # encoded_json = fast_api_response_packet
            utility_obj.background_api_call_handler(token, 1, call_limit, GlobalMetricManager().api_call_key)

            # create and return the success packet at the bottom
            return success_response(date_results, location, radius, results)

        except BrokenPipeError:
            # 505 server error response
            return NullResponses().internal_error

    else:
        # no calls response
        return NullResponses().exhausted_calls


################################## Convex Search endpoint ########################################


def excessive_edge_length_response(edges: List[list], date_results: dict) -> Dict:
    """edges length exceeded response"""

    return {
        'meta': {'build': 'EDGE_EXC', 'status': 404, 'matching': 0,
                 'timestamps': {'date': date_results['date'],
                                'time': date_results['time'],
                                'official_timestamp': date_results['official_timestamp']},
                 'geocoded_data': {'convex_array': [],
                                   'certainty': 'Within 10 ft'}},
        'supplied_data': {'search_edges': edges},
        'source': '©OpenStreetMap contributors'
    }


# noinspection PyUnresolvedReferences
def count_edge_response(edges: List[list]) -> bool:
    """count the number of edges and check if it exceeds the global maximum set"""
    if len(edges[0]) > GlobalDataModel().convex_edge_limit:
        return True


def duplicate_edge_response(search_edges: List, repeated_edges: List, date_results: dict) -> Dict:
    """duplicate edge response"""
    repeated_edges = [literal_eval(node) for node in set(repeated_edges)]
    return {
        'meta': {'build': 'DUP_EDGE', 'status': 404, 'matching': 0,
                 'timestamps': {'date': date_results['date'],
                                'time': date_results['time'],
                                'official_timestamp': date_results['official_timestamp']},
                 'geocoded_data': {'convex_array': [],
                                   'certainty': 'Within 10 ft',
                                   'repeated_edges': repeated_edges}},
        'geocoded_data': {'search_edges': search_edges[0]},
        'source': '©OpenStreetMap contributors'
    }


def duplicate_edge_check(edges_duplicate: list):
    """check for duplicate edges in user input"""
    duplication_check = check_dups.is_duplicates(edges_duplicate)
    if duplication_check[0]:
        return duplication_check[1]
    else:
        return False


def area_exceeded_response(area: Union[float, int, None], date_results: dict) -> Dict:
    """area exceeded response"""

    return {
        'meta': {'build': 'AREA_EXC, CURRENT: {}'.format(area), 'status': 500, 'matching': 0,
                 'timestamps': {'date': date_results['date'],
                                'time': date_results['time'],
                                'official_timestamp': date_results['official_timestamp']},
                 'geocoded_data': {}},
        'supplied_data': {},
        'source': '©OpenStreetMap contributors'
    }


# noinspection PyUnresolvedReferences
def area_check(class_obj: Callable, latitudes: List[Union[float, int]], longitudes: List[Union[float, int]]) -> bool:
    """check for area exceeding"""
    area = class_obj.get_polygon_area(latitudes, longitudes)
    if area > GlobalDataModel().convex_area_limit:
        return area
    else:
        return False


def convex_success_response(edges: list, results: Any, date_results: dict):
    """create the success case for the convex endpoint"""

    return {
        'meta': {'build': 'OK', 'status': 200, 'matching': len(list(results)),
                 'timestamps': {'date': date_results['date'],
                                'time': date_results['time'],
                                'official_timestamp': date_results['official_timestamp']},
                 'geocoded_data': {'convex_array': [i for i in results],
                                   'certainty': 'Within 10 ft'}},
        'supplied_data': {'search_edges': edges[0]},
        'source': '©OpenStreetMap contributors'
    }


class SetUpConvex:
    """set up convex class for polygon searches"""

    def __init__(self, token: str, coordinates: List[Union[float, int]], reverse_param: Optional[bool] = False):
        self.token = token
        self.coordinates = coordinates
        self.reverse_param = reverse_param

    # noinspection PyCompatibility
    def set_up(self):
        """set up all computational objects for the convex endpoint"""

        # create the backend object handlers
        utility_obj = PeekGeoUtilities(Convex)
        backend_obj = utility_obj.backend_utility

        latitudes, longitudes = utility_obj.get_lats_longs(self.coordinates, self.reverse_param)

        # get the call limit
        call_limit = utility_obj.get_call_limit(self.token, GlobalMetricManager().api_call_key)

        # create utility return packet here
        return [backend_obj, utility_obj, self.coordinates, self.token, call_limit, latitudes, longitudes]


class ConvexContainer(containers.DeclarativeContainer):
    """convex container class"""

    config = providers.Configuration()

    loader = providers.Factory(
        SetUpConvex,
        token=config.token,
        coordinates=config.coordinates,
        reverse_param=config.reverse_param
    )


# noinspection PyCompatibility
async def convex_search_api(class_dependency: dict) -> dict:
    """convex search endpoint for all convex functionality"""

    # create the container
    container = ConvexContainer()
    container.config.from_dict(class_dependency)

    # get the api endpoint objects from dependency
    geocoding_library, utility_obj, edges, token, call_limit, latitudes, longitudes = container.loader().set_up()

    # create call management background task
    utility_obj.regulate_api_calls(token, 'single')

    # create date task
    date_task = create_task(utility_obj.get_datetime_objs())

    # await the date_task coroutine
    date_results = await date_task

    # get the inner edges
    inner_edges = edges[0]

    # edges count, duplicate check, and area response here
    if count_edge_response(edges):
        return excessive_edge_length_response(edges, utility_obj)
    duplicate_check = duplicate_edge_check(inner_edges[0:len(inner_edges) - 1])
    if type(duplicate_check) is not bool:
        return duplicate_edge_response(edges, duplicate_check, date_results)
    area_val = area_check(geocoding_library, latitudes, longitudes)
    if type(area_val) is not bool:
        return area_exceeded_response(area_val, date_results)

    # add background tasks for convex endpoint
    utility_obj.handle_user_metrics('convex', token=token,
                                    area=area_val, edge_count=len(edges))

    # create polygon task after verification
    polygon_task = create_task(geocoding_library.convex_director(edges))

    # check if user has api calls available
    if call_limit - 1 >= 0:
        try:
            # await the results from polygon task
            results = await polygon_task
            utility_obj.close_client()

            # decrease api calls only in the success case
            utility_obj.background_api_call_handler(token, 1, call_limit,
                                                    GlobalMetricManager().api_call_key)

            # create and return the success packet here
            return convex_success_response(edges, results, date_results)

        except BrokenPipeError:
            # 505 error response
            utility_obj.close_client()
            return NullResponses().edges_error

    else:
        # no remaining calls response
        return NullResponses().exhausted_calls


#################################### DENSITY SEARCH ENDPOINT HERE ################################################


def exceeded_radius_check(radius: int, unit: str) -> bool:
    """handle exceeded density radius response"""
    if radius > GlobalDataModel().density_radius_limit[unit]:
        return True


def exceeded_radius_response(radius: int, unit_out: str, unit_in: str, coordinates: List[Union[float, int]],
                             date_results: dict) -> Dict:
    """exceeded radius for density coordinate query"""

    return {
        'meta': {'build': 'RADIUS_EXC'.format(GlobalDataModel().density_radius_limit[unit_in], unit_in), 'status': 404,
                 'matching': 0,
                 'timestamps': {'date': date_results['date'],
                                'time': date_results['time'],
                                'official_timestamp': date_results['official_timestamp']},
                 'geocoded_data': {'density': 0,
                                   'unit': '{}'.format(unit_out)}},
        'supplied_data': {'coordinates': coordinates, 'radius': str(radius)},
        'source': '©OpenStreetMap contributors'
    }


def success_density_response(result: Union[float, int, None], date_results: dict, unit_out: str, supplied: dict):
    """create the success response for the density endpoint"""
    return {'meta': {'build': 'OK', 'status': 200, 'matching': 1,
                         'timestamps': {'date': date_results['date'],
                                        'time': date_results['time'],
                                        'official_timestamp': date_results['official_timestamp']},
                         'geocoded_data': {'density': result,
                                           'unit': '{}'.format(unit_out)}},
                'supplied_data': supplied,
                'source': '©OpenStreetMap contributors'
            }


class SetUpDensity:
    """density base set up class creation"""

    def __init__(self, token: str,
                 coordinate: Optional[Union[list, None]] = None,
                 unit_in: Optional[str] = "ft",
                 unit_out: Optional[str] = "ft",
                 radius: Optional[Union[float, int, None]] = None,
                 reverse_param: Optional[Union[bool, None]] = False,
                 custom_option: Optional[Union[frontend_models.DensitySearch('do'), None]] = None,
                 custom_utility: Union[Optional[Union[str, int, float, None]], None] = None
                 ):
        self.token = token
        self.coordinate = coordinate
        self.unit_in = unit_in
        self.unit_out = unit_out
        self.radius = radius
        self.reverse_param = reverse_param
        self.custom_option = custom_option
        self.custom_utility = custom_utility

    # noinspection PyCompatibility
    def set_up(self):
        """set up all computational objects for the density endpoint"""

        # create the backend handlers
        utility_obj = PeekGeoUtilities(DensityRadius)
        backend_obj = utility_obj.backend_utility

        # check the strategies and translate into usable models
        if self.custom_option is not None and self.custom_utility is not None:
            strategy = utility_obj.custom_density_mapping[utility_obj.runner_model.engine][self.custom_option]
        else:
            strategy = None

        # handle the user coordinate
        coordinate = utility_obj.handle_coordinates(self.coordinate, self.reverse_param)

        # make sure input unit is supported and raise HTTPException if not
        check_units(self.unit_in, self.unit_out)

        # check if there is any input at all
        if coordinate == [None, None] and strategy is None:
            raise HTTPException(
                status_code=404,
                detail='No Input Detected',
                headers={'Error_Description': "Fill Required Input Fields"}
            )

        # get call limit
        call_limit = utility_obj.get_call_limit(self.token, GlobalMetricManager().api_call_key)
        return [backend_obj, utility_obj, coordinate, self.radius, self.unit_in, self.unit_out,
                self.custom_utility, strategy, self.token, call_limit]


class DensityContainer(containers.DeclarativeContainer):
    """density container class for density functionality support"""

    # create config container for variable storage
    config = providers.Configuration()

    # create dependency instance
    loader = providers.Factory(
        SetUpDensity,
        token=config.token,
        coordinate=config.coordinate,
        unit_in=config.unit_in,
        unit_out=config.unit_out,
        radius=config.radius,
        reverse_param=config.reverse_param,
        custom_option=config.custom_option,
        custom_utility=config.custom_utility
    )


# noinspection PyCompatibility
async def density_search_api(class_dependency: dict) -> dict:
    """density search endpoint functionality"""

    # create container instance
    container = DensityContainer()
    container.config.from_dict(class_dependency)

    fn, utility_obj, coordinates, radius, unit_in, unit_out, custom_query_value, strategy, token, call_limit = container.loader().set_up()

    # create call management background task
    await utility_obj.regulate_api_calls(token, 'single')

    date_task = create_task(utility_obj.get_datetime_objs())
    date_results = await date_task

    # check the call exceeding condition
    if call_limit - 1 >= 0:

        # deal with custom density search first
        if strategy is not None:
            result = create_task(fn.density_factory("custom", strategy=strategy, query_value=custom_query_value))
            result = await result
            utility_obj.close_client()

            # add user metrics
            await utility_obj.handle_user_metrics('density', token=token, radius=radius,
                                            unit_in=unit_in, unit_out=unit_out, density=result, custom=True)

            return success_density_response(result, date_results, unit_out, {'custom_utility': custom_query_value})

        # check if inputted radius exceeds the global variable set at top
        if exceeded_radius_check(radius, unit_in):
            return exceeded_radius_response(radius, unit_out, unit_in, coordinates, date_results)

        try:
            # create coroutines here
            result = await create_task(
                fn.density_factory("generic", coordinates=coordinates, radius=radius, unit_in=unit_in))
            utility_obj.close_client()

            await utility_obj.handle_user_metrics('density', token=token, radius=radius,
                                            unit_in=unit_in, unit_out=unit_out, density=result, custom=False)

            # handle API calls
            utility_obj.background_api_call_handler(token, 1, call_limit,
                                                    GlobalMetricManager().api_call_key)

            return success_density_response(result, date_results, unit_out, {"radius": radius, "coordinates": coordinates})

        # any error occurs
        except BrokenPipeError:
            # add user metrics
            utility_obj.handle_user_metrics('density', token=token, radius=radius,
                                            unit_in=unit_in, unit_out=unit_out, density='ISE')
            utility_obj.close_client()
            return NullResponses().internal_error

    else:
        # null calls response
        return NullResponses().exhausted_calls


########################### REVERSE GEOCODER ###################################


def success_single_reverse(date_results: dict, formatted_address: str, location: List[Union[float, int]],
                           radius: Union[float, int], address_components: dict, confidence: float):
    """create success case singular reverse geocoding response"""

    return {'meta': {'build': 'OK', 'status': 200, 'matching': 1,
                     'timestamps': {'date': date_results['date'],
                                    'time': date_results['time'],
                                    'official_timestamp': date_results['official_timestamp']},
                     'geocoded_data': {'format_address': formatted_address,
                                       'address_parts': address_components,
                                       'address_validation': True,
                                       'confidence': round(confidence, 1)}},
            'supplied_data': {'coordinates': location, 'radius': radius},
            'source': '©OpenStreetMap contributors'
            }


def poi_not_found_response(date_results: dict, formatted_address: Union[str, None], radius: int,
                           address_components: dict, location: List[Union[float, int]]) -> Dict:
    """not found response for place of interest"""

    return {'meta': {'build': 'POI_NULL', 'status': 200, 'matching': 0,
                     'timestamps': {'date': date_results['date'],
                                    'time': date_results['time'],
                                    'official_timestamp': date_results['official_timestamp']},
                     'geocoded_data': {'format_address': formatted_address,
                                       'address_parts': address_components,
                                       'address_validation': False,
                                       'confidence': 0.0}},
            'supplied_data': {'coordinates': location, 'radius': radius},
            'source': '©OpenStreetMap contributors'
            }


class SetUpReverse:
    """radius setup class for basic functionalities"""

    def __init__(self, token: str,
                 coordinate: List[Union[float, int]],
                 radius: Optional[Union[float, int]] = 10,
                 reverse_param: Optional[bool] = False
                 ):
        self.token = token
        self.coordinate = coordinate
        self.radius = radius
        self.reverse_param = reverse_param

    # noinspection PyCompatibility
    def set_up(self):
        """set up function for singular reverse geocoding endpoint"""

        # create backend object handlers
        utility_obj = PeekGeoUtilities(GeneralReverseManager)
        backend_obj = utility_obj.backend_utility

        coordinate = utility_obj.handle_coordinates(self.coordinate, self.reverse_param)

        # get the call limit
        call_limit = utility_obj.get_call_limit(self.token, GlobalMetricManager().api_call_key)

        # define response array
        return [backend_obj, utility_obj, coordinate, self.radius, call_limit, self.token]


class ReverseContainer(containers.DeclarativeContainer):
    """reverse container class creation"""

    # create configuration variable storage
    config = providers.Configuration()

    # create running instance of radius set up class
    loader = providers.Factory(
        SetUpReverse,
        token=config.token,
        coordinate=config.coordinate,
        radius=config.radius,
        reverse_param=config.reverse_param
    )


# noinspection PyCompatibility
async def reverse_geocode_api(class_dependency: dict) -> dict:
    """endpoint for single reverse geocoding requests"""

    # create container instance
    container = ReverseContainer()
    container.config.from_dict(class_dependency)

    # get set-up objects
    geocoding_library, utility_obj, location, radius, call_limit, token = container.loader().set_up()

    # add background task for closing mongo client
    utility_obj.close_client()

    # create call management background task
    await utility_obj.regulate_api_calls(token, 'single')

    # create datetime objects coroutine
    date_results = create_task(utility_obj.get_datetime_objs())

    # add user metrics
    await utility_obj.handle_user_metrics('reverse_single',
                                          coordinates=location, token=token)

    # check if API call limit was exceeded
    if call_limit - 1 >= 0:

        try:
            # client code request for backend reverse-geocoded data
            formatted_address, address_components, confidence = geocoding_library.single_reverse(location, radius)

            # get the date results from coroutine
            date_results = await date_results

            # check if the property response is empty (when poi is not found)
            if common_models.poi_not_found_check(formatted_address):
                return poi_not_found_response(date_results, formatted_address, radius, address_components, location)

            # deduct one api call from user profile
            utility_obj.background_api_call_handler(token, 1, call_limit,
                                                    GlobalMetricManager().api_call_key)

            return success_single_reverse(date_results, formatted_address, location, radius, address_components,
                                          confidence)

        except BrokenPipeError:
            # 505 internal error
            return NullResponses().property_not_found

    else:
        # null call response
        return NullResponses().exhausted_calls


############################### BATCH REVERSE GEO ENDPOINT ##################################


def batch_reverse_success(date_results: Dict, geocoded_data: List[Any], coordinates: List[list], radius: int):
    """create success response for batch reverse geocoding endpoint"""
    return {'meta': {'build': 'OK', 'status': 200, 'matching': len(geocoded_data),
                     'timestamps': {'date': date_results['date'],
                                    'time': date_results['time'],
                                    'official_timestamp': date_results['official_timestamp']},
                     'geocoded_data': geocoded_data},
            'supplied_data': {'coordinates': coordinates, 'radius': radius},
            'source': '©OpenStreetMap contributors'
            }


def batch_reverse_duplicate(date_results: Dict, repeated_edges, coordinates: List[list], radius: int):
    """create success response for batch reverse geocoding endpoint"""
    repeated_edges = [literal_eval(node) for node in repeated_edges]
    return {'meta': {'build': 'DUP', 'status': 400, 'matching': 0,
                     'timestamps': {'date': date_results['date'],
                                    'time': date_results['time'],
                                    'official_timestamp': date_results['official_timestamp']},
                     'geocoded_data': [{"repeated_edges": repeated_edges}]},
            'supplied_data': {'coordinates': coordinates, 'radius': radius},
            'source': '©OpenStreetMap contributors'
            }


class SetUpBatchReverse:
    """setup class for batch reverse geocoding"""

    def __init__(self, token: str,
                 latitudes: Optional[List[float]] = Query(None),
                 longitudes: Optional[List[float]] = Query(None),
                 radius: Optional[Union[int, float]] = 10,
                 coordinate_file: Optional[UploadFile] = File(None),
                 reverse_param: Optional[bool] = False
                 ):
        self.token = token
        self.latitudes = latitudes
        self.longitudes = longitudes
        self.radius = radius
        self.coordinate_file = coordinate_file
        self.reverse_param = reverse_param

    # noinspection PyCompatibility
    def set_up(self):
        """batch reverse geocoding functionality"""

        # create backend handlers
        utility_obj = PeekGeoUtilities(GeneralReverseManager)
        backend_obj = utility_obj.backend_utility

        # create the coordinates array regardless of File(...) input type
        coordinates = utility_obj.handle_batch_reverse_coords(self.latitudes, self.longitudes, self.reverse_param,
                                                              self.coordinate_file)

        # get call limit for user
        call_limit = utility_obj.get_call_limit(self.token, GlobalMetricManager().api_call_key)

        return [self.coordinate_file, backend_obj, utility_obj, "None", coordinates, self.reverse_param, self.radius,
                self.token, call_limit]


class BatchReverseContainer(containers.DeclarativeContainer):
    """create container instance for batch reverse geocoding"""

    # create configuration
    config = providers.Configuration()

    # running instance for setup class
    loader = providers.Factory(
        SetUpBatchReverse,
        token=config.token,
        latitudes=config.latitudes,
        longitudes=config.longitudes,
        radius=config.radius,
        coordinate_file=config.coordinate_file,
        reverse_param=config.reverse_param
    )


# noinspection PyCompatibility
async def batch_reverse_api(class_dependency: dict) -> dict:
    """batch reverse geocoding endpoint"""

    # create container
    container = BatchReverseContainer()
    container.config.from_dict(class_dependency)

    # get objects used for computation
    coordinate_file, geocoding_library, utility_obj, user_agent, coordinates, reverse_param, radius, token, call_limit = container.loader().set_up()

    # get the filename for logging purposes
    file_name = os.path.basename(__file__)

    # create call management background task
    await utility_obj.regulate_api_calls(token, 'single')

    # make date results coroutine
    dates = create_task(utility_obj.get_datetime_objs())

    # handle date coroutine
    date_results = await dates

    # check duplicate coordinates
    duplicate_check = duplicate_edge_check(coordinates)
    if type(duplicate_check) is not bool:
        return batch_reverse_duplicate(date_results, duplicate_check, coordinates, radius)

    # user metrics
    await utility_obj.handle_user_metrics('reverse_batch', token=token,
                                    coordinates=coordinates, batch_size=len(coordinates))

    if call_limit - 1 >= 0:
        try:
            # data from the batch geocoder in backend is returned
            data = geocoding_library.batch_reverse(coordinates, radius)
            utility_obj.close_client()

            # handle api calls, subtract
            utility_obj.background_api_call_handler(token, 1, call_limit,
                                                    GlobalMetricManager().api_call_key)

            # logging for user data
            await utility_obj.background_logging('AddUserLogger', '/Users/martinmashalov/Documents/Python/PeekGeo/Logs/BatchReverse.txt',
                                           'DEBUG','USER-AGENT: {}, Coordinates: {}, Arr_Len: {}, results: {}, file: {}'.format(
                                               user_agent, coordinates, len(coordinates), data[0], file_name))

            return batch_reverse_success(date_results, data, coordinates, radius)

        # internal server error
        except BrokenPipeError or BufferError:
            utility_obj.background_logging('AddUserLogger',
                                           '/Users/martinmashalov/Documents/Python/PeekGeo/Logs/ReverseGeocodingBatch.txt',
                                           'CRITICAL', 'USER-AGENT: {}, Buffer Error encountered'.format(user_agent))
            utility_obj.close_client()
            return NullResponses().internal_error

    else:
        # null call response
        return NullResponses().exhausted_calls


#################################### Single Geocoding Endpoint ########################################


def create_geocode_singe_success(date_results: dict, response_packet: list, supplied_packet: list) -> Dict:
    """create success response packet for singular geocoder"""
    return {'meta': {'build': 'OK', 'status': 200, 'matching': 1,
                     'timestamps': {'date': date_results['date'],
                                    'time': date_results['time'],
                                    'official_timestamp': date_results['official_timestamp']
                                    },
                     'geocoded_data': response_packet
                     },
            'supplied_data': supplied_packet,
            'source': '©OpenStreetMap contributors'
            }


class SetUpSingleForward:
    """create setup instance for forward geocoding function"""

    def __init__(self, token: str,
                 full_address: Optional[str] = None,
                 street: Optional[str] = None,
                 number: Optional[int] = None,
                 postcode: Optional[int] = None,
                 region: Optional[str] = None,
                 city: Optional[str] = None,
                 unit: Optional[str] = None,
                 ):
        self.token = token
        self.full_address = full_address
        self.street = street
        self.number = number
        self.postcode = postcode
        self.region = region
        self.city = city
        self.unit = unit

    # noinspection PyCompatibility
    def set_up(self):
        """singular geocoding computational object creation"""

        # backend object handlers
        utility_obj = PeekGeoUtilities(GeneralGeocodingManager)
        backend_obj = utility_obj.backend_utility

        # get the call limit
        call_limit = utility_obj.get_call_limit(self.token, GlobalMetricManager().api_call_key)

        # if address is None, then use the parsed input for address
        if self.full_address is None:
            # create parsed dictionary, with checks for accuracy
            try:
                if self.region.upper() in common_models.CommonUtilityModel().states and len(str(self.postcode)) == 5:
                    self.full_address: Dict = dict(street=self.street, number=self.number, state=self.region,
                                              postcode=self.postcode, city=self.city,
                                              unit=self.unit)
                    address_type = 0
                else:
                    raise HTTPException(
                        status_code=500,
                        detail='State must follow the abbreviations in the documentation; postcode must be a valid 5 digit postcode',
                        headers={"Error_Description": "Check type and formatting of postcode and street inputs"}
                    )
            except AttributeError:
                raise HTTPException(
                    status_code=404,
                    detail='Must include either parsed address or full address. No Input Detected',
                    headers={"Error_Description": "Fulfill address formatting requirements, check docs."}
                )

        # just return the full address string
        else:
            address_type = 1

        return [backend_obj, utility_obj, self.full_address, address_type, call_limit, self.token]


class SingleGeocodeContainer(containers.DeclarativeContainer):
    """create single geocoder container"""

    # create configuration
    config = providers.Configuration()

    # running instance of setup base class
    loader = providers.Factory(
        SetUpSingleForward,
        token=config.token,
        full_address=config.full_address,
        street=config.street,
        number=config.number,
        postcode=config.postcode,
        region=config.region,
        city=config.city,
        unit=config.unit
    )


# noinspection PyCompatibility
async def single_geocode_api(class_dependency: dict) -> dict:
    """singular geocoding endpoint"""

    # create container
    container = SingleGeocodeContainer()
    container.config.from_dict(class_dependency)

    # get computational objects
    geocoding_library, utility_obj, address, address_type, call_limit, token = container.loader().set_up()

    # create call management background task
    await utility_obj.regulate_api_calls(token, 'single')

    # create datetime coroutine
    dates = create_task(utility_obj.get_datetime_objs())

    # check the call limitations
    if call_limit - 1 >= 0:
        try:
            # add user metrics
            await utility_obj.handle_user_metrics('forward_single', token=token,
                                            address=address, full=0, parsed=1)

            # get the output
            output_packets = geocoding_library.singular_geocode(address, address_type)
            utility_obj.close_client()

            # await date coroutine
            date_results = await dates

            # subtract an api call in the background
            utility_obj.background_api_call_handler(token, 1, call_limit,
                                                    GlobalMetricManager().api_call_key)

            # make the response packet
            return create_geocode_singe_success(date_results, output_packets['response_packet'],
                                                output_packets['supplied_packet'])

        except ValueError:
            # 505 internal server response
            utility_obj.close_client()
            return NullResponses().internal_error

    else:
        # null call response
        return NullResponses().exhausted_calls


################################## Batch Geocoder Endpoint ####################################


def success_batch_forward(date_results, geocoded_data: dict) -> Dict:
    """create success case response packet for batch geocoding"""

    return {'meta': {'build': 'OK', 'status': 200, 'matching': len(geocoded_data['response_packet']),
                     'timestamps': {'date': date_results['date'],
                                    'time': date_results['time'],
                                    'official_timestamp': date_results['official_timestamp']
                                    },
                     'geocoded_data': geocoded_data['response_packet']
                     },
            'supplied_data': geocoded_data['supplied_packet'],
            'source': '©OpenStreetMap contributors'
            }


class SetUpBatchGeocode:
    """batch geocode setup base class"""

    def __init__(self, token: str,
                 addresses: List[str] = Query(None),
                 address_file: Optional[UploadFile] = File(None)
                 ):
        self.token = token
        self.addresses = addresses
        self.address_file = address_file

    # noinspection PyCompatibility
    def set_up(self):
        """batch geocoding backend code for FastAPI"""

        # backend object handlers
        utility_obj = PeekGeoUtilities(GeneralGeocodingManager)
        backend_obj = utility_obj.backend_utility

        # get call limit
        call_limit: int = utility_obj.get_call_limit(self.token, GlobalMetricManager().api_call_key)

        # address processing
        address_arr: list = utility_obj.handle_batch_reverse_addresses(self.addresses, self.address_file)

        return [backend_obj, utility_obj, address_arr,
                self.address_file.filename if self.address_file is not None else None,
                call_limit, self.token]


class BatchGeocodeContainer(containers.DeclarativeContainer):
    """container for batch reverse geocoding"""

    # create configuration for variable storage
    config = providers.Configuration()

    # running instance of base setup class
    loader = providers.Factory(
        SetUpBatchGeocode,
        token=config.token,
        addresses=config.addresses,
        address_file=config.address_file
    )


# noinspection PyCompatibility
async def batch_geocode_api(class_dependency: dict) -> dict:
    """batch geocoding endpoint function"""

    # create container
    container = BatchGeocodeContainer()
    container.config.from_dict(class_dependency)

    # create class object and other computational objects
    backend_obj, utility_obj, addresses, file_name, call_limit, token = container.loader().set_up()

    # create call management background task
    await utility_obj.regulate_api_calls(token, 'single')

    # create date_results coroutine
    date_results = create_task(utility_obj.get_datetime_objs())

    # add user metrics
    await utility_obj.handle_user_metrics('forward_batch', token=token,
                                    addresses=addresses,
                                    batch_size=len(addresses))

    # check call limitations
    if call_limit - 1 >= 0:
        # get date results here
        date_results = await date_results

        try:
            # get backend data
            data = backend_obj.batch_geocode(addresses)
            utility_obj.close_client()

            # add background task for call limit handling
            utility_obj.background_api_call_handler(token, 1, call_limit,
                                                    GlobalMetricManager().api_call_key)

            return success_batch_forward(date_results, data)

        except BrokenPipeError or BufferError:
            # internal error response
            utility_obj.close_client()
            return NullResponses().internal_error

    else:
        # null call response
        return NullResponses().exhausted_calls


############################### MAIN FACADE CLASS ###############################


class places:
    """places facade class for package contents"""

    def __init__(self, token: str):
        self.token: str = token

    @staticmethod
    def process_basic_args(additional_args: dict) -> bool:
        """process the basic arguments for load radius, convex, density, reverse, and batch reverse methods"""

        # reverse_parameter extraction
        try:
            reverse_param: Union[bool, None] = additional_args['reverse_param']
        except KeyError:
            reverse_param: Union[bool, None] = None

        return reverse_param

    def load_properties(self, coordinates: list = (), radius: Union[float, int] = 10, **additionals):
        """load properties facade for package purposes"""

        # get token and reverse parameter
        reverse_param = self.process_basic_args(additionals)

        # create and send response package
        return run(load_properties_api(
            {'coordinates': coordinates, 'radius': radius, 'token': self.token, 'reverse_param': reverse_param}))

    def convex(self, coordinates: list, **additionals) -> Any:
        """convex search facade method for places package"""

        # get token and reverse parameter
        reverse_param = self.process_basic_args(additionals)

        # create response and send it
        return convex_search_api({"token": self.token, "coordinates": coordinates, "reverse_param": reverse_param})

    def density(self, unit_in="ft", unit_out="ft", coordinate: list = None, radius: Union[float, int] = 1,
                custom_option: str = None, custom_utility: Union[float, int, str] = None, **additionals) -> Any:
        """density facade function for places package"""

        # get token and reverse parameter
        reverse_param = self.process_basic_args(additionals)

        return run(density_search_api(
            {"token": self.token, "coordinate": coordinate, "unit_in": unit_in, "unit_out": unit_out,
             "radius": radius, "reverse_param": reverse_param, "custom_option": custom_option,
             "custom_utility": custom_utility}))

    def reverse(self, coordinate: list = (), radius: Union[float, int] = 10, **additionals) -> Any:
        """reverse geocoding facade method for Places package"""
        # get token and reverse parameter
        reverse_param = self.process_basic_args(additionals)

        # create and send response packet
        return run(reverse_geocode_api({"token": self.token, "coordinate": coordinate, "radius": radius,
                                        "reverse_param": reverse_param}))

    def batch_reverse(self, coordinates: List[list] = (()), radius: Union[float, int] = 10, coordinate_file: UploadFile = None,
                      **additionals) -> Any:
        """batch reverse geocoding facade method for Places package"""

        # get token and reverse parameter
        reverse_param = self.process_basic_args(additionals)

        # create containers for lats and longs
        lats, longs = coordinate_conv_package.coords_conv(coordinates)

        # create and send response packet
        return run(batch_reverse_api({"token": self.token, "latitudes": lats, "longitudes": longs, "radius": radius,
                                  "coordinate_file": coordinate_file, "reverse_param": reverse_param}))

    def forward(self, full_address: str = None, street: str = None, number: Union[str, int] = None, postcode: int = None, region: str = None, city:
                      str = None, unit=None) -> Any:
        """facade method for forward geocoding on Places API"""

        return run(single_geocode_api(
            {"token": self.token, "full_address": full_address, "street": street, "number": number,
             "postcode": postcode, "region": region, "city": city, "unit": unit}))

    def batch_forward(self, addresses: list = (), address_file: UploadFile = None) -> Any:
        """batch forward facade method"""

        # create the send response
        return run(batch_geocode_api({"token": self.token, "addresses": addresses, "address_file": address_file}))


__all__ = [
    places
]
