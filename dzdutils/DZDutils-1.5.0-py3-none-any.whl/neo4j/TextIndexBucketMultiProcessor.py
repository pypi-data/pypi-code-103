import py2neo
import uuid
import threading
import time
from typing import Dict, List
from DZDutils.neo4j import nodes_to_buckets_distributor, run_periodic_iterate, wait_for_index_build_up


class TextIndexBucketMultiProcessor:
    _iterate_bucket_prefix: str = "_Bucket_mp_iter_"
    _text_bucket_prefix: str = "_Bucket_mp_ft_"
    _pre_neo4j_4_4_no_index:bool = False

    def __init__(self, graph: py2neo.Graph, buckets_count_per_collection: int = 10):
        self.graph = graph
        self.id = uuid.uuid4().hex[:6]
        self.buckets_count_per_collection = buckets_count_per_collection
        self.bucket_text_index_names = {}

    def add_iterate_node_collection(self, name: str, query: str):
        self.iterate_collection_buckets: List[str] = nodes_to_buckets_distributor(
            self.graph,
            query,
            bucket_count=self.buckets_count_per_collection,
            bucket_label_prefix=f"{self._iterate_bucket_prefix}{self.id}_",
        )
        self.iterate_collection_name = name

    def add_text_node_collection(
        self, name: str, query: str, text_property: str
    ):
        self.text_collection_buckets = nodes_to_buckets_distributor(
            self.graph,
            query,
            bucket_count=self.buckets_count_per_collection,
            bucket_label_prefix=f"{self._text_bucket_prefix}{self.id}_",
        )
        self.text_collection_name = name
        self.text_collection_property = text_property
        self._create_bucket_text_index(text_property)

    def _create_bucket_text_index(self, property: str):
        for bucket_label in self.text_collection_buckets:
            ti_name: str = f"{bucket_label}_ti"
            q = f"CREATE TEXT INDEX {ti_name} FOR (n:{bucket_label}) ON (n.{property})"
            if not self._pre_neo4j_4_4_no_index:
                self.graph.run(q)
            self.bucket_text_index_names[bucket_label] = ti_name
        if not self._pre_neo4j_4_4_no_index:
            wait_for_index_build_up(self.graph,list(self.bucket_text_index_names.values()))

    def clean_up(self, clean_orphean_text_index: bool = False):
        # delete text indexes
        for bucket_label, index_name in self.bucket_text_index_names.items():
            q = f"DROP INDEX {index_name}"
            self.graph.run(q)
        # delete bucket labels
        for bucket_label in (
            self.iterate_collection_buckets + self.text_collection_buckets
        ):
            run_periodic_iterate(
                self.graph,
                cypherIterate=f"MATCH (n:{bucket_label}) return n",
                cypherAction=f"REMOVE n:{bucket_label}",
                parallel=True,
            )
        if clean_orphean_text_index:
            self._clean_up_orphean_buckets_and_indexes()

    def _clean_up_orphean_buckets_and_indexes(self):
        # delete indexes
        indexes = self.graph.run(
            'SHOW INDEXES YIELD type, name WHERE type = "text"'
        ).to_data_frame()
        if not indexes.empty:
            for index_name in indexes["name"].to_list():
                if index_name.startswith(self._text_bucket_prefix):
                    self.graph.run(f"DROP INDEX {index_name}")
        # delete labels
        labels: List[str] = (
            self.graph.run("call db.labels()").to_data_frame()["label"].tolist()
        )
        for label in labels:
            if label.startswith(self._text_bucket_prefix) or label.startswith(
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

    def run_text_index(
        self,
        iterate_property,
        cypher_action,
    ):
        query_params_per_iter_bucket: Dict[str, List[Dict]] = {}
        # exmaple cypher_action
        # cypher_action = f"MERGE (source_col)<-[r:HAS_GENE]-(target_col)"

        # Collect query params
        for ti_bucket_label in self.text_collection_buckets:
            bucket_ti_name = self.bucket_text_index_names[ti_bucket_label]
            for iterate_bucket in self.iterate_collection_buckets:
                match_query = f"MATCH ({self.iterate_collection_name}:{iterate_bucket}) return {self.iterate_collection_name}"
                ti_query = f"""MATCH ({self.text_collection_name}:{ti_bucket_label}) WHERE {self.text_collection_name}.{self.text_collection_property} CONTAINS toString({self.iterate_collection_name}.{iterate_property}) """
                action_query = f"{ti_query} {cypher_action}"
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

