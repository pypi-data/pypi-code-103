from typing import TYPE_CHECKING, Optional, Iterable

if TYPE_CHECKING:
    from . import FxSurfaceParameters
    from ._models import VolatilitySurfacePoint
    from ._models._surface_output import SurfaceOutput
    from .._enums import Format


SurfaceParameters = Optional["FxSurfaceParameters"]
SurfaceLayout = Optional["SurfaceOutput"]
OptFormat = Optional["Format"]
OptVolatilitySurfacePoints = Optional[Iterable["VolatilitySurfacePoint"]]
