import sys
import os
import py2neo
from linetimer import CodeTimer
from py2neo.database import Graph


if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(
        os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
    )
    SCRIPT_DIR = os.path.join(SCRIPT_DIR, "..")
    sys.path.insert(0, os.path.normpath(SCRIPT_DIR))
from DZDutils.neo4j.LuceneTextCleanerTools import LuceneTextCleanerTools
from DZDutils.neo4j import nodes_to_buckets_distributor, run_periodic_iterate


def test_nodes_to_buckets_distributor():

    base_label = "_TEST_BUCKET_NODE"
    bucket_label_prefix = "_TEST_BUCKET_"
    number_of_nodes = 1000000
    bucket_size = 33333
    bucket_count = 33
    g = py2neo.Graph()

    # TEST BUCKET SIZE
    print(f"TEST bucket_size={bucket_size}")

    # clean the plate
    print("Clean old test nodes: ", f"MATCH (n:{base_label}) delete n")
    g.run(f"MATCH (n:{base_label}) delete n")
    print("Create test nodes")
    g.run(f"UNWIND range(1,{number_of_nodes}) as i CREATE (:{base_label})")
    # g.run(f"FOREACH ( i IN range(1,{number_of_nodes}) | CREATE (:{base_label}))")
    with CodeTimer("BucketDistribution", unit="s"):
        print("Start bucket Distribution")
        labels = nodes_to_buckets_distributor(
            g,
            query=f"MATCH (n:{base_label}) return n",
            bucket_size=bucket_size,
            bucket_label_prefix=bucket_label_prefix,
        )
    print("RESULT LABELS", labels)

    # TEST BUCKET COUNT
    print(f"TEST bucket_count={bucket_count}")

    # clean the plate
    print("Clean old test nodes: ", f"MATCH (n:{base_label}) delete n")
    g.run(f"MATCH (n:{base_label}) delete n")
    print("Create test nodes")
    g.run(f"UNWIND range(1,{number_of_nodes}) as i CREATE (:{base_label})")

    with CodeTimer("BucketDistribution", unit="s"):
        print("Start bucket Distribution")
        labels = nodes_to_buckets_distributor(
            g,
            query=f"MATCH (n:{base_label}) return n",
            bucket_count=bucket_count,
            bucket_label_prefix=bucket_label_prefix,
        )
    print("LABEL count", len(labels))
    print("RESULT LABELS", labels)


def test_run_periodic_iterate():
    g = py2neo.Graph()
    run_periodic_iterate(
        g,
        cypherIterate="MATCH (n:_TestNode) return n",
        cypherAction="SET n.prop = 'MyVal'",
        parallel=True,
    )


def test_LuceneTextCleaner():
    import py2neo
    import graphio
    from DZDutils.neo4j import LuceneTextCleanerTools

    g = py2neo.Graph()

    # lets create some testdata

    actorset = graphio.NodeSet(["Actor"], ["name"])
    # lets assume our actor names came from a messy source;
    for actor in [
        "The.Rock",
        "Catherine Zeta-Jones",
        "Keith OR Kevin Schultz",
        "32567221",
    ]:
        actorset.add_node({"name": actor})
    movieset = graphio.NodeSet(["Movie"], ["name"])
    for movie_name, movie_desc in [
        (
            "Hercules",
            "A movie with The Rock and other people. maybe someone is named Keith",
        ),
        (
            "The Iron Horse",
            "An old movie with the twin actors Keith and Kevin Schultz. Never seen it; 5 stars nevertheless. its old and the title is cool",
        ),
        (
            "Titanic",
            "A movie with The ship titanic and Catherine Zeta-Jones and maybe someone who is named Keith",
        ),
    ]:
        movieset.add_node({"name": movie_name, "desc": movie_desc})

    actorset.create_index(g)
    actorset.merge(g)
    movieset.create_index(g)
    movieset.merge(g)

    # We have our test data. lets start...

    # If we now would do create a fulltext index on `(:Movie).desc` and do a search by every actor name and create a relationship on every actor appearing in the description our result would be all over the place
    # e.g.
    #   * `Keith OR Kevin Schultz` would be connected to every movie because Keith comes up in every description. But actually we wanted to match  `Keith OR Kevin Schultz` but `OR` is an lucene operator
    #   * `Catherine Zeta-Jones` would appear in no description because the Hyphen expludes anything with `Jones`
    #   * `The.Rock` would appeat in no description because the data is dirty and there is a dot in his name

    # lets sanitize our actor names with LuceneTextCleanerTools
    txt = LuceneTextCleanerTools(g)
    txt.create_sanitized_property_for_lucene_index(
        labels=["Actor"],
        property="name",
        target_property="name_clean",
        min_word_length=2,
        max_word_count=3,
        min_word_count=2,
        exlude_num_only=False,
        to_be_escape_chars=["-"],
    )
    # this will cast our actor names to:
    # * "The.Rock" -> "The Rock"
    # * "Catherine Zeta-Jones" -> "Catherine Zeta\-Jones"
    # * "Keith OR Kevin Schultz" -> "Keith Kevin Schultz"

    #  The new value will be writen into a new property `name_clean`. No information is lost

    # optionaly, depending on what we want to do, we also can import common words in many languages

    txt.import_common_words(
        top_n_words_per_language=4000, min_word_length=2, max_word_length=6
    )

    # we can now tag actor names that are not suitable for full text matching
    txt.find_sanitized_properties_unsuitable_for_lucene_index(
        match_labels=["Actor"],
        check_property="name_clean",
        tag_with_labels=["_OmitFullTextMatch"],
        match_properties_equal_to_common_word=True,
    )

    # this would tag the Actor `32567221` which is only some ID for unsuitable. and remove the word "The" from rocks name

    # Now we can do our lucene full test matching on clean data :)


if __name__ == "__main__":
    test_nodes_to_buckets_distributor()
    exit()
    g = Graph()
    test_LuceneTextCleaner()
    exit()
    txt = LuceneTextCleanerTools(g)
    test_LuceneTextCleaner()
