from abc import abstractmethod, ABCMeta
import sys
from time import perf_counter
from places_geocode.app.models import common_models
from elasticsearch.exceptions import ConflictError


# utilize bridge pattern: share the implementation of the logging functionality amongst all input types of input objects
class TrackUsers:
    """track user general class implementation"""

    def __init__(self, implementation):
        # instantialize implementation var
        self._implementation = implementation

    def handle_metrics(self, class_obj, time_now, date, **info_packet):
        """metric base handler function"""
        try:
            # pymongo
            database = class_obj.database_objs[common_models.ObjModel().current_accounts_collection]
        except KeyError:
            # elasticsearch
            database = class_obj.database_objs['connection']

        # create implementation of generalized metric model functionality here
        self._implementation().metric_recorder(class_obj, time_now, date, database, **info_packet)


# noinspection PyCompatibility, PyClassHasNoInit
class UserMetricRecorder(metaclass=ABCMeta):
    """metaclass for user metrics"""

    @abstractmethod
    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """
        :param class_function:
        :param time_now:
        :param date:
        :param info_packet:
        """
        pass


# noinspection PyClassHasNoInit
class RadiusMetrics(UserMetricRecorder):
    """implementation for radius metric recorder"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """record radius metrics"""
        radius = info_packet['radius']
        token = info_packet['token']

        database.update_one({'token': str(token)},
                            {'$push': {'user_metrics.radius.time': [time_now, date],
                                       'user_metrics.radius.radius': int(radius)}
                             })

        database.update_one({'token': token}, {'$inc': {'user_metrics.radius.hits': 1}})


# noinspection PyClassHasNoInit
class RadiusMetricsElastic(UserMetricRecorder):
    """radius metrics adjusted for elasticsearch"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet) -> None:
        """record radius metrics"""
        radius = float(info_packet['radius'])
        token = info_packet['token']
        index = common_models.ObjModel().current_accounts_collection

        # create body for user metrics
        body_metrics_time_radius = {
            "script": {
                "inline": "ctx._source.user_metrics.radius.time.add(params.update_time); ctx._source.user_metrics.radius.radius.add(params.radius); "
                          "ctx._source.user_metrics.radius.hits++",
                'params': {
                    'update_time': [time_now, date],
                    'radius': radius
                },
                "lang": "painless"
            },
            "query": {
                "match": {
                    "token": token
                }
            }
        }

        # do updates to database here
        try:
            database.update_by_query(index=index, body=body_metrics_time_radius)
        except ConflictError:
            database.indices.refresh(index=index)
            database.update_by_query(index=index, body=body_metrics_time_radius)


# noinspection PyClassHasNoInit
class ConvexMetrics(UserMetricRecorder):
    """convex metrics implementation"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """convex metric record"""
        area = info_packet['area']
        edge_count = info_packet['edge_count']
        token = info_packet['token']

        database.update({'token': token},
                        {'$push': {'user_metrics.convex.time': [time_now,
                                                                date],
                                   'user_metrics.convex.area': area,
                                   'user_metrics.convex.edges_count': edge_count}
                         }
                        )

        database.update({'token': token}, {'$inc': {'user_metrics.convex.hits': 1}})


# noinspection PyClassHasNoInit
class ConvexMetricsElastic(UserMetricRecorder):
    """convex metrics class adjusted for elasticsearch"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder interior function for convex elasticsearch"""

        # parse for update components
        area = info_packet['area']
        edge_count = info_packet['edge_count']
        token = info_packet['token']

        # collect desired index for elasticsearch update query
        index = common_models.ObjModel().current_accounts_collection

        # create outgoing query bodies
        body_push_metrics = {
            "script": {
                "inline": f"ctx._source.user_metrics.convex.time.add(params.update_time);"
                          f"ctx._source.user_metrics.convex.area.add(params.area);"
                          f"ctx._source.user_metrics.convex.edges_count.add(params.edge_count); "
                          f"ctx._source.user_metrics.convex.hits++",
                "lang": "painless"
            },
            'params': {
                'update_time': [time_now, date],
                'area': area,
                'edges_count': edge_count
            },
            "query": {
                "match": {
                    "token": token
                }
            }
        }

        # compute update queries
        try:
            database.update_by_query(index=index, body=body_push_metrics)
        except ConflictError:
            database.indices.refresh(index=index)
            database.update_by_query(index=index, body=body_push_metrics)


# noinspection PyClassHasNoInit
class DensityMetrics(UserMetricRecorder):
    """density metrics implementation"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """record density metrics"""
        unit_in, unit_out, radius, density, custom, token = info_packet['unit_in'], \
                                                            info_packet['unit_out'], \
                                                            info_packet['radius'], \
                                                            info_packet['density'], \
                                                            info_packet['custom'], \
                                                            info_packet['token']

        database.update({'token': token},
                        {'$push': {'user_metrics.density.time': [time_now,
                                                                 date],
                                   'user_metrics.density.radius': radius,
                                   'user_metrics.density.unit_in': unit_in,
                                   'user_metrics.density.unit_out': unit_out,
                                   'user_metrics.density.density': density,
                                   'user_metrics.density.custom': custom
                                   }}
                        )

        database.update({'token': token}, {'$inc': {'user_metrics.density.hits': 1}})


# noinspection PyClassHasNoInit
class DensityMetricsElastic(UserMetricRecorder):
    """density metrics adjusted for elasticsearch"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder function for elasticsearch"""

        # find the desired update query for elasticsearch
        index = common_models.ObjModel().current_accounts_collection

        # query for update components
        unit_in, unit_out, radius, density, custom, token = info_packet['unit_in'], \
                                                            info_packet['unit_out'], \
                                                            float(info_packet['radius']), \
                                                            info_packet['density'], \
                                                            info_packet['custom'], \
                                                            info_packet['token']

        # create outgoing requests bodies
        body_update_components = {
            "script": {
                "inline": f"ctx._source.user_metrics.density.time.add(params.updated_time); "
                          f"ctx._source.user_metrics.density.radius.add(params.radius); "
                          f"ctx._source.user_metrics.density.unit_in.add(params.unit_in); "
                          f"ctx._source.user_metrics.density.unit_out.add(params.unit_out); "
                          f"ctx._source.user_metrics.density.density.add(params.density); "
                          f"ctx._source.user_metrics.density.custom.add(params.custom); "
                          f"ctx._source.user_metrics.density.hits++",
                'params': {
                    'updated_time': [time_now, date],
                    'radius': radius,
                    'unit_in': unit_in,
                    'unit_out': unit_out,
                    'density': density,
                    'custom': custom
                },
                "lang": "painless"
            },
            "query": {
                "match": {
                    "token": token
                }
            }
        }

        # compute update queries
        try:
            database.update_by_query(index=index, body=body_update_components)
        except ConflictError:
            database.indices.refresh(index=index)
            database.update_by_query(index=index, body=body_update_components)


# noinspection PyClassHasNoInit
class SingleReverseMetrics(UserMetricRecorder):
    """single reverse metrics"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder for pymongo"""
        coordinates, token = info_packet['coordinates'], info_packet['token']

        database.update({'token': token},
                        {'$push': {'user_metrics.reverse_single.time': [time_now,
                                                                        date],
                                   'user_metrics.reverse_single.coordinates': coordinates}
                         }
                        )

        database.update({'token': token}, {'$inc': {'user_metrics.reverse_single.hits': 1}})


# noinspection PyClassHasNoInit
class SingleReverseMetricsElastic(UserMetricRecorder):
    """single reverse geocoding metrics adjusted for elasticsearch"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder function for elasticsearch single reverse"""

        # get desired update index for query
        index = common_models.ObjModel().current_accounts_collection

        # get update components
        coordinates, token = info_packet['coordinates'], info_packet['token']

        # create request outgoing bodies
        body_update_components = {
            "script": {
                "inline": f"ctx._source.user_metrics.reverse_single.time.add(params.update_time); "
                          f"ctx._source.user_metrics.reverse_single.coordinates.add(params.coordinates); "
                          f"ctx._source.user_metrics.reverse_single.hits++",
                'params': {
                    'update_time': [time_now, date],
                    'coordinates': coordinates
                },
                "lang": "painless"
            },
            "query": {
                "match": {
                    "token": token
                }
            }
        }

        # compute queries with update one option
        try:
            database.update_by_query(index=index, body=body_update_components)
        except ConflictError:
            database.indices.refresh(index=index)
            database.update_by_query(index=index, body=body_update_components)


# noinspection PyClassHasNoInit
class BatchReverseMetrics(UserMetricRecorder):
    """batch reverse metrics"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """batch reverse metric recorder function"""
        batch_size, coordinates, token = info_packet['batch_size'], info_packet['coordinates'], info_packet['token']

        database.update({'token': token},
                        {'$push': {'user_metrics.reverse_batch.time': [time_now,
                                                                       date],
                                   'user_metrics.reverse_batch.coordinates': coordinates,
                                   'user_metrics.reverse_batch.batch_size': batch_size}
                         }
                        )

        database.update({'token': token}, {'$inc': {'user_metrics.reverse_batch.hits': 1}})


# noinspection PyClassHasNoInit
class BatchReverseMetricsElastic(UserMetricRecorder):
    """batch reverse geocoding - elasticsearch adjusted"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder for elasticsearch batch reverse geocoding"""

        # query common models for desired update index
        index = common_models.ObjModel().current_accounts_collection

        # get update components
        batch_size, coordinates, token = info_packet['batch_size'], info_packet['coordinates'], info_packet['token']

        # create outgoing request bodies
        body_update_components = {
            "script": {
                "inline": f"ctx._source.user_metrics.reverse_batch.time.add(params.update_time); "
                          f"ctx._source.user_metrics.reverse_batch.coordinates.add(params.coordinates); "
                          f"ctx._source.user_metrics.reverse_batch.batch_size.add(params.batch_size); "
                          f"ctx._source.user_metrics.reverse_batch.hits++",
                'params': {
                    'update_time': [time_now, date],
                    'coordinates': coordinates,
                    'batch_size': batch_size
                },
                "lang": "painless"
            },
            "query": {
                "match": {
                    "token": token
                }
            }
        }

        # compute update one queries
        try:
            database.update_by_query(index=index, body=body_update_components)
        except ConflictError:
            database.indices.refresh(index=index)
            database.update_by_query(index=index, body=body_update_components)


# noinspection PyClassHasNoInit
class SingleForwardMetrics(UserMetricRecorder):
    """single forward geocoding metrics here"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder for pymongo"""
        address, parsed_counter, full_counter, token = info_packet['address'], \
                                                       info_packet['parsed'], \
                                                       info_packet['full'], \
                                                       info_packet['token']

        database.update({'token': token},
                        {'$push': {'user_metrics.geocode_single.time': [time_now,
                                                                        date],
                                   'user_metrics.geocode_single.address': address}
                         }
                        )

        if full_counter == 1:
            database.update({'token': token},
                            {'$inc': {'user_metrics.geocode_single.full_address_count': 1,
                                      'user_metrics.geocode_single.hits': 1}})
        elif parsed_counter == 1:
            database.update({'token': token},
                            {'$inc': {
                                'user_metrics.geocode_single.parsed_address_count': 1,
                                'user_metrics.geocode_single.hits': 1}})


# noinspection PyClassHasNoInit
class SingleForwardMetricsElastic(UserMetricRecorder):
    """single forward geocoding adjusted for elasticsearch"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder for single forward geocoding - elasticsearch engine"""

        # get desired update index from common models
        index = common_models.ObjModel().current_accounts_collection

        # query for update components
        address, parsed_counter, full_counter, token = info_packet['address'], \
                                                       info_packet['parsed'], \
                                                       info_packet['full'], \
                                                       info_packet['token']

        # create outgoing request bodies for counter variables
        if full_counter == 1:
            body_update_components = {
                "script": {
                    "inline": f"ctx._source.user_metrics.geocode_single.time.add(params.update_time); "
                              f"ctx._source.user_metrics.geocode_single.hits++; "
                              f"ctx._source.user_metrics.geocode_single.full_address_count++",
                    'params': {
                        'update_time': [time_now, date],
                    },
                    "lang": "painless"
                },
                "query": {
                    "match": {
                        "token": token
                    }
                }
            }
        elif parsed_counter == 1:
            # create outgoing request bodies for component update variables
            body_update_components = {
                "script": {
                    "inline": f"ctx._source.user_metrics.geocode_single.time.add(params.update_time); "
                              f"ctx._source.user_metrics.geocode_single.hits++; "
                              f"ctx._source.user_metrics.geocode_single.parsed_address_count++",
                    'params': {
                        'update_time': [time_now, date],
                    },
                    "lang": "painless"
                },
                "query": {
                    "match": {
                        "token": token
                    }
                }
            }
        else:
            body_update_components = {}

        # compute update queries in elasticsearch
        try:
            database.update_by_query(index=index, body=body_update_components)
        except ConflictError:
            database.indices.refresh(index='apiusers')
            database.update_by_query(index=index, body=body_update_components)


# noinspection PyClassHasNoInit
class BatchForwardMetrics(UserMetricRecorder):
    """batch forward geocoding metrics here"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder for pymongo"""
        addresses, batch_size, token = info_packet['addresses'], info_packet['batch_size'], info_packet['token']

        database.update({'token': token},
                        {'$push': {'user_metrics.geocode_batch.time': [time_now,
                                                                       date],
                                   'user_metrics.geocode_batch.address': addresses,
                                   'user_metrics.geocode_batch.batch_size': batch_size}
                         }
                        )

        database.update({'token': token}, {'$inc': {'user_metrics.geocode_batch.hits': 1}})


# noinspection PyClassHasNoInit
class BatchForwardMetricsElastic(UserMetricRecorder):
    """batch forward geocoding metrics for elasticsearch"""

    def metric_recorder(self, class_function, time_now, date, database, **info_packet):
        """metric recorder for elastic search batch geocoding"""

        # find desired update query index
        index = common_models.ObjModel().current_accounts_collection

        # query for update components
        addresses, batch_size, token = info_packet['addresses'], str(info_packet['batch_size']), info_packet['token']

        # create outgoing request bodies
        body_update_components = {
            "script": {
                "inline": f"ctx._source.user_metrics.geocode_batch.time.add(params.update_time); "
                          f"ctx._source.user_metrics.geocode_batch.batch_size.add(params.batch_size); "
                          f"ctx._source.user_metrics.geocode_batch.hits++",
                'params': {
                    'update_time': [time_now, date],
                    'batch_size': batch_size
                },
                "lang": "painless"
            },
            "query": {
                "match": {
                    "token": token
                }
            }
        }

        # compute update queries for elasticsearch
        try:
            database.update_by_query(index=index, body=body_update_components)
        except ConflictError:
            database.indices.refresh(index=index)
            database.update_by_query(index=index, body=body_update_components)


# noinspection PyClassHasNoInit
class SpreadsheetReverseMetrics(UserMetricRecorder):
    """spreadsheet reverse metric handler"""

    def metric_recorder(self, class_function, time_now, date, **info_packet):
        batch_size, token = info_packet['batch_size'], info_packet['token']

        class_function.api_accounts.update({'token': token}, {'$inc': {'user_metrics.reverse_large_scale.hits': 1}})

        class_function.api_accounts.update({'token': token},
                                           {'$push': {'user_metrics.reverse_large_scale.time': [time_now,
                                                                                                date],
                                                      'user_metrics.reverse_large_scale.batch_size': batch_size}
                                            }
                                           )


# noinspection PyClassHasNoInit
class SpreadsheetForwardMetrics(UserMetricRecorder):
    """implementation of spreadsheet forward geocoding pattern"""

    def metric_recorder(self, class_function, time_now, date, **info_packet):
        batch_size, token = info_packet['batch_size'], info_packet['token']

        class_function.api_accounts.update({'token': token}, {'$inc': {'user_metrics.geocode_large_scaled.hits': 1}})

        class_function.api_accounts.update({'token': token},
                                           {'$push': {'user_metrics.geocode_large_scaled.time': [time_now,
                                                                                                 date],
                                                      'user_metrics.geocode_large_scaled.batch_size': batch_size}
                                            }
                                           )
