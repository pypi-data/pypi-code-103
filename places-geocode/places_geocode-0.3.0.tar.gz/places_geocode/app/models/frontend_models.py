from pydantic import BaseModel
from enum import Enum
from typing import Union, Optional, List
from fastapi import HTTPException, Query


# noinspection PyCompatibility
def LoadRadiusModel(class_method):
    """load properties/radius endpoint data model"""

    class LoadRadiusModelInput(str, Enum):
        parcel = "parcel"
        roof_top = "roof_top"

    class TimestampsModel(BaseModel):
        date: str = None
        official_timestamp: float = None
        time: str = None

    class InternalCoordinateArray(BaseModel):
        latitude: Optional[Union[float, int, None]] = None
        longitude: Optional[Union[float, int, None]] = None
        address: Optional[str] = None

    class GeocodedData(BaseModel):
        load_radius: Optional[List[InternalCoordinateArray]] = []
        certainty: Optional[str] = None

    class WithinMeta(BaseModel):
        build: str = None
        geocoded_data: Optional[GeocodedData] = []
        matching: int = None
        status: int = None
        timestamps: Optional[TimestampsModel] = None

    class SuppliedDataModel(BaseModel):
        latitude: float = None
        longitude: float = None
        supplied_radius: int = None

    class MetaModel(BaseModel):
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[SuppliedDataModel] = []
        source: str

        class Config:
            orm_mode = True

    if class_method == 'meta':
        return MetaModel
    if class_method == 'lr':
        return LoadRadiusModelInput


# noinspection PyCompatibility
def ConvexSearchModel(class_method):
    """convex search endpoint data model"""

    class SearchModel(str, Enum):
        parcel = "parcel"
        rooftop = "roof_top"

    class TimestampsModel(BaseModel):
        date: str = None
        official_timestamp: float = None
        time: str = None

    class GeocodedDataModel(BaseModel):
        certainty: str = 'Computational Search'
        convex_array: List[dict] = []
        repeated_edges: Optional[List[list]] = []

    class WithinMeta(BaseModel):
        build: str = None
        geocoded_data: Optional[GeocodedDataModel] = {}
        matching: int = None
        status: int = None
        timestamps: Optional[TimestampsModel] = None

    class SuppliedDataModel(BaseModel):
        search_edges: Optional[List[List[float]]] = []

    class MetaModel(BaseModel):
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[SuppliedDataModel] = {}
        source: str

        class Config:
            orm_mode = True

    class DataModeIn(BaseModel):
        coordinates: List[List[float]] = Query(None)

    if class_method.lower() == 'mt':
        return MetaModel
    elif class_method.lower() == 'sm':
        return SearchModel
    elif class_method.lower() == 'dm':
        return DataModeIn
    else:
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error Description': "Check the details of specified error"}
        )


# noinspection PyMissingOrEmptyDocstring,PyCompatibility
def DensitySearch(method):
    """density endpoint data model"""

    class SearchModel(str, Enum):
        TwoDSphere = "2dSphere"
        HullCentroid = "ConvexHullCentroid"

    class DensityCustomOptions(str, Enum):
        state = 'state'
        postcode = 'postcode'
        city = 'city'

    class TimestampsModel(BaseModel):
        date: str = None
        official_timestamp: float = None
        time: str = None

    class GeocodedDataModel(BaseModel):
        density: Union[float, int]
        unit: str

    class WithinMeta(BaseModel):
        build: str = None
        geocoded_data: Optional[List[GeocodedDataModel]] = []
        matching: int = None
        status: int = None
        timestamps: Optional[TimestampsModel] = None

    class SuppliedDataModel(BaseModel):
        radius: Union[float, None, int]
        coordinates: Union[List[float], None, List[None]] = None

    class MetaModel(BaseModel):
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[List[SuppliedDataModel]] = []
        source: str

        class Config:
            orm_mode = True

    class DataModeIn(BaseModel):
        coordinates: List[List[float]] = Query(None)

    if method.lower() == 'mt':
        return MetaModel
    elif method.lower() == 'sm':
        return SearchModel
    elif method.lower() == 'dm':
        return DataModeIn
    elif method.lower() == 'do':
        return DensityCustomOptions
    else:
        # print('in else statement lie 933')
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error_Description': "Check the details of specified error"}
        )


# noinspection PyMissingOrEmptyDocstring,PyCompatibility
def SingleReverseModel(method):
    """singular geocoding models here"""

    class ReverseModel(str, Enum):
        rooftop = "roof_top"
        parcel_search = "parcel_search"
        centroid = "centroid"

    class TimestampsModel(BaseModel):
        date: str = None
        official_timestamp: float = None
        time: str = None

    class AddressParts(BaseModel):
        unit: Optional[str] = ''
        street: Optional[str] = ''
        number: Optional[Union[int, str]] = ''
        state: Optional[str] = ""
        postcode: Optional[Union[str, int]] = ''
        city: Optional[str] = ''

    class GeocodedDataModel(BaseModel):
        certainty: Union[str, None]
        format_address: Optional[str] = ''
        address_parts: Optional[AddressParts] = {}
        address_validation: Union[None, bool]
        confidence: Union[float, None]

    class WithinMeta(BaseModel):
        build: str = None
        geocoded_data: Optional[GeocodedDataModel] = {}
        matching: int = None
        status: int = None
        timestamps: Optional[TimestampsModel] = None

    class SuppliedDataModel(BaseModel):
        coordinates: List[float] = None
        radius: Optional[int] = None

    class MetaModel(BaseModel):
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[SuppliedDataModel] = {}
        source: str

        class Config:
            orm_mode = True

    class DataModeIn(BaseModel):
        coordinates: List[List[float]] = Query(None)

    if method.lower() == 'mt':
        return MetaModel
    elif method.lower() == 'sm':
        return ReverseModel
    elif method.lower() == 'dm':
        return DataModeIn
    else:
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error_Description': "Check the details of specified error"}
        )


# noinspection PyMissingOrEmptyDocstring,PyCompatibility
def BatchReverseModel(class_method):
    """batch reverse geocoding models"""

    class ReverseMapModel(str, Enum):
        rooftop = "roof_top"
        parcel_search = "parcel_search"
        centroid = "centroid"

    class TimestampsModel(BaseModel):
        date: str = None
        official_timestamp: float = None
        time: str = None

    class AddressParts(BaseModel):
        unit: Optional[str] = None
        street: Optional[str] = None
        number: Optional[Union[int, str]] = None
        region: Optional[str] = None
        postcode: Optional[Union[int, str]] = None
        city: Optional[str] = None

    class GeocodedDataModel(BaseModel):
        format_address: Union[str, None]
        coordinates: List[float]
        address_parts: Optional[AddressParts] = []
        address_validation: Union[None, bool]
        accuracy: Union[int, float, None]

    class DuplicateModel(BaseModel):
        repeated_edges: Optional[list] = []

    class WithinMeta(BaseModel):
        build: str = None
        geocoded_data: Optional[Union[List[GeocodedDataModel], List[DuplicateModel]]] = []
        matching: int = None
        status: int = None
        timestamps: Optional[TimestampsModel] = None

    class SuppliedDataModel(BaseModel):
        coordinates: List[list] = None
        radius: Optional[int] = None

    class MetaModel(BaseModel):
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[SuppliedDataModel] = None
        source: str

        class Config:
            orm_mode = True

    class DataModeIn(BaseModel):
        coordinates: List[List[float]] = Query(None)

    if class_method.lower() == 'mt':
        return MetaModel
    elif class_method.lower() == 'sm':
        return ReverseMapModel
    elif class_method.lower() == 'dm':
        return DataModeIn
    else:
        # print('in else statement lie 933')
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error_Description': "Check the details of specified error"}
        )


# noinspection PyCompatibility
def SingleGeocodeModel(class_method):
    """singular geocoding response model and more"""

    class ReverseMapModel(str, Enum):
        rooftop = "roof_top"
        parcel_search = "parcel_search"
        centroid = "centroid"

    class TimestampsModel(BaseModel):
        date: str
        official_timestamp: float
        time: str

    class GeocodedDataModel(BaseModel):
        coordinates: Optional[List[Union[float, None]]] = [None, None]
        accuracy: Union[float, None, int]
        address: Optional[Union[str, None, dict]] = None
        address_parts: Optional[dict] = {}

    class WithinMeta(BaseModel):
        build: str
        geocoded_data: Optional[List[GeocodedDataModel]] = []
        matching: int
        status: int
        timestamps: Optional[TimestampsModel] = None

    class AddressPartsModel(BaseModel):
        street: Union[str, None]
        number: Union[int, str, None]
        postcode: Union[int, str, None]
        state: Union[str, None]
        city: Union[str, None]
        unit: Union[str, None]

    class SuppliedDataModel(BaseModel):
        address: Optional[Union[AddressPartsModel, str]] = None

    class MetaModel(BaseModel):
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[List[SuppliedDataModel]] = None
        source: str

        class Config:
            orm_mode = True

    class DataModeIn(BaseModel):
        coordinates: List[List[float]] = Query(None)

    if class_method.lower() == 'mt':
        return MetaModel
    elif class_method.lower() == 'sm':
        return ReverseMapModel
    elif class_method.lower() == 'dm':
        return DataModeIn
    else:
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error_Description': "Check the details of specified error"}
        )


# noinspection PyCompatibility
def BatchGeocodeModel(class_method):
    """batch geocoding models"""

    class ReverseMapModel(str, Enum):
        rooftop = "roof_top"
        parcel_search = "parcel_search"
        centroid = "centroid"

    class TimestampsModel(BaseModel):
        date: str = None
        official_timestamp: float = None
        time: str = None

    class AddressPartsModel(BaseModel):
        street: Union[str, None]
        number: Union[str, int, None]
        postcode: Union[str, int, None]
        state: Union[str, None]
        city: Union[str, None]
        unit: Union[str, None]

    class GeocodedDataModel(BaseModel):
        coordinates: List[Union[float, None]] = None
        address_parts: Optional[Union[AddressPartsModel, str]] = None
        address: Optional[str] = None
        accuracy: Optional[float] = None

    class WithinMeta(BaseModel):
        build: str = None
        geocoded_data: Optional[List[GeocodedDataModel]] = None
        matching: int = None
        status: int = None
        timestamps: Optional[TimestampsModel] = None

    class SuppliedDataModel(BaseModel):
        address: Optional[AddressPartsModel] = None
        formatted_address: Union[str, None]

    class MetaModel(BaseModel):
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[List[SuppliedDataModel]] = None
        source: str

        class Config:
            orm_mode = True

    class DataModeIn(BaseModel):
        coordinates: List[List[float]] = Query(None)

    if class_method.lower() == 'mt':
        return MetaModel
    elif class_method.lower() == 'sm':
        return ReverseMapModel
    elif class_method.lower() == 'dm':
        return DataModeIn
    else:
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error_Description': "Check the details of specified error"}
        )


# noinspection PyCompatibility
class Subscription(BaseModel):
    """subscription frontend model"""
    token: str


# noinspection PyCompatibility
def Autocompletion(class_method):
    """singular geocoding response model and more"""

    class TimestampsModel(BaseModel):
        """timestamps model"""
        date: str
        official_timestamp: float
        time: str

    class AutocompletedDataModel(BaseModel):
        """geocoded data model"""
        accuracy: Union[float, None, int]
        corrected_address: Optional[Union[str, None, dict]] = None

    class WithinMeta(BaseModel):
        """under meta data model"""
        build: str
        geocoded_data: Optional[AutocompletedDataModel] = {}
        matching: int
        status: int
        timestamps: Optional[TimestampsModel] = None

    class AddressPartsModel(BaseModel):
        """address component model"""
        street: Union[str, None]
        number: Union[int, None]
        postcode: Union[int, None]
        state: Union[str, None]
        city: Union[str, None]
        unit: Union[str, None]

    class SuppliedDataModel(BaseModel):
        """supplied data"""
        full_address: Optional[Union[AddressPartsModel, str]] = None

    class MetaModel(BaseModel):
        """meta model"""
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[List[SuppliedDataModel]] = None
        source: str

        class Config:
            """enable orm mode"""
            orm_mode = True

    if class_method.lower() == 'mt':
        return MetaModel
    elif class_method.lower() == 'sm':
        return AutocompletedDataModel
    else:
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error_Description': "Check the details of specified error"}
        )


# noinspection PyCompatibility
def AddressParse(class_method):
    """singular geocoding response model and more"""

    class TimestampsModel(BaseModel):
        """timestamps model"""
        date: str
        official_timestamp: float
        time: str

    class ParsedDataModel(BaseModel):
        """geocoded data model"""
        accuracy: Union[float, None, int]
        address_parts: Optional[dict] = {}

    class WithinMeta(BaseModel):
        """under meta data model"""
        build: str
        geocoded_data: Optional[ParsedDataModel] = {}
        matching: int
        status: int
        timestamps: Optional[TimestampsModel] = None

    class AddressPartsModel(BaseModel):
        """address component model"""
        street: Union[str, None]
        number: Union[int, None]
        postcode: Union[int, None]
        state: Union[str, None]
        city: Union[str, None]
        unit: Union[str, None]

    class SuppliedDataModel(BaseModel):
        """supplied data"""
        full_address: Optional[Union[AddressPartsModel, str]] = None

    class MetaModel(BaseModel):
        """meta model"""
        meta: Optional[WithinMeta] = None
        supplied_data: Optional[List[SuppliedDataModel]] = None
        source: str

        class Config:
            """enable orm mode"""
            orm_mode = True

    if class_method.lower() == 'mt':
        return MetaModel
    elif class_method.lower() == 'sm':
        return ParsedDataModel
    else:
        raise HTTPException(
            status_code=505,
            detail='Invalid Data Model suggested',
            headers={'Error_Description': "Check the details of specified error"}
        )


