from typing import Optional, List

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.distribution.distribution_data import DistributionData
from xlsx_lib.domain.power_supply.power_supply_component import PowerSupplyComponent
from xlsx_lib.domain.electronic.electronic_element import ElectronicElement

from xlsx_lib.domain.engine.engine_section import EngineSection
from xlsx_lib.domain.frame.frame_element import FrameElement
from xlsx_lib.domain.generic_replacements.replacement import Replacement
from xlsx_lib.domain.tightening_specifications.specification_element import SpecificationElement


class MotorcycleModel(CamelModel):
    model_name: str
    generic_replacements: Optional[List[Replacement]]
    tightening_specifications: Optional[List[SpecificationElement]]
    electronic: Optional[List[ElectronicElement]]
    engine: Optional[List[EngineSection]]
    frame: Optional[List[FrameElement]]
    power_supply: Optional[List[PowerSupplyComponent]]
    distribution: Optional[DistributionData]
