from shexer.shaper import Shaper
from test.const import default_namespaces

from shexer.consts import TURTLE


raw_graph = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Jimmy a foaf:Person ;  # Complete
	foaf:age "23"^^xsd:integer ;
	foaf:name "Jimmy" ;
	foaf:familyName "Jones" ;
	foaf:familyName "Jonas" ;
	foaf:knows ex:Bella ;
	foaf:knows ex:David ;
	foaf:knows ex:Sarah .

ex:Sarah a foaf:Person ;  # Complete implicit type for age
	foaf:age 22 ;
	foaf:name "Sarah" ;
	foaf:familyName "Salem" .

ex:Bella a foaf:Person ;  # Missing familyName
	foaf:age "56"^^xsd:integer ;
	foaf:name "Isabella" ;
	foaf:knows ex:Jimmy .

ex:David a foaf:Person ;  # Missing age and use knows
	foaf:name "David" ;
	foaf:knows ex:Sarah .

ex:HumanLike foaf:name "Person" ;  # foaf properties, but not explicit type.
	foaf:familyName "Maybe" ;
	foaf:age 99 .


ex:x1 rdf:type foaf:Document ;
	foaf:depiction "A thing that is nice" ;
	foaf:title "A nice thing" .


ex:x2 rdf:type foaf:Document ;
	foaf:title "Another thing" .

"""


def test_all_classes_g1():
    shaper = Shaper(
        raw_graph=raw_graph,
        namespaces_dict=default_namespaces(),
        all_classes_mode=True,
        disable_exact_cardinality=True,
        input_format=TURTLE,
        inverse_paths=True)
    str_result = shaper.shex_graph(string_output=True, acceptance_threshold=0)
    print(str_result)
    # self.assertTrue(file_vs_str_tunned_comparison(file_path=G1_ALL_CLASSES_NO_COMMENTS,
    #                                               str_target=str_result))

def test_remote():
    shape_map_raw = "SPARQL'select ?p where " \
                    "{ ?p <http://www.wikidata.org/prop/direct/P31> <http://www.wikidata.org/entity/Q14660> } " \
                    "LIMIT 1'@<Flag>"
    shaper = Shaper(shape_map_raw=shape_map_raw,
                    url_endpoint="https://query.wikidata.org/sparql",
                    namespaces_dict=default_namespaces(),
                    instantiation_property="http://www.wikidata.org/prop/direct/P31",
                    disable_comments=True,
                    depth_for_building_subgraph=1,
                    track_classes_for_entities_at_last_depth_level=False,
                    all_classes_mode=False,
                    inverse_paths=True)
    str_result = shaper.shex_graph(string_output=True)
    print(str_result)

if __name__ == "__main__":
    test_remote()
