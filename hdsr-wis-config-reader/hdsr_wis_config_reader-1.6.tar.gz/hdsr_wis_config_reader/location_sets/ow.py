from hdsr_wis_config_reader.idmappings.sections import SectionTypeChoices
from hdsr_wis_config_reader.location_sets.base import LocationSetBase


class WaterstandLocationSet(LocationSetBase):
    @property
    def name(self):
        return "waterstandlocaties"

    @property
    def fews_name(self):
        return "OPVLWATER_WATERSTANDEN_AUTO"

    @property
    def idmap_section_name(self):
        return SectionTypeChoices.waterstandlocaties.value

    @property
    def skip_check_location_set_error(self):
        return False

    @property
    def validation_rules(self):
        return [
            {
                "parameter": "H.G.",
                "extreme_values": {
                    "hmax": "HARDMAX",
                    "smax_win": "WIN_SMAX",
                    "smax_ov": "OV_SMAX",
                    "smax_zom": "ZOM_SMAX",
                    "smin_win": "WIN_SMIN",
                    "smin_ov": "OV_SMIN",
                    "smin_zom": "ZOM_SMIN",
                    "hmin": "HARDMIN",
                },
            }
        ]
