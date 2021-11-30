from enum import Enum
from hdsr_wis_config_reader.idmappings.files import IdMapChoices


class SectionTypeChoices(Enum):
    kunstwerken = "KUNSTWERKEN"
    waterstandlocaties = "WATERSTANDLOCATIES"
    mswlocaties = "MSWLOCATIES"


IDMAP_SECTIONS_MAPPER = {
    IdMapChoices.idmap_opvl_water_hymos.value: {
        SectionTypeChoices.kunstwerken.value: [{"section_end": "<!--WATERSTANDSLOCATIES-->"}],
        SectionTypeChoices.waterstandlocaties.value: [
            {"section_start": "<!--WATERSTANDSLOCATIES-->", "section_end": "<!--OVERIG-->",}
        ],
    },
    IdMapChoices.idmap_opvl_water.value: {
        SectionTypeChoices.kunstwerken.value: [
            {
                "section_start": "<!--KUNSTWERK SUBLOCS (old CAW id)-->",
                "section_end": "<!--WATERSTANDSLOCATIES (old CAW id)-->",
            },
            {
                "section_start": "<!--KUNSTWERK SUBLOCS (new CAW id)-->",
                "section_end": "<!--WATERSTANDSLOCATIES (new CAW id)-->",
            },
        ],
        SectionTypeChoices.waterstandlocaties.value: [
            {"section_start": "<!--WATERSTANDSLOCATIES (old CAW id)-->", "section_end": "<!--MSW (old CAW id)-->",},
            {"section_start": "<!--WATERSTANDSLOCATIES (new CAW id)-->", "section_end": "<!--MSW (new CAW id)-->",},
        ],
        SectionTypeChoices.mswlocaties.value: [{"section_start": "<!--MSW (new CAW id)-->"}],
    },
}
SECTION_TYPE_PREFIX_MAPPER = {
    SectionTypeChoices.kunstwerken.value: "KW",
    SectionTypeChoices.waterstandlocaties.value: "OW",
    SectionTypeChoices.mswlocaties.value: "(OW|KW)",
}
