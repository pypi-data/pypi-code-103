from hdsr_wis_config_reader.location_sets.base import LocationSetBase


class MswLocationSet(LocationSetBase):
    @property
    def name(self):
        return "mswlocaties"

    @property
    def fews_name(self):
        return "MSW_STATIONS"

    @property
    def idmap_section_name(self):
        return ""

    @property
    def skip_check_location_set_error(self):
        return True

    @property
    def validation_rules(self):
        return []
