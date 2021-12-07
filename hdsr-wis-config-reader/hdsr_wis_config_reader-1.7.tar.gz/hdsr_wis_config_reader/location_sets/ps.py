from hdsr_wis_config_reader.location_sets.base import LocationSetBase


class PeilschaalLocationSet(LocationSetBase):
    @property
    def name(self):
        return "peilschalen"

    @property
    def fews_name(self):
        return "OPVLWATER_PEILSCHALEN"

    @property
    def idmap_section_name(self):
        return ""

    @property
    def skip_check_location_set_error(self):
        return True

    @property
    def validation_rules(self):
        return []
