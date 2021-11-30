from enum import Enum
from hdsr_wis_config_reader.idmappings.sections import SectionTypeChoices
from hdsr_wis_config_reader.location_sets.base import LocationSetBase


class SubLocTypeChoices(Enum):
    pompvijzel = "pompvijzel"
    krooshek = "krooshek"
    stuw = "stuw"
    totaal = "totaal"
    vispassage = "vispassage"
    schuif = "schuif"
    debietmeter = "debietmeter"  # TODO: debietmeter can also be a hoofdlocatie..
    overlaat = "overlaat"
    afsluiter = "afsluiter"

    @classmethod
    def is_a_subloc(cls, value: str):
        return value in {cls.__members__.values()}


class SubLocationSet(LocationSetBase):
    @property
    def name(self):
        return "sublocaties"

    @property
    def fews_name(self):
        return "OPVLWATER_SUBLOC"

    @property
    def idmap_section_name(self):
        return SectionTypeChoices.kunstwerken.value

    @property
    def skip_check_location_set_error(self):
        return False

    @property
    def validation_rules(self):
        return [
            {"parameter": "H.R.", "extreme_values": {"hmax": "HR1_HMAX", "hmin": "HR1_HMIN"},},
            {"parameter": "H2.R.", "extreme_values": {"hmax": "HR2_HMAX", "hmin": "HR2_HMIN"},},
            {"parameter": "H3.R.", "extreme_values": {"hmax": "HR3_HMAX", "hmin": "HR3_HMIN"},},
            {"parameter": "F.", "extreme_values": {"hmax": "FRQ_HMAX", "hmin": "FRQ_HMIN"},},
            {"parameter": "Hh.", "extreme_values": {"hmax": "HEF_HMAX", "hmin": "HEF_HMIN"},},
            {
                "parameter": "POS.",
                "extreme_values": {"hmax": "PERC_HMAX", "smax": "PERC_SMAX", "smin": "PERC_SMIN", "hmin": "PERC_HMIN",},
            },
            {
                "parameter": "POS2.",
                "extreme_values": {
                    "hmax": "PERC2_HMAX",
                    "smax": "PERC2_SMAX",
                    "smin": "PERC2_SMIN",
                    "hmin": "PERC2_HMIN",
                },
            },
            {"parameter": "TT.", "extreme_values": {"hmax": "TT_HMAX", "hmin": "TT_HMIN"},},
            # HDSR does not yet have validation CSVs for berekend debiet
            # {"parameter": "Q.B.",
            #  "extreme_values": {"hmax": "Q_HMAX", "smax": "Q_SMAX", "smin": "Q_SMIN", "hmin": "Q_HMIN"}},
            {
                "parameter": "Q.G.",
                "extreme_values": {"hmax": "Q_HMAX", "smax": "Q_SMAX", "smin": "Q_SMIN", "hmin": "Q_HMIN",},
            },
            # TODO: I added krooshek below (see H.G.) as it was missing, but krooshek validation csv has:
            #   - 3 soft min: HW_SMIN, HO_SMIN, HZ_SMIN
            #   - 3 soft max: HW_SMAX, HO_SMAX, HZ_SMAX
            #  Roger, what do they mean? and what to choose?
            # background info:
            # noqa  LOC_ID	    STARTDATE   ENDDATE	HW_SMAX	HW_SMIN	HO_SMAX	HO_SMIN	HZ_SMAX	HZ_SMIN	H_HMAX	H_HMIN	H_RRRF	H_SARE	H_SAPE	H_RTS	H_TPS	code	opmerking  noqa
            #       KW100112	19000101	21000101							2791	1811	0.0003	5	2419200	0.0003	43200	2020-1  noqa
            #  {"internal": "H.G.", "external": "HG"}, --> moet bij krooshek
            #  {"internal": "H.G.", "external": "HB."},  --> moet bij krooshek
            #  {"internal": "H.G.", "external": "HO."}, --> moet bij krooshek
            {
                "parameter": "H.G.",
                "extreme_values": {"hmax": "H_HMAX", "smax": "HW_SMAX", "smin": "HW_SMIN", "hmin": "H_HMIN",},
            },
        ]
