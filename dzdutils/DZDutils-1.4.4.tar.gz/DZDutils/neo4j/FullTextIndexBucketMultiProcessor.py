import py2neo
import uuid
import threading
import time
from typing import Dict, List
from DZDutils.neo4j import nodes_to_buckets_distributor, run_periodic_iterate


class FullTextIndexBucketMultiProcessor:
    _iterate_bucket_prefix: str = "_Bucket_mp_iter_"
    _full_text_bucket_prefix: str = "_Bucket_mp_ft_"

    def __init__(self, graph: py2neo.Graph, buckets_count_per_collection: int = 10):
        self.graph = graph
        self.id = uuid.uuid4().hex[:6]
        self.buckets_count_per_collection = buckets_count_per_collection
        self.bucket_fulltext_index_names = {}

    def add_iterate_node_collection(self, name: str, query: str):
        self.iterate_collection_buckets: List[str] = nodes_to_buckets_distributor(
            self.graph,
            query,
            bucket_count=self.buckets_count_per_collection,
            bucket_label_prefix=f"{self._iterate_bucket_prefix}{self.id}_",
        )
        self.iterate_collection_name = name

    def add_fulltext_node_collection(
        self, name: str, query: str, fulltext_properties: List[str]
    ):
        self.fulltext_collection_buckets = nodes_to_buckets_distributor(
            self.graph,
            query,
            bucket_count=self.buckets_count_per_collection,
            bucket_label_prefix=f"{self._full_text_bucket_prefix}{self.id}_",
        )
        self.fulltext_collection_name = name
        self._create_bucket_full_text_index(fulltext_properties)

    def _create_bucket_full_text_index(self, properties: List[str]):
        for bucket_label in self.fulltext_collection_buckets:
            fti_name: str = f"{bucket_label}_FTI"
            q = f'Call db.index.fulltext.createNodeIndex("{fti_name}",["{bucket_label}"],{properties})'
            self.graph.run(q)
            self.bucket_fulltext_index_names[bucket_label] = fti_name
        self._wait_for_fulltextindex_build_up()

    def _wait_for_fulltextindex_build_up(self):
        build_up = True
        while build_up:
            indexes = self.graph.run(
                'SHOW INDEXES YIELD type, name, state WHERE type = "FULLTEXT"'
            ).to_data_frame()
            if not indexes.empty:
                bucket_index_names = list(self.bucket_fulltext_index_names.values())
                indexes_online = []
                for index, db_index_data in indexes.iterrows():
                    if (
                        db_index_data["name"] in bucket_index_names
                        and db_index_data["state"] == "ONLINE"
                    ):
                        indexes_online.append(db_index_data["name"])
                build_up = bool(len(bucket_index_names) != len(indexes_online))
            time.sleep(1)

    def clean_up(self, clean_orphean_full_text_index: bool = False):
        # delete fulltext indexes
        for bucket_label, index_name in self.bucket_fulltext_index_names.items():
            q = f"DROP INDEX {index_name}"
            self.graph.run(q)
        # delete bucket labels
        for bucket_label in (
            self.iterate_collection_buckets + self.fulltext_collection_buckets
        ):
            run_periodic_iterate(
                self.graph,
                cypherIterate=f"MATCH (n:{bucket_label}) return n",
                cypherAction=f"REMOVE n:{bucket_label}",
                parallel=True,
            )
        if clean_orphean_full_text_index:
            self._clean_up_orphean_buckets_and_indexes()

    def _clean_up_orphean_buckets_and_indexes(self):
        # delete indexes
        indexes = self.graph.run(
            'SHOW INDEXES YIELD type, name WHERE type = "FULLTEXT"'
        ).to_data_frame()
        if not indexes.empty:
            for index_name in indexes["name"].to_list():
                if index_name.startswith(self._full_text_bucket_prefix):
                    self.graph.run(f"DROP INDEX {index_name}")
        # delete labels
        labels: List[str] = (
            self.graph.run("call db.labels()").to_data_frame()["label"].tolist()
        )
        for label in labels:
            if label.startswith(self._full_text_bucket_prefix) or label.startswith(
                self._iterate_bucket_prefix
            ):
                run_periodic_iterate(
                    self.graph,
                    cypherIterate=f"MATCH (n:{label}) return n",
                    cypherAction=f"REMOVE n:{label}",
                    parallel=True,
                )

    @classmethod
    def _run_periodic_iterate_thread(cls, params: Dict):
        run_periodic_iterate(**params)

    def run_full_text_index(
        self,
        iterate_property,
        cypher_action,
    ):
        query_params_per_iter_bucket: Dict[str, List[Dict]] = {}
        # exmaple cypher_action
        # cypher_action = f"MERGE (source_col)<-[r:HAS_GENE]-(target_col)"

        # Collect query params
        for fti_bucket_label in self.fulltext_collection_buckets:
            bucket_fti_name = self.bucket_fulltext_index_names[fti_bucket_label]
            for iterate_bucket in self.iterate_collection_buckets:
                match_query = f"MATCH ({self.iterate_collection_name}:{iterate_bucket}) return {self.iterate_collection_name}"
                fti_query = f"""call db.index.fulltext.queryNodes('{bucket_fti_name}', '\\"' + {self.iterate_collection_name}.{iterate_property} + '\\"') yield node as {self.fulltext_collection_name},score"""
                action_query = f"{fti_query} {cypher_action}"
                if not iterate_bucket in query_params_per_iter_bucket:
                    query_params_per_iter_bucket[iterate_bucket] = []
                query_params_per_iter_bucket[iterate_bucket].append(
                    dict(
                        graph=self.graph,
                        cypherIterate=match_query,
                        cypherAction=action_query,
                    )
                )

        # Run queries parallel
        for bucket_name, querie_params in query_params_per_iter_bucket.items():
            # todo: refactor with pool executor https://realpython.com/intro-to-python-threading/#using-a-threadpoolexecutor
            threads = []
            for query_param in querie_params:
                t = threading.Thread(
                    target=self._run_periodic_iterate_thread, args=(query_param,)
                )
                threads.append(t)
                t.start()
            for t in threads:
                t.join()


def create_demo_data(g: py2neo.Graph):
    # create test nodes
    import graphio

    list_of_genes = [
        "A2M",
        "ABL1",
        "ACE2",
        "ACE212",
        "ACE2232fw",
        "CACNA1A",
        "CHEK2",
        "CREBBP",
        "CTNNB1",
        "EEF1E1",
        "EP300",
    ]
    nodeset = graphio.NodeSet(["Gene", "TestGenes"], merge_keys=["sid"])
    for gene in list_of_genes:
        nodeset.add_node(properties={"sid": gene})
    nodeset.create_index(g)
    nodeset.merge(g)

    abstract_texts = [
        "Lorem A2M ipsum ABL1 dolor ACE2-232.fw sit amet, consetetur CACNA1A sadipscing elitr, sed EP300 diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, EP300 consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum CHEK2 dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, CTNNB1 sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
        "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
    ]
    nodeset = graphio.NodeSet(["AbstractText", "TestAbstractText"], merge_keys=["text"])
    for text in abstract_texts:
        nodeset.add_node(properties={"text": text})
    nodeset.create_index(g)
    nodeset.merge(g)
