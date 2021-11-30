from enum import Enum


class StatTypes(Enum):
    INVESTOR_TYPE = 1
    INVESTMENT_STYLE = 2
    REGION = 3
    ROTATION = 4
    COUNTRY = 5
    METRO_AREA = 6
    INVESTOR_TYPE_PARENT = 7
    INVESTOR_STYLE_PARENT = 8


class Frequency(Enum):
    QUARTERLY = "Q"
    MONTHLY = "M"


class SortOrder(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"
