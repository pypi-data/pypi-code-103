from dataclasses import dataclass


@dataclass
class Indicator:
    Id: str
    Name: str
    Script: str
    FirstLevel: str
    SecondLevel: str


@dataclass
class SuperTrend(Indicator):
    Value_1: float
    Value_2: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0):
        super().__init__(Id="STD;Supertrend",
                         Name="SuperTrend",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2


@dataclass
class Volume(Indicator):
    Value_1: float
    Value_2: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0):
        super().__init__(Id="",
                         Name="Volume",
                         Script="Volume",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2


@dataclass
class TripleMovingAverages(Indicator):
    Value_1: float
    Value_2: float
    Value_3: float

    def __init__(self, Value_1: float = 0, Value_2: float = 0, Value_3: float = 0):
        super().__init__(Id="PUB;y784PkOKflCjfhCiCB4ewuC0slMtB8PQ",
                         Name="TripleMovingAverages",
                         Script="Script@tv-scripting-101!",
                         FirstLevel="",
                         SecondLevel="")
        self.Value_1 = Value_1
        self.Value_2 = Value_2
        self.Value_3 = Value_3
