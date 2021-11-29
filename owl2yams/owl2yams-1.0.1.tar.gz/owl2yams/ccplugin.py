from cubicweb.toolsutils import Command
from cubicweb.cwctl import CWCTL
from cubicweb.cwconfig import CubicWebConfiguration as cwcfg
from cubicweb.server.serverctl import repo_cnx
from rdflib import Graph, RDF
from cubicweb import NoResultError, MultipleResultsError


@CWCTL.register
class ImportRDFDataCommand(Command):
    """Import RDF data from rdf file to an owl2yams generated instance

    <instance>
      an identifier for the instance
    """

    name = "import-rdf"
    arguments = "<instance>"
    min_args = max_args = 1
    options = (
        (
            "rdf-file",
            {
                "short": "f",
                "help": "The rdf file to import",
                "required": True,
                "type": "string",
            },
        ),
        (
            "parse-format",
            {
                "help": "Specify the RDF file serialization format",
                "type": "choice",
                "default": "turtle",
                "choices": ("turtle", "xml", "n3", "nquads", "nt", "trix"),
            },
        ),
    )

    def get_entity_from_uri(self, cnx, entity_uri, entity_type=None):
        if entity_type is not None:
            rql_query = (
                f"Any E Where E is {entity_type}, E equivalent_uri U, U uri %(uri)s"
            )
        else:
            rql_query = "Any E Where E equivalent_uri U, U uri %(uri)s"
        return cnx.execute(rql_query, {"uri": entity_uri}).one()

    def run(self, args):
        """run the command with its specific arguments"""
        rdf_file = self.config.rdf_file
        g = Graph()
        with open(rdf_file) as f:
            g.parse(f, format=self.config.parse_format)

        appid = args.pop(0)
        config = cwcfg.config_for(appid)
        repo, cnx = repo_cnx(config)

        with repo.internal_cnx() as cnx:
            # keep, for each created entity, the predicate_uri and object_uri to set non final
            # relation after creating entities
            temp_relations = {}

            for instance_uri, _, class_uri in g.triples((None, RDF.type, None)):
                temp_labels = []

                # Get entity type from equivalent_uri
                try:
                    entity_type = self.get_entity_from_uri(cnx, class_uri, "CWEType")
                except NoResultError:
                    print(
                        f"Did not import {instance_uri} as {class_uri} is unknown in the schema."
                    )
                    continue
                except MultipleResultsError:
                    print(
                        f"Did not import {instance_uri} as {class_uri} because"
                        " multiple types are possible."
                    )
                    continue

                # Get entity attribute
                try:
                    external_uri = cnx.find("ExternalUri", uri=instance_uri).one()
                except NoResultError:
                    external_uri = cnx.create_entity("ExternalUri", uri=instance_uri)
                temp_attributes = {"equivalent_uri": external_uri}
                for predicate_uri, object_value in g.predicate_objects(instance_uri):
                    relation_type = None
                    try:
                        relation_type = self.get_entity_from_uri(
                            cnx, predicate_uri, "CWRType"
                        )
                    except NoResultError:
                        if (
                            predicate_uri.toPython()
                            == "http://www.w3.org/2000/01/rdf-schema#label"
                        ):
                            label_entity = cnx.create_entity(
                                "Label", value=object_value.toPython()
                            )
                            temp_labels.append(label_entity)
                        else:
                            continue
                    except MultipleResultsError:
                        continue
                    if relation_type is None:
                        continue
                    if relation_type.final:
                        temp_attributes[relation_type.name] = object_value.toPython()
                    else:
                        if instance_uri not in temp_relations:
                            temp_relations[instance_uri] = []
                        temp_relations[instance_uri].append(
                            (relation_type, object_value)
                        )
                entity = cnx.create_entity(entity_type.name, **temp_attributes)
                entity.cw_set(label=tuple(temp_labels))

            for (instance_uri, relations) in temp_relations.items():
                try:
                    entity = self.get_entity_from_uri(cnx, instance_uri)
                except (NoResultError, MultipleResultsError):
                    continue
                for (relation, object_uri) in relations:
                    try:
                        object_entity = self.get_entity_from_uri(cnx, object_uri)
                    except (NoResultError, MultipleResultsError):
                        continue
                    set_relations = {}
                    set_relations[relation.name] = object_entity.eid
                    entity.cw_set(**set_relations)

            cnx.commit()
