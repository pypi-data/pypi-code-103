from hdsr_wis_config_reader.readers.config_reader import FewsConfigReader
from hdsr_wis_config_reader.readers.xml_reader import XmlReader
from pathlib import Path
from typing import Dict
from typing import List

import geopandas as gpd
import logging
import re


logger = logging.getLogger(__name__)


class LocationSetBase:
    def __init__(self, fews_config: FewsConfigReader = None, fews_config_path: Path = None):
        assert (fews_config and not fews_config_path) or (
            fews_config_path and not fews_config
        ), "use either path or config"
        self.fews_config_path = fews_config_path
        self._fews_config = fews_config
        self._geo_df = None
        self._geo_df_original = None
        self._general_location_sets_dict = None
        self._csvfile_meta = None
        self._attrib_files = None

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def fews_name(self) -> str:
        raise NotImplementedError

    @property
    def idmap_section_name(self) -> str:
        raise NotImplementedError

    @property
    def skip_check_location_set_error(self) -> bool:
        raise NotImplementedError

    @property
    def validation_rules(self) -> Dict:
        raise NotImplementedError

    @property
    def fews_config(self) -> FewsConfigReader:
        if self._fews_config is not None:
            return self._fews_config
        self._fews_config = FewsConfigReader(path=self.fews_config_path)
        return self._fews_config

    @property
    def geo_df_original(self) -> gpd.GeoDataFrame:
        if self._geo_df_original is not None:
            return self._geo_df_original
        self._geo_df_original = self.fews_config.get_locations(location_set_key=self.fews_name)
        assert isinstance(self._geo_df_original, gpd.GeoDataFrame)
        return self._geo_df_original

    @property
    def geo_df(self) -> gpd.GeoDataFrame:
        if self._geo_df is not None:
            return self._geo_df
        self._geo_df = self.fews_config.get_locations(location_set_key=self.fews_name)
        assert isinstance(self._geo_df, gpd.GeoDataFrame)
        return self._geo_df

    @property
    def general_location_sets_dict(self) -> Dict:
        if self._general_location_sets_dict is not None:
            return self._general_location_sets_dict
        location_sets_file_path = self.fews_config.RegionConfigFiles["LocationSets"]
        location_sets_dict = XmlReader.xml_to_dict(xml_filepath=location_sets_file_path)
        self._general_location_sets_dict = location_sets_dict["locationSets"]["locationSet"]
        # ensure unique ids, e.g. 'OPVLWATER_HOOFDLOC', 'OPVLWATER_SUBLOC', 'RWZI', ..
        ids = [x["id"] for x in self._general_location_sets_dict]
        assert len(set(ids)) == len(ids), "we expected unique id's in RegionConfigFiles LocationSets"
        return self._general_location_sets_dict

    @property
    def csv_file_meta(self) -> Dict:
        """
        e.g. {
                'file': 'oppvlwater_hoofdloc',
                'geoDatum': 'Rijks Driehoekstelsel',
                'id': '%LOC_ID%',
                'name': '%LOC_NAME%',
                'description': 'Hoofdlocaties oppervlaktewater',
                etc..
            }
        """
        if self._csvfile_meta is not None:
            return self._csvfile_meta
        csvfile_meta = [loc_set for loc_set in self.general_location_sets_dict if loc_set["id"] == self.fews_name]
        assert len(csvfile_meta) == 1
        self._csvfile_meta = csvfile_meta[0]["csvFile"]
        return self._csvfile_meta

    @property
    def csv_filename(self) -> str:
        """e.g. 'oppvlwater_hoofdloc'"""
        return self.csv_file_meta["file"]

    @property
    def attrib_files(self) -> List:
        if self._attrib_files is not None:
            return self._attrib_files
        attribute_files = self.csv_file_meta.get("attributeFile", None)
        if not attribute_files:
            self._attrib_files = []
            return self._attrib_files
        if not isinstance(attribute_files, list):
            attribute_files = [attribute_files]
        assert all(
            [isinstance(attrib_file, dict) for attrib_file in attribute_files]
        ), "attribute_files must be list with dicts"
        self._attrib_files = [attrib_file for attrib_file in attribute_files if "attribute" in attrib_file]
        return self._attrib_files

    def get_validation_attributes(self, int_pars: List[str] = None) -> List[str]:
        """Get attributes (as a list) from validation rules (list with nested dicts).

        Example:
            validation_rules = [
                {
                    'parameter': 'H.R.',
                    'extreme_values': {'hmax': 'HR1_HMAX', 'hmin': 'HR1_HMIN'}
                },
                {
                    'parameter': 'H2.R.',
                    'extreme_values': {'hmax': 'HR2_HMAX', 'hmin': 'HR2_HMIN'}
                },
                    etc..
                ]

            get_validation_attributes(int_pars=None) returns: ['HR1_HMAX', 'HR1_HMIN', 'HR2_HMAX', 'HR2_HMIN']
        """
        if not int_pars:
            logger.debug(f"returning all validation parameters for locationset {self.name}")
            int_pars = [rule["parameter"] for rule in self.validation_rules]
        result = []
        for rule in self.validation_rules:
            if not any(bool(re.match(pattern=rule["parameter"], string=int_par)) for int_par in int_pars):
                continue
            result.extend(rule["extreme_values"].values())
        return result
