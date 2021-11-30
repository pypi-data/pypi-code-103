"""finite state machine (event-based) for unit conversion functionality on density endpoint"""

from state_machine import State, Event, acts_as_state_machine, after, InvalidStateTransition
from typing import Union, Callable, Optional, Any
from pydantic import BaseModel


# noinspection PyCompatibility
class StatesModel(BaseModel):
    """states and events base model"""

    # define the necessary states
    arbitrary_unit: Optional[Any] = State(initial=True)
    kilometer: Optional[Any] = State()
    mile: Optional[Any] = State()
    yard: Optional[Any] = State()
    foot: Optional[Any] = State()
    meter: Optional[Any] = State()

    class Config:
        """config class for arbitrary types"""
        arbitrary_types_allowed = True


# noinspection PyCompatibility
class EventsModelInput(BaseModel):
    """create events base model"""

    # create the inner states model and arbitrary unit type
    states = StatesModel()
    arbitrary_unit = states.arbitrary_unit

    # define processes/events
    to_ft: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.foot)
    to_mi: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.mile)
    to_m: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.meter)
    to_yd: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.yard)
    to_km: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.kilometer)

    class Config:
        """config class for arbitrary types"""
        arbitrary_types_allowed = True


# noinspection PyCompatibility
class EventsModelOutput(BaseModel):
    """output events defined in base model"""
    # create the inner states model and arbitrary unit type
    states = StatesModel()
    arbitrary_unit = states.arbitrary_unit

    # define events
    to_ft_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.foot)
    to_mi_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.mile)
    to_m_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.meter)
    to_yd_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.yard)
    to_km_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=states.kilometer)

    class Config:
        """config class for arbitrary types"""
        arbitrary_types_allowed = True


# noinspection PyCompatibility
@acts_as_state_machine
class UnitConversionsToFeet:

    """track the unit conversions"""

    # define the necessary states
    arbitrary_unit: Optional[Any] = State(initial=True)
    kilometer: Optional[Any] = State()
    mile: Optional[Any] = State()
    yard: Optional[Any] = State()
    foot: Optional[Any] = State()
    meter: Optional[Any] = State()

    # define processes/events
    to_ft: Optional[Any] = Event(from_states=arbitrary_unit, to_state=foot)
    to_mi: Optional[Any] = Event(from_states=arbitrary_unit, to_state=foot)
    to_m: Optional[Any] = Event(from_states=arbitrary_unit, to_state=foot)
    to_yd: Optional[Any] = Event(from_states=arbitrary_unit, to_state=foot)
    to_km: Optional[Any] = Event(from_states=arbitrary_unit, to_state=foot)

    # define output events
    to_m_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=meter)
    to_km_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=kilometer)
    to_yd_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=yard)
    to_ft_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=foot)
    to_mi_output: Optional[Any] = Event(from_states=arbitrary_unit, to_state=mile)

    def __init__(self, radius: Union[float, int], *conversion_algorithm):
        self.radius = radius
        self.unit_result: Union[int, float, None] = None
        self.conv_algorithm_outer: Union[None, Callable] = None
        self.conv_algorithm_inner: Union[None, Callable] = None

    @staticmethod
    def call_event(event: Callable) -> None:
        """call a class event"""
        event()

    @after('to_ft')
    def feet_conversion(self):
        """convert radius to feet"""
        self.unit_result = self.radius

    @after('to_m')
    def meter_conversion(self):
        """convert radius to meters"""
        self.unit_result = self.conv_algorithm_outer(self.radius)

    @after('to_yd')
    def yard_conversion(self):
        """convert radius to yards"""
        self.unit_result = self.radius * 3

    @after('to_mi')
    def mile_conversion(self):
        """convert radius to miles"""
        self.unit_result = self.conv_algorithm_outer(self.radius)

    @after('to_km')
    def km_conversion(self):
        """convert radius to kilometers"""
        self.unit_result = self.conv_algorithm_outer(self.conv_algorithm_inner(self.radius))

    @after('to_ft_output')
    def to_feet_conversion(self):
        """radius to feet for output"""
        self.unit_result = self.radius

    @after('to_m_output')
    def to_meter_conversion(self):
        """radius to meter for output"""
        self.unit_result = self.conv_algorithm_outer(self.radius)

    @after('to_mi_output')
    def to_mile_conversion(self):
        """radius to mile unit for output"""
        self.unit_result = self.conv_algorithm_outer(self.radius)

    @after('to_yd_output')
    def to_yard_conversion(self):
        """to yard conversion for radius output"""
        self.unit_result = self.conv_algorithm_outer(self.radius)

    @after('to_km_output')
    def to_kilometer_conversion(self):
        """radius to kilometers for output"""
        self.unit_result = self.conv_algorithm_inner(self.conv_algorithm_outer(self.radius))


# noinspection PyTypeHints,PyCompatibility
def state_machine_conversion_controller(conv_option, conv_class, *conversion_algorithm):
    """control the finite-state machine conversion process"""

    # process the *args conversion algorithms input
    try:
        conv_class.conv_algorithm_outer: Union[None, Callable] = conversion_algorithm[0]
    except IndexError:
        conv_class.conv_algorithm_outer: Union[None, Callable] = None

    try:
        conv_class.conv_algorithm_inner: Union[None, Callable] = conversion_algorithm[1]
    except IndexError:
        conv_class.conv_algorithm_inner: Union[None, Callable] = None

    # run the event
    try:
        conv_class.call_event(conv_option)
        return conv_class.unit_result
    except InvalidStateTransition:
        raise BufferError







