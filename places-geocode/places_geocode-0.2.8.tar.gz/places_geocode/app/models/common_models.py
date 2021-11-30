import pydantic
from typing import List, Optional, Union, Any
import sys


# noinspection PyCompatibility
class ObjModel(pydantic.BaseModel):
    """keep track of maxSize parameter of client initialization"""
    maxSize: Union[int, None]
    current_geographic_collection: Optional[str] = 'proplocations'
    current_accounts_collection: Optional[str] = 'apiusers'
    token_choices: Optional[List[str]] = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")


poi_not_found_check = lambda formatted_address: formatted_address == ''


# noinspection PyCompatibility
class CommonUtilityModel(pydantic.BaseModel):
    """common model for all overarching tasks"""
    earth_radius: Optional[float] = 6378.1 * 1000
    generator_threshold: Optional[int] = 250
    states: Optional[List[str]] = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
                                   "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                                   "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                                   "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                                   "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


# noinspection PyCompatibility
class PointsModel(pydantic.BaseModel):
    """points model here"""
    coordinates: List[List[Union[float, int]]]

    @pydantic.validator("coordinates")
    @classmethod
    def coordinate_val(cls, arr) -> List:
        if not isinstance(arr, list):
            raise Exception("Invalid Coordinate Array Inputted")
        else:
            return arr


def parse_coordinates_elastic(document: dict) -> List[Union[float, Any]]:
    """parse the elastic coordinates from elastic DB"""

    # get the location db object
    location_key: str = document['location']

    # remove whitespaces
    location_key = location_key.replace(" ", "")

    # capture latitude and longitude
    latitude, longitude = location_key.split(",")

    # type conversion for lat/long pair
    try:
        type_conv_latitude = float(latitude)
    except TypeError:
        type_conv_latitude = latitude

    try:
        type_conv_longitude = float(longitude)
    except TypeError:
        type_conv_longitude = longitude

    return [type_conv_latitude, type_conv_longitude]


def parse_coordinates_pymongo(document: dict) -> List[Union[int, float, None]]:
    """parse the pymongo document coordinates"""

    return document['location']['coordinates']