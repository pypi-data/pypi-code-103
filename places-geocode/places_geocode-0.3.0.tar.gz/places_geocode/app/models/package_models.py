from pydantic import BaseModel
from typing import Optional, Tuple
from app.models import density_models


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
