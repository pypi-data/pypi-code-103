from .filesystem import write_graph
from .graph_common import add_common_elements, generate_generic_graph
from .provenance_uris import get_empty_prov_graph, add_prov_meta_information
from .graph_common import NS
from pathlib import Path
from rdflib import Graph, Literal, RDF, URIRef, XSD
from rdflib.namespace import RDFS, DC
from rdflib import Namespace
import csv
import re
import pandas
import sys
import os


def file_exists(indir, file):
    if not os.path.exists(Path(indir, file)):
        print("Please add file {} to directory {}".format(file, indir))
        sys.exit(1)


def generate_ystafdb_metadata_uris(args):
    output_base_dir = Path(args.outdir)
    input_base_dir = Path(args.indir)

    # ----------------- Provenance -------------------------

    # Start Provenance Graph and add info on providers
    # Get Empty Provenance Graph
    prov_graph = get_empty_prov_graph()
    prov_graph = add_prov_meta_information(prov_graph)

    if not os.path.exists(input_base_dir):
        print("Please add ystafdb csv data folder, and use argument -i <indir> from the cli to point at the folder")
        sys.exit(1)

    # Index of Super Dataset
    ystafdb_id = 0
    dataset_counter = 0

    # publication Data
    publication_file = "publications.csv"
    file_exists(input_base_dir, publication_file)
    file_path = os.path.join(input_base_dir, publication_file)
    publications = pandas.read_csv(
            file_path,
            header=0,
        )

    bprov_uri = "http://rdf.bonsai.uno/prov/ystafdb"
    bprov = Namespace("{}#".format(bprov_uri))
    prov = Namespace("http://www.w3.org/ns/prov#")
    dtype = Namespace("http://purl.org/dc/dcmitype/")
    spar = Namespace("http://purl.org/spar/datacite/")

    dataset_list = []
    for i in range(0, len(publications)):
        # TODO: author info missing
        author = publications['author'][i] if type(publications['author'][i]) != float else False
        title = publications['title'][i] if type(publications['title'][i]) != float else False
        doi = publications['doi'][i] if type(publications['doi'][i]) != float else False
        notes = publications['notes'][i] if type(publications['notes'][i]) != float else False
        pub_id = publications['publication_id'][i] if type(publications['publication_id'][i]) != float else False

        node = URIRef(bprov["dataset_{}".format(pub_id + dataset_counter)])
        dataset_counter += 1
        dataset_list.append(node)
        prov_graph.add((node, RDF.type, prov.Entity))
        prov_graph.add((node, spar.hasGeneralResourceType, dtype.Dataset))
        if doi:
            prov_graph.add((node, spar.hasIdentifier, Literal(doi, datatype=XSD.string)))
        if title:
            prov_graph.add((node, DC.title, Literal(title, datatype=XSD.string)))
        if notes:
            prov_graph.add((node, RDFS.label, Literal(notes, datatype=XSD.string)))

    # Add membership to super-dataset
    super_dataset = URIRef(bprov['dataset_{}'.format(ystafdb_id)])
    for dataset in dataset_list:
        prov_graph.add((super_dataset, prov.hadMember, dataset))

    # ------------------------- Locations -----------------------------------

    # Locations
    location_file = "reference_spaces.csv"
    file_exists(input_base_dir, location_file)
    file_path = os.path.join(input_base_dir, location_file)
    locations = pandas.read_csv(
        file_path,
        header=0,
    )

    ystafdb_location_uri = "http://rdf.bonsai.uno/location/ystafdb"
    g = add_common_elements(
        graph=Graph(),
        base_uri=ystafdb_location_uri,
        title="Custom locations for YSTAFDB",
        description="Country groupings used for YSTAFDB",
        author="Emil Riis Hansen",
        provider="Yale University",
        dataset="YSTAFDB"
    )
    g.bind("gn", "http://sws.geonames.org/")
    g.bind("brdflo", "{}#".format(ystafdb_location_uri))
    g.bind("schema", "http://schema.org/")

    for i, label in enumerate(locations['reference_space'], 1):
        node = URIRef("{}#L_{}".format(ystafdb_location_uri, i))

        g.add((node, RDF.type, URIRef("http://schema.org/Place")))
        g.add((node, RDFS.label, Literal(label)))
        g.add((URIRef(ystafdb_location_uri), NS.prov.hadMember, node))

    write_graph(output_base_dir / "location" / "ystafdb", g, args.format)

    # -------------------------- Activity Types ---------------------------------

    # Activity Types
    # Aggregate Subsystems
    activity_file = "aggregate_subsystem_modules.csv"
    file_exists(input_base_dir, activity_file)
    file_path = os.path.join(input_base_dir, activity_file)
    agg_subsystems = pandas.read_csv(
        file_path,
        header=0,
    )

    # Subsystems
    subsystem_file = "subsystems.csv"
    file_exists(input_base_dir, subsystem_file)
    file_path = os.path.join(input_base_dir, subsystem_file)
    subsystems = pandas.read_csv(
        file_path,
        header=0,
    )

    # Create all combinations of agg_subsystems and subsystems,
    # These are the Activity Types
    process_combinations = []
    for agg_id in agg_subsystems['aggregate_subsystem_module_id']:
        for sub_id in subsystems['subsystem_id']:
            process_combinations.append((agg_id, sub_id))

    # Create dictionaries for future usage
    agg_sub_dict = {i: x for i, x in zip(agg_subsystems["aggregate_subsystem_module_id"], agg_subsystems["aggregate_subsystem_module"])}
    sub_dict = {i: x for i, x in zip(subsystems["subsystem_id"], subsystems["subsystem"])}
    process_combinations = list(set(process_combinations))
    activity_type_dict_index = {"{}_{}".format(agg_sub, sub): index for index, (agg_sub, sub) in enumerate(process_combinations)}

    # ----------------------------- Flow Objects ----------------------------------

    # These are a combination of Reference_material and material_name, therefor
    # They can only be create when extracting flows, to omit instantiating combinations
    # Which makes no sense
    reference_mat_file = "reference_materials.csv"
    file_exists(input_base_dir, reference_mat_file)
    file_path = os.path.join(input_base_dir, reference_mat_file)
    reference_materials = pandas.read_csv(
        file_path,
        header=0,
    )

    # Material Names
    mat_name_file = "material_names.csv"
    file_exists(input_base_dir, mat_name_file)
    file_path = os.path.join(input_base_dir, mat_name_file)
    materials = pandas.read_csv(
        file_path,
        header=0,
    )

    # Create dictionaries for future usage
    reference_materials_dict = {i: x for i, x in zip(reference_materials["reference_material_id"], reference_materials["reference_material"])}
    materials_dict = {i: x for i, x in zip(materials["material_name_id"], materials["material_name"])}
    flow_object_dict = {}

    # ----------------------------- Units -------------------------------------

    # Dictionary to hold unit conversions
    unit_dict = {
        3: "megagram",
        4: "gigagram",
        5: "teragram",
        17: "gigabecquerel"
    }

    # ---------------------------- Reference Times ---------------------------------------

    # Extract reference times for later usage
    times_file = "reference_timeframes.csv"
    file_exists(input_base_dir, times_file)
    file_path = os.path.join(input_base_dir, times_file)
    times = pandas.read_csv(
        file_path,
        header=0,
    )

    times_dict = {i: x for i, x in zip(times["reference_timeframe_id"], times["reference_timeframe"])}

    # ----------------------------- Flows ----------------------------------

    "Extract all flow from the file, for each flow find which data is needed from other files"
    flows_file = "flows.csv"
    file_exists(input_base_dir, flows_file)
    file_path = os.path.join(input_base_dir, flows_file)
    with open(file_path) as file_handler:
        c = csv.reader(file_handler)
        data_rows = []
        print("Extracting flows from YSTAFDB")
        for i, line in enumerate(c):
            if i == 0:
                header = line
                continue
            dict1 = {}
            # Multiple delimiter characters ; and , are present, along with quotes.
            # Pandas is not good in this situation, therefor this conversion
            dict1.update({key: value for key, value in zip(header, re.split(',', ",".join(line)))})
            data_rows.append(dict1)
    print("Done Extracting flows from YSTAFDB")

    # Create graph for flows with common elements
    ystafdb_flow_uri = "http://rdf.bonsai.uno/data/ystafdb/huse"
    g = add_common_elements(
        graph=Graph(),
        base_uri=ystafdb_flow_uri,
        title="Custom locations for YSTAFDB",
        description="Country groupings used YSTAFDB",
        author="Emil Riis Hansen",
        provider="Yale University",
        dataset="YSTAFDB"
    )

    prov = Namespace("http://www.w3.org/ns/prov#")
    bont = Namespace("http://ontology.bonsai.uno/core#")
    brdffo = Namespace("http://rdf.bonsai.uno/flowobject/ystafdb#")
    om2 = Namespace("http://www.ontology-of-units-of-measure.org/resource/om-2/")
    brdfat = Namespace("http://rdf.bonsai.uno/activitytype/ystafdb#")
    brdftime = Namespace("http://rdf.bonsai.uno/time#")
    bloc = Namespace("http://rdf.bonsai.uno/location/ystafdb#")

    g.bind("bont", "http://ontology.bonsai.uno/core#")
    g.bind("flow", "http://rdf.bonsai.uno/data/ystafdb/huse#")
    g.bind("schema", "http://schema.org/")
    g.bind("brdffo", "http://rdf.bonsai.uno/flowobject/ystafdb#")
    g.bind("om2", "http://www.ontology-of-units-of-measure.org/resource/om-2/")
    g.bind("brdftime", "http://rdf.bonsai.uno/time#")
    g.bind("brdfat", "http://rdf.bonsai.uno/activitytype/ystafdb#")
    g.bind("bloc", "http://rdf.bonsai.uno/location/ystafdb#")

    flowCounter, activityCounter = 0, 0
    flows = pandas.DataFrame(data_rows, columns=header)
    flow_object_counter = 0
    balance_counter = 0
    error_counter = 0
    for x in range(0, len(flows)):
        reference_material_id = int(flows['reference_material_id'][x])
        reference_timeframe_id = int(flows['reference_timeframe_id'][x])
        reference_space_id = int(flows['reference_space_id'][x])
        subsystem_id_origin = int(flows['subsystem_id_origin'][x])
        aggregate_subsystem_module_id_origin = int(flows['aggregate_subsystem_module_id_origin'][x])
        subsystem_id_destination = int(flows['subsystem_id_destination'][x])
        aggregate_subsystem_module_id_destination = int(flows['aggregate_subsystem_module_id_destination'][x])
        material_name_id = int(flows['material_name_id'][x])
        quantity_unit_id = int(flows['quantity_unit_id'][x])
        publication_id = flows['publication_id'][x]

        # TODO: Sometimes quantity is Null, What to do in this case?
        if flows['quantity'][x] == "NULL":
            error_counter += 1
            continue
        else:
            quantity = float(flows['quantity'][x])

        # Combine reference_material and material_name
        ref_mat_name = reference_materials_dict[reference_material_id]
        mat_name = materials_dict[material_name_id]
        flow_object_name = "{};{}".format(mat_name, ref_mat_name)
        if flow_object_name not in flow_object_dict:
            flow_object_dict[flow_object_name] = flow_object_counter
            flow_object_counter += 1

        activity_type_index_orig = "{}_{}".format(aggregate_subsystem_module_id_origin, subsystem_id_origin)
        activity_type_index_dest = "{}_{}".format(aggregate_subsystem_module_id_destination, subsystem_id_destination)
        if activity_type_index_orig not in activity_type_dict_index or activity_type_index_dest not in activity_type_dict_index:
            error_counter += 1
            continue

        # Here we create the two activities linking the flow
        activity_input = URIRef("{}#A_{}".format(ystafdb_flow_uri, activityCounter))
        g.add((activity_input, RDF.type, URIRef(bont.Activity)))
        g.add((
            activity_input,
            bont.hasActivityType,
            URIRef("{}A_{}".format(brdfat, activity_type_dict_index[activity_type_index_orig]))
        ))
        g.add((
            activity_input,
            bont.hasTemporalExtent,
            URIRef(brdftime[times_dict[reference_timeframe_id].replace("-", "_")])
        ))
        g.add((activity_input, bont.hasLocation, URIRef("{}L_{}".format(bloc, reference_space_id))))
        activityCounter += 1

        activity_output = URIRef("{}#A_{}".format(ystafdb_flow_uri, activityCounter))
        g.add((activity_output, RDF.type, URIRef(bont.Activity)))
        g.add((
            activity_output,
            bont.hasActivityType,
            URIRef("{}A_{}".format(brdfat, activity_type_dict_index[activity_type_index_dest]))
        ))
        g.add((
            activity_output,
            bont.hasTemporalExtent,
            URIRef(brdftime[times_dict[reference_timeframe_id].replace("-", "_")])
        ))
        g.add((activity_output, bont.hasLocation, URIRef("{}L_{}".format(bloc, reference_space_id))))
        activityCounter += 1

        # Balanceable Property
        # We omit becquerel
        if quantity_unit_id != 17:
            balance = URIRef("{}#B_{}".format(ystafdb_flow_uri, balance_counter))
            g.add((balance, RDF.type, URIRef(bont.BalanceableProperty)))
            g.add((balance, bont.hasBalanceablePropertyType, om2.DryMass))
            g.add((balance, om2.hasNumericalValue, Literal(quantity, datatype=XSD.float)))
            g.add((balance, om2.hasUnit, URIRef(om2[unit_dict[quantity_unit_id]])))
            g.add((
                balance,
                RDFS.label,
                Literal("{};{} {}".format(ref_mat_name, quantity, unit_dict[quantity_unit_id]), datatype=XSD.string)
            ))
            balance_counter += 1

        # Here we create the Flow
        flow = URIRef("{}#F_{}".format(ystafdb_flow_uri, flowCounter))
        g.add((flow, RDF.type, URIRef(bont.Flow)))
        g.add((flow, bont.hasObjectType, URIRef("{}C_{}".format(brdffo, flow_object_dict[flow_object_name]))))
        g.add((flow, om2.hasUnit, URIRef(om2[unit_dict[quantity_unit_id]])))
        g.add((flow, bont.hasBalanceableProperty, balance))
        g.add((flow, om2.hasNumericalValue, Literal(quantity, datatype=XSD.float)))
        g.add((flow, bont.isInputOf, activity_input))
        g.add((flow, bont.isOutputOf, activity_output))
        flowCounter += 1

        # Provenance Information
        g.add((URIRef(ystafdb_flow_uri), NS.prov.hadMember, flow))
        g.add((URIRef(ystafdb_flow_uri), NS.prov.hadMember, activity_input))
        g.add((URIRef(ystafdb_flow_uri), NS.prov.hadMember, activity_output))
        g.add((URIRef(ystafdb_flow_uri), NS.prov.hadMember, balance))
        prov_uri = URIRef(bprov['dataset_{}'.format(publication_id)])
        prov_graph.add((prov_uri, prov.hadMember, flow))

        if x % 1000 == 0:
            print("Extracted {} flows and {} activities".format(x, x * 2))

    # Write Flows and Provenance graphs to file
    print("Extracted {} flows successfully".format(x))
    print("Encountered {} flows, which could not be extracted".format(error_counter))
    write_graph(output_base_dir / "prov" / "ystafdb", prov_graph, args.format)
    write_graph(output_base_dir / "flow" / "ystafdb/huse", g, args.format)

    # Write Flow Objects graph to file
    flow_object_list = [[x, "C_{}".format(y)] for x, y in zip(flow_object_dict.keys(), flow_object_dict.values())]
    generate_generic_graph(
        output_base_dir,
        kind="FlowObject",
        data=flow_object_list,
        directory_structure=["ystafdb"],
        title="Yale Stocks and Flows Database Flow Objects",
        description="FlowObject instances needed for BONSAI modelling of YSTAFDB version 1.0",
        author="BONSAI team",
        provider="Yale University",
        dataset="YSTAFDB",
        format=args.format
    )

    # Write Activity Types graph to file
    activity_type_dict_names = {i: "{};{}".format(agg_sub_dict[agg_sub], sub_dict[sub]) for i, (agg_sub, sub) in enumerate(process_combinations)}
    activity_type_list = [[y, "A_{}".format(x)] for x, y in zip(activity_type_dict_names.keys(), activity_type_dict_names.values())]
    generate_generic_graph(
        output_base_dir,
        kind="ActivityType",
        data=sorted(activity_type_list),
        directory_structure=["ystafdb"],
        title="Yale Stocks and Flows Database Activity Types",
        description="ActivityType instances needed for BONSAI modelling of YSTAFDB version 1.0",
        author="BONSAI team",
        provider="Yale University",
        dataset="YSTAFDB",
        format=args.format
    )
