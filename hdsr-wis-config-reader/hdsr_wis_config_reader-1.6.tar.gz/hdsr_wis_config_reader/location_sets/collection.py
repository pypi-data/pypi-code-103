from hdsr_wis_config_reader.location_sets.base import LocationSetBase
from hdsr_wis_config_reader.location_sets.hoofd import HoofdLocationSet
from hdsr_wis_config_reader.location_sets.msw import MswLocationSet
from hdsr_wis_config_reader.location_sets.ow import WaterstandLocationSet
from hdsr_wis_config_reader.location_sets.ps import PeilschaalLocationSet
from hdsr_wis_config_reader.location_sets.sub import SubLocationSet
from hdsr_wis_config_reader.readers.config_reader import FewsConfigReader
from typing import List

import pandas as pd  # noqa pandas comes with geopandas


class LocationSetCollection:
    def __init__(self, fews_config: FewsConfigReader):
        self.fews_config = fews_config
        self._hoofdloc_new = None
        self._hoofdloc = None
        self._subloc = None
        self._waterstandloc = None
        self._mswloc = None
        self._psloc = None

    def all(self) -> List[LocationSetBase]:
        return [self.hoofdloc, self.subloc, self.waterstandloc, self.mswloc, self.psloc]

    @property
    def hoofdloc(self) -> HoofdLocationSet:
        """Get HoofdLocationSet. The property .geo_df has eventually been updated."""
        if self._hoofdloc_new is not None:
            assert self._hoofdloc and isinstance(self._hoofdloc, HoofdLocationSet)
            assert isinstance(self._hoofdloc_new, pd.DataFrame)
            self._hoofdloc._geo_df = self._hoofdloc_new
        if self._hoofdloc is not None:
            return self._hoofdloc
        self._hoofdloc = HoofdLocationSet(fews_config=self.fews_config)
        return self._hoofdloc

    @property
    def subloc(self) -> SubLocationSet:
        if self._subloc is not None:
            return self._subloc
        self._subloc = SubLocationSet(fews_config=self.fews_config)
        return self._subloc

    @property
    def waterstandloc(self) -> WaterstandLocationSet:
        if self._waterstandloc is not None:
            return self._waterstandloc
        self._waterstandloc = WaterstandLocationSet(fews_config=self.fews_config)
        return self._waterstandloc

    @property
    def mswloc(self) -> MswLocationSet:
        if self._mswloc is not None:
            return self._mswloc
        self._mswloc = MswLocationSet(fews_config=self.fews_config)
        return self._mswloc

    @property
    def psloc(self) -> PeilschaalLocationSet:
        if self._psloc is not None:
            return self._psloc
        self._psloc = PeilschaalLocationSet(fews_config=self.fews_config)
        return self._psloc
