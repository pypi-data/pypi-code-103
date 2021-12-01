from pydantic import BaseModel, validator
from typing import List, Optional, Union, Any, Tuple, Callable
import sys
from abc import ABC, abstractmethod
import places_geocode.app.generator_BSON as generator
from places_geocode.app.models import common_models



# noinspection PyCompatibility
class DensitySchema(BaseModel):
    """base model for density endpoint data"""
    units: Optional[List[str]] = ['km', 'mi', 'm', 'ft', 'yd']
    radius: Optional[Union[int, float]]
    region_area: Optional[Union[int, float]] = 0
    iterative_counter: Optional[int] = 0
    query: Optional[List[Any]] = []

    @validator("radius")
    @classmethod
    def validate_radius(cls, radius):
        """validate the radius inputted"""
        if not (isinstance(radius, int) or isinstance(radius, float)):
            raise Exception("Radius Datatype Incorrect")


def convert_generator_exp(mongo_obj: Any, generator_strategy: Callable, parser: Callable) -> List[Any]:
    """convert the generator"""
    query_arr = generator.handler_func(mongo_obj, generator_strategy(), parser, option=0)
    return query_arr


# Density (Custom) strategies below
class DensityStrategy(ABC):
    """abstract base class custom density strategies"""

    @abstractmethod
    def create_dense_strategy(self, collection, level: Union[str, None], generator_strategy: Callable, parser: Callable, *es) -> Tuple[List, int]:
        """create the density strategy"""
        pass


class StateDensityStrategy(DensityStrategy):
    """State strategy for custom density endpoints"""

    def create_dense_strategy(self, collection, level: Union[int, str, None], generator_strategy: Callable, parser: Callable, *es) -> Tuple[
        List, int]:
        """create the density strategy"""

        query = collection.find({
            'properties.region': level
        })
        query_arr = convert_generator_exp(query, generator_strategy, parser)
        try:
            length = len(query_arr)
        except TypeError:
            length = 0
        return query_arr, length

    @validator("level")
    @classmethod
    def _check_level(cls, level):
        if level not in CommonUtilityModel.states:
            raise Exception("State not Found")


class PostcodeDensityStrategy(DensityStrategy):
    """postcode strategy for density computation"""

    def create_dense_strategy(self, collection, level: Union[int, str, None], generator_strategy: Callable, parser: Callable, *es) -> Tuple[
        List, int]:
        """create the density strategy"""
        query = collection.find({
            'properties.postcode': str(level)
        })
        query_arr = convert_generator_exp(query, generator_strategy, parser)
        try:
            length = len(query_arr)
        except TypeError:
            length = 0
        return query_arr, length

    @validator("level")
    @classmethod
    def _check_level(cls, level):
        if len(level) != 5:
            raise Exception("Invalid Postcode Entered")


class CityDensityStrategy(DensityStrategy):
    """city density strategy for city approximation of parcel density"""

    def create_dense_strategy(self, collection, level: Union[int, str, None], generator_strategy: Callable, parser, *es) -> Tuple[
        List, int]:
        """create the density strategy"""
        query = collection.find({
            'properties.city': level
        })
        query_arr = convert_generator_exp(query, generator_strategy, parser)
        try:
            length = len(query_arr)
        except TypeError:
            length = 0
        return query_arr, length


def conduct_elastic_query(connection: Any, index: str, body: dict) -> list:
    """run the elastic query"""

    result = connection.search(index=index, body=body)['hits']['hits']
    return result


class DensityStrategyElastic(ABC):
    """density model class for elasticsearch"""

    @abstractmethod
    def create_dense_strategy(self, index: str, level: Union[str, None], generator_strategy: Callable, parser: Callable, *es) -> Tuple[
        List, int]:
        """create the density strategy involving elasticsearch implementing encapsulation design pattern"""
        pass


class StateDensityElastic(DensityStrategyElastic):
    """find the density of the state"""

    def create_dense_strategy(self, index: str, level: Union[str, None], generator_strategy: Callable, parser: Callable, *es) -> Tuple[List, int]:
        """make elastic density strategy for state-level query"""

        # create the query body input
        body = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"properties.region": level}}
                    ]
                }
            }
        }

        results = conduct_elastic_query(es[0], index, body)

        length = len(results)
        query_arr = convert_generator_exp(results, generator_strategy, parser)

        return query_arr, length

    @validator("level")
    @classmethod
    def _check_level(cls, level):
        if level not in common_models.CommonUtilityModel.states:
            raise Exception("State not Found")


class PostcodeDensityElastic(DensityStrategyElastic):
    """create postcode strategy option for elasticsearch"""

    def create_dense_strategy(self, index: str, level: Union[str, None], generator_strategy: Callable, parser: Callable, *es) -> Tuple[
        List, int]:
        """make density elastic pattern for postcodes"""

        body = {
            "query": {
                "bool": {
                    "should": [
                        {"term": {"properties.postcode": level}}
                    ]
                }
            }
        }

        # compute elasticsearch query
        results = conduct_elastic_query(es[0], index, body)

        try:
            length = len(results)
        except TypeError:
            length = 0

        # convert the array to coordinates
        query_arr = convert_generator_exp(results, generator_strategy, parser)

        return query_arr, length

    @validator("level")
    @classmethod
    def _check_level(cls, level):
        if len(level) != 5:
            raise Exception("Invalid Postcode Entered")


class CityDensityElastic(DensityStrategyElastic):
    """create elastic strategy for city density query"""

    def create_dense_strategy(self, index: str, level: Union[str, None], generator_strategy: Callable, parser: Callable, *es) -> Tuple[List, int]:
        """create the density strategy for general city queries"""

        # create the body of the query outgoing request
        body = {
            "query": {
                "fuzzy": {
                    "properties.city": {
                        "value": level,
                        "fuzziness": "AUTO",
                        "max_expansions": 50,
                        "prefix_length": 0,
                        "transpositions": True,
                        "rewrite": "constant_score"
                    }
                }
            }
        }

        results = conduct_elastic_query(es[0], index, body)

        try:
            length = len(results)
        except TypeError:
            length = 0

        query_arr = convert_generator_exp(results, generator_strategy, parser)

        return query_arr, length


def strategies_main(collection: Any, query_value: Union[int, str, None], strategy, generator_strategy: Callable, parser: Callable,
                    *es) -> Tuple:
    """return the correct strategy"""

    # test for presence of elastic request
    try:
        # elasticsearch option
        es = es[0]
        results = strategy.create_dense_strategy(collection, query_value, generator_strategy, parser, es)
    except IndexError:
        # pymongo option
        results = strategy.create_dense_strategy(collection, query_value, generator_strategy, parser)

    # send results to client code
    return results
