from .filesystem import write_graph
from pathlib import Path
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import FOAF, SKOS, DC, OWL, XSD, DCTERMS
import datetime
from . import __version__
from .config_parser import get_config_data


def generate_foaf_uris(args):
    """Note the URIs needed for units. They all come from the Ontology of Units
    of Measure."""
    output_base_dir = Path(args.outdir)

    org = Namespace("https://www.w3.org/TR/vocab-org/")
    prov = Namespace("http://www.w3.org/ns/prov#")
    purl = Namespace("http://purl.org/dc/dcmitype/")
    bfoaf = Namespace("http://rdf.bonsai.uno/foaf/ystafdb#")
    bonsaifoaf = Namespace("http://rdf.bonsai.uno/foaf/bonsai#")
    bprov = Namespace("http://rdf.bonsai.uno/prov/ystafdb#")
    dtype = Namespace("http://purl.org/dc/dcmitype/")
    vann = Namespace("http://purl.org/vocab/vann/")

    g = Graph()
    g.bind("vann", vann)
    g.bind("org", org)
    g.bind("dtype", dtype)
    g.bind("skos", SKOS)
    g.bind("foaf", FOAF)
    g.bind("dc", DC)
    g.bind("dcterms", DCTERMS)
    g.bind("owl", OWL)
    g.bind("prov", prov)
    g.bind("bfoaf", bfoaf)
    g.bind("bonsaifoaf", bonsaifoaf)
    g.bind("bprov", bprov)

    node = URIRef("http://rdf.bonsai.uno/foaf/ystafdb")

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    g.add((node, RDF.type, dtype.Dataset))
    g.add((node, DC.creator, bonsaifoaf.bonsai))
    g.add((node, DC.description, Literal("Instances of Organizations")))
    g.add((node, vann.preferredNamespaceUri, URIRef(bfoaf)))
    g.add((node, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/3.0/")))
    g.add((node, DCTERMS.modified, Literal(today, datatype=XSD.date)))
    g.add((node, DC.publisher, bonsaifoaf.bonsai))
    g.add((node, DC.title, Literal("Organizations")))
    g.add((node, OWL.versionInfo, Literal(__version__)))

    # Dataset providers, comes from config.json file
    providers, _ = get_config_data()
    for provider in providers:
        providerUri = URIRef(bfoaf["provider_{}".format(provider['id'])])
        g.add((providerUri, RDF.type, org.Organization))
        g.add((providerUri, RDF.type, prov.Agent))
        g.add((providerUri, DC.title, Literal(provider['name'])))
        g.add(
            (
                providerUri,
                DC.description,
                Literal(provider['label'])
            )
        )
        g.add((providerUri, FOAF.homepage, URIRef(provider['homepage'])))
        g.add((node, prov.hadMember, providerUri))


    # Provenance
    g.add((node, RDF.type, prov.Collection))
    g.add((node, prov.wasAttributedTo, bonsaifoaf.bonsai))
    g.add((node, prov.wasGeneratedBy, bprov["dataExtractionActivity_{}".format(__version__.replace(".", "_"))]))
    g.add((node, prov.generatedAtTime, Literal(today, datatype=XSD.date)))
    g.add(
        (
            node,
            URIRef("http://creativecommons.org/ns#license"),
            URIRef("http://creativecommons.org/licenses/by/3.0/"),
        )
    )

    write_graph(output_base_dir / "foaf" / "ystafdb", g, args.format)
