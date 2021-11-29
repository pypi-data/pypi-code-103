from typing import Dict
import jinja2

postcreate_template = jinja2.Template(
    """
yams_schema_mapping = {{ mapping }}
for name, uri, entity_type in yams_schema_mapping:

    equivalent_uri = find(entity_type,name=name).one()

    rset = find('ExternalUri', uri=uri)
    if len(rset) == 1:
        rset.one().cw_set(reverse_equivalent_uri=equivalent_uri)
    elif len(rset) == 0:
        create_entity('ExternalUri', reverse_equivalent_uri=equivalent_uri, uri=uri)

    commit()
"""
)


def generate_postcreate(
    entitytype_to_uri: Dict[str, str], relationtype_to_uri: Dict[str, str]
):

    mapping = []
    for yams_class_name, uri_with_namespace in entitytype_to_uri.items():
        mapping.append((yams_class_name, str(uri_with_namespace), "CWEType"))
    for yams_relation_name, uri_with_namespace in relationtype_to_uri.items():
        mapping.append((yams_relation_name, str(uri_with_namespace), "CWRType"))

    return postcreate_template.render(mapping=mapping)
