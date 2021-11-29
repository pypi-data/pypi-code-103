import logging
import unittest
import pathlib
from io import StringIO
from rdflib import Graph
from typing import Optional, Dict
from owl2yams import owl_model_to_yams
from yams.schema import Schema
from logilab.common.graph import ordered_nodes

TEST_DATA = pathlib.Path(__file__).parent / "data"


def mock_serialize_to_python(schema: Schema) -> str:
    out = StringIO()
    w = out.write
    w("from yams.buildobjs import *\n\n")

    graph: Dict = {}

    for entity in schema.entities():
        graph.setdefault(entity, [])

    for e in ordered_nodes(graph):
        if not e.final:
            if e._specialized_type:
                base = e._specialized_type
            else:
                base = "EntityType"
            w("class %s(%s):\n" % (e.type, base))
            attr_defs = list(e.attribute_definitions())
            if attr_defs:
                for attr, obj in attr_defs:
                    w("    %s = %s()\n" % (attr.type, obj.type))
            else:
                w("    pass\n")
            w("\n")

    for r in schema.relations():
        if not r.final:
            if r.subjects() and r.objects():
                w("class %s(RelationDefinition):\n" % r.type)
                w(
                    "    subject = (%s,)\n"
                    % ", ".join("'%s'" % x for x in sorted(r.subjects()))
                )
                w(
                    "    object = (%s,)\n"
                    % ", ".join("'%s'" % x for x in sorted(r.objects()))
                )
                w("\n")
            else:
                logging.warning(
                    "relation definition %s missing subject/object" % r.type
                )

    return out.getvalue()


#  This mock is needed since this issue is not fixed:
#  https://forge.extranet.logilab.fr/open-source/yams/-/issues/3
serialize_to_python = mock_serialize_to_python


class Owl2YamsTC(unittest.TestCase):
    def _load_owl_and_yams(
        self,
        owl_model_file_name: str,
        yams_schema_file_name: Optional[str] = None,
    ):
        data_input = TEST_DATA / owl_model_file_name
        owl_model = Graph()
        owl_model.parse(str(data_input), format="turtle")

        (schema, _, _) = owl_model_to_yams(owl_model, "TEST")

        if yams_schema_file_name is not None:
            expected_output = TEST_DATA / yams_schema_file_name
            with open(expected_output) as f:
                expected_yams_schema = f.read()
            self.assertEqual(serialize_to_python(schema), expected_yams_schema)
        return schema

    def test_transform_class(self):
        self._load_owl_and_yams("test_class.owl", "test_class.yams")

    def test_transform_attribute(self):
        self._load_owl_and_yams("test_attribute.owl", "test_attribute.yams")

    def test_transform_relation(self):
        self._load_owl_and_yams("test_relation.owl", "test_relation.yams")

    def test_transform_hierarchy(self):
        self._load_owl_and_yams("test_hierarchy.owl", "test_hierarchy.yams")

    def test_transform_relation_without_domain_range(self):
        self._load_owl_and_yams(
            "test_relation_without_domain_range.owl",
            "test_relation_without_domain_range.yams",
        )

    def test_transform_attribute_owl_thing(self):
        self._load_owl_and_yams(
            "test_attribute_owl_thing.owl",
            "test_attribute_owl_thing.yams",
        )

    def test_transform_relation_multi_range(self):
        self._load_owl_and_yams(
            "test_relation_multi_range.owl",
            "test_relation_multi_range.yams",
        )

    def test_raise_multi_class(self):
        self._load_owl_and_yams("test_multi_class.owl", "test_multi_class.yams")

    def test_raise_multi_attribute(self):
        self._load_owl_and_yams("test_multi_attribute.owl", "test_multi_attribute.yams")

    def test_raise_multi_relation(self):
        self._load_owl_and_yams("test_multi_relation.owl", "test_multi_relation.yams")


if __name__ == "__main__":
    unittest.main()
