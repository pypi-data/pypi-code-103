from yams.schema import Schema
from typing import Dict
import jinja2

entities_template = jinja2.Template(
    """
from cubicweb.entities import AnyEntity
from cubicweb.entities.adapters import EntityRDFAdapter
from cubicweb.predicates import is_instance
from cubicweb.rdf import NAMESPACES
from rdflib import URIRef, namespace, Literal
from rdflib.namespace import Namespace




class OWL2YAMSRDFAdapter(EntityRDFAdapter):
    __regid__ = "rdf"

    def __init__(self, _cw, **kwargs):
        super().__init__(_cw, **kwargs)
        NAMESPACES["cubicweb"] = Namespace(self._cw.cnx.base_url())

    def owl2yams_triples(self):
        OWL = self._use_namespace("owl")
        CW = self._use_namespace("cubicweb")
        RDFS = self._use_namespace("rdfs")
    {% for fragment, uri in entitytype_fragment_to_uri.items() %}
        yield(CW["{{fragment}}"], RDFS.subClassOf, URIRef("{{uri}}"))
    {% endfor %}
    {% for fragment, uri in relationtype_fragment_to_uri.items() %}
        yield(CW["{{fragment}}"], RDFS.subPropertyOf, URIRef("{{uri}}"))
    {% endfor %}
        if self.entity.label:
            for label in self.entity.label:
                yield(self.uri, RDFS.label, Literal(label.value))
        yield(CW["equivalent_uri"], RDFS.subPropertyOf, OWL.sameAs)
        if self.entity.equivalent_uri:
            yield (self.uri, OWL.sameAs, URIRef(self.entity.equivalent_uri[0].uri))

    def filter_rdf_type(self, triples):
        RDF = self._use_namespace("rdf")
        CW = self._use_namespace("cubicweb")
        for triple in triples:
            if triple == (self.uri, RDF.type, CW[self.entity.e_schema.type]):
                yield (self.uri, RDF.type, URIRef(self.entity.is_instance_of[0].cwuri))
            elif triple[1] not in [CW["cw_source"], CW["label"], CW["equivalent_uri"]]:
                yield triple


{% for fragment, uri in entitytype_fragment_to_uri.items() %}
class {{fragment}}RDFAdapter(OWL2YAMSRDFAdapter):
    __select__ = is_instance("{{fragment}}")

    def triples(self):
        yield from self.owl2yams_triples()
        yield from self.filter_rdf_type(super().triples())

class {{fragment}}(AnyEntity):
    __regid__ = "{{fragment}}"

    def dc_title(self):
        if self.label:
            return self.label[0].value
        prefered_relations = []
        for rschema, attrschema in self.e_schema.attribute_definitions():
            if rschema.meta:
                continue
            if "label" in rschema.type:
                prefered_relations.append(rschema.type)
            elif "title" in rschema.type:
                prefered_relations.append(rschema.type)
            elif "name" in rschema.type:
                prefered_relations.append(rschema.type)
        for prefered_relation in prefered_relations:
            value = self.cw_attr_value(prefered_relation)
            if value is not None:
                return self.printable_value(
                    rschema.type, value, attrschema.type, format="text/plain"
                )
        return super().dc_title()

{% endfor %}


class CWETypeOWL2YAMSRDFAdapter(OWL2YAMSRDFAdapter):
    __select__ = is_instance("CWEType")
    __regid__ = "rdf"

    def triples(self):
        CW = self._use_namespace("cubicweb")
        OWL = self._use_namespace("owl")
        yield(self.uri, OWL.sameAs, CW[self.entity.name])
        yield from self.owl2yams_triples()
        yield from super().triples()


class CWRTypeOWL2YAMSRDFAdapter(OWL2YAMSRDFAdapter):
    __select__ = is_instance("CWRType")
    __regid__ = "rdf"

    def triples(self):
        CW = self._use_namespace("cubicweb")
        OWL = self._use_namespace("owl")
        yield(self.uri, OWL.sameAs, CW[self.entity.name])
        yield from self.owl2yams_triples()
        yield from super().triples()


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, ())

"""
)


def generate_entities(
    schema: Schema,
    entitytype_fragment_to_uri: Dict[str, str],
    relationtype_fragment_to_uri: Dict[str, str],
) -> str:
    return entities_template.render(
        entitytype_fragment_to_uri=entitytype_fragment_to_uri,
        relationtype_fragment_to_uri=relationtype_fragment_to_uri,
    )
