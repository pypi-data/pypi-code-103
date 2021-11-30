from typing import Dict, Set

from cfn_tools import ODict, dump_json, CfnYamlLoader
from cfn_tools.yaml_dumper import TAG_MAP
from cloudrail.knowledge.context.aws.cloudformation.cloudformation_utils import CloudformationUtils

from common.api.dtos.supported_services_response_dto import SupportedSectionDTO

ELEMENT_POSITION_KEY: str = 'cfn_resource_block_position'
NODE_KEY_LINE_REGEX: str = '"{}"\\s*:'


# pylint: disable=R1710
class CustomCloudformationLoader(CfnYamlLoader):
    pass


def construct_mapping(self, node, deep=False):
    """
    Use ODict for maps
    """

    mapping = ODict()
    for key_node, value_node in node.value:
        key = self.construct_object(key_node, deep=deep)
        value = self.construct_object(value_node, deep=deep)
        mapping[key] = value

    if 'Type' in mapping and ELEMENT_POSITION_KEY not in mapping:
        mapping[ELEMENT_POSITION_KEY] = (node.start_mark.line, node.end_mark.line - 1)

    return mapping


CustomCloudformationLoader.add_constructor(TAG_MAP, construct_mapping)


class CloudformationHelper:

    EXTRA_PARAMETERS_KEY: str = 'cr_extra_params'

    @classmethod
    def create_filtered_cfn_template(cls, cfn_template_file: str,
                                     supported_services: Dict[str, SupportedSectionDTO],
                                     cfn_extra_params: dict = None) -> str:
        cfn_template_dict: dict = CloudformationUtils.load_cfn_template(cfn_template_file)
        cls.handle_include_resources(cfn_template_dict, supported_services)
        # self._handle_hashed_properties() # todo
        cfn_template_dict.update(ODict([[cls.EXTRA_PARAMETERS_KEY, CloudformationUtils.to_odict(cfn_extra_params or {})]]))
        return dump_json(cfn_template_dict)

    @staticmethod
    def handle_include_resources(cfn_template_dict: dict, supported_services: Dict[str, SupportedSectionDTO]) -> None:
        if supported_services:
            properties_to_include: Dict[str, Set[str]] = {}
            common_properties = supported_services.get('common', {})
            for resource_name, properties in supported_services.items():
                properties_to_include[resource_name] = set(properties.known_fields.pass_values)
                properties_to_include[resource_name].update(common_properties.known_fields.pass_values)
            del properties_to_include['common']

            for resource in cfn_template_dict.get('Resources').values():
                resource_type: str = resource['Type']
                properties: dict = resource.get('Properties', ODict())
                for property_name in properties.copy():
                    if property_name.lower() not in properties_to_include.get(resource_type, {}):
                        del properties[property_name]
