import json, os, sys
from elasticsearch import RequestsHttpConnection
from elasticsearch.helpers import bulk
from elasticsearch_dsl import connections, Search, Document, UpdateByQuery, Q
import boto3, json
from tqdm.auto import tqdm
from collections import Counter
from requests_aws4auth import AWS4Auth
from typing import List, Optional, Dict, Union


class Manager(object):
	
	def __init__(self, hosts, access_key=None, secret_key=None, region='eu-west-3', service='es', use_ssl=True, verify_certs=True, timeout=60):
		
		if access_key is None or secret_key is None:
			credentials = boto3.Session().get_credentials()
			# access_key = credentials.access_key
			# secret_key = credentials.secret_key
			credentials = boto3.Session().get_credentials()
			awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
		else:
			awsauth = AWS4Auth(access_key, secret_key, region, service)
		# credentials = boto3.Session().get_credentials()
		# awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, config['ES']['REGION'], service, session_token=credentials.token)

		
		self.connect = connections.create_connection(
						hosts=hosts,
						timeout=timeout,
						http_auth = awsauth,
						use_ssl = use_ssl,
						verify_certs = use_ssl,
						connection_class = RequestsHttpConnection
					)


		
	def _check_field_cross_index(self, field_values, index, field):
		"""
		"""
		query_2 = {"query": {"terms": {field: field_values}}}
		res2 = self.get_from_index(index, query_2)
		return res2[1]



	def check_field_cross_index(self, from_index, to_index, field):
		"""

		"""
		query_1 = {"query": {"match_all": {}}}
		res1 = self.get_from_index(from_index, query_1)
		# print(type(list(res1[0])))
		field_values = [hit.to_dict().get(field, 'fake') for hit in res1[0]]
		print(len(field_values))
		return self._check_field_cross_index(field_values, to_index, field)
		# values = [self._check_field_cross_index(hit, to_index, field)   for hit in res1[0]]
		# return Counter(values)

			
	def get_index_as_partial_dict(self, index, cols):
		l = []
		search_dict = {
		"_source": cols,
		"query": {
		  "match_all": {  
		  }
		}
		}

		s = Search().from_dict(search_dict).index(index).scan()
		for hit in tqdm(s):
			d = hit.to_dict()
			d["_id"] = hit.meta.id
			l.append(d)
		return l
		

	def gendata(index, docs):
		for doc in docs:
			yield {
				"_op_type": "update",
				"_index": index,
				"_id": doc["_id"],
				"doc": {doc['column']: doc["value"]}
			}
		print("end gen")


	def get_from_index(self, index, body: [str, dict]):
		"""
		"""
		if isinstance(body, str):
			body = json.loads(body)


		results = Search().from_dict(body).index(index)
		results.execute()
		# print("#######ES query gives {} articles".format(results.count()))
		return (results.scan(), results.count())

		# for hit in results.scan():
		#     print(hit.to_dict()['DOI'])
		#     break
		# print("#######ES query gives {} articles".format(results.count()))

		
	def create_index(self, index_name: str, settings: None, erase_if_exists: bool=False):
		
		if settings is None:
			 settings = {
				"settings":{
					"number_of_shards":5,
					"number_of_replicas":1,
					"analysis":{
						"filter":{"backslash":{"pattern":"\\[a-z]","type":"pattern_replace","replacement":""},
						"english_snowball":{"type":"snowball","language":"English"},
						"english_stop":{"type":"stop","stopwords":"_english_"}},
						"analyzer":{
						"classic_analyzer":{
							"filter":["lowercase","backslash"],
							"char_filter":["html_strip"],
							"type":"custom",
							"tokenizer":"standard"},
						"stopword_analyzer":{
							"filter":["lowercase","backslash","english_stop","english_snowball"],
							"char_filter":["html_strip"],
							"type":"custom",
							"tokenizer":"standard"}
						}
					}
					},
					"mappings":{
					"properties":{
						"DOI":{"type":"keyword"},
						"prefix_doi": {"type": "keyword"},
						"URL":{"type":"keyword"},
						"abstract":{"type":"text","analyzer":"classic_analyzer","search_analyzer":"stopword_analyzer","search_quote_analyzer":"classic_analyzer"},
						"abstract_clean":{"type":"keyword"},
						"authors":{"type":"keyword"},
						"fullText":{"type":"text","analyzer":"classic_analyzer","search_analyzer":"stopword_analyzer","search_quote_analyzer":"classic_analyzer"},
						"fullText_clean":{"type":"text"},
						"keywords":{"type":"keyword"},
						"language":{"type":"keyword"},
						"openaire_id":{"type":"keyword"},
						"provider":{"type":"keyword"},
						"provider_id":{"type":"keyword"},
						"publication_date":{"type":"date","ignore_malformed":True,"format":"yyyy-mm-dd"},
						"title":{"type":"text"},
						"citation": {"type": "text"},
						# "ISBN": {"type": "keyword"},

						},
					}
			}
		
		if self.connect.indices.exists(index_name):
			print(index_name + " index already exists")
			if(erase_if_exists):
				print(index_name + " deleted and recreated")
				self.connect.indices.delete(index=index_name)
		try:
			self.connect.indices.create(index=index_name,body=settings,ignore=400)
		except Exception as e:
			print(e)
		
		
	def save_to_index(self, generator):
		print('Bulk starts')
		res = bulk(self.connect, generator, raise_on_error=False, raise_on_exception=False)
		print(res)
		



	def get_articles(self,
		keywords: List[str],
		field: str = 'content',
		index: str = 'publications',
		review: bool = False,
		date_start: Optional[str] = None,
		date_end: Optional[str] = None,
		page_start: Optional[int] = 0,
		page_end: Optional[int] = 100,
		**extra
	) -> Dict[str, Union[str, Dict[str, str]]]:

		"""
		Pull articles from index using keywords query
		
		keywords: (list) of keywords
		field: (str) field name to quieried
		index: (str) ES index name
		review: (bool) Filter for reviews only. Default False
		date_start: (str) Filter article from YYYY-MM-DD. Default None
		date_end: (str) Filter article until YYYY-MM-DD. Defaut None
		source: (list) of fields to be returned
		page_start: (int) Index article to start. Default 0
		page_end: (int) Index article to end > start. Default 10
		total_hits: (bool, int) If true, stops when all the documents are scanned.
			If int, stops if the limit is reached. Default 500
		
		:return: Dict[stats, hits]
		"""

		extras = {
			'from': page_start,
			'size': page_end,
			'track_total_hits': extra.get('total_hits', 500)
		}
		sources = extra.get(
			'source',
			["authors", "title", "DOI", "URLs", "publication_date", "pages",
			 "container-title", "volume", "issue", "chapter", "publisher",
			 "published-print", "editor", "address", "type", "citation", "abstract"]
		)
		highlight = {
			"type": "unified",
			"boundary_scanner": "sentence",
			"number_of_fragments": 3,
			"fragment_size": 100,
			"phrase_limit": 10,
			"boundary_scanner_locale": "en-US",
			"pre_tags": ["<span class='hglt'>"],
			"post_tags": ["</span>"]
		}

		review = int(review)
		filters = [Q('range', publication_date = {'gte': date_start, 'lte': date_end})]
		filters += [Q('term', **{field: 'review'})] if review else list()
		
		query = Q('bool',
		  should = [ Q(
			  'match', **{ field: {
				  'query': k,
				  'operator': "and",
				  'fuzziness': "AUTO:5,8",
				  'auto_generate_synonyms_phrase_query': False
			  }}) for k in keywords if k[0] != '-'
		  ],
		  must_not = [Q(
			  'match', **{ field: {
				  'query': k[1:],
				  'auto_generate_synonyms_phrase_query': False
			  }}) for k in keywords if k[0] == '-'
		  ],
		  minimum_should_match = 1,
		  filter = filters)
		
		resp = Search(index = index).extra(**extras).query(query).highlight(
			field, **highlight).source(sources).execute()
		
		hits = list(map(
			lambda x: {
				**x.to_dict(), 'highlights':
				x.meta.__dict__['_d_'].get('highlight', {}).get(field, [])
			}, resp.hits
		))
		results = {
			'hits': hits,
			'stats': {**resp.hits.total.to_dict(), 'took': resp.took}
		}
		return results


	  
	# def get_histogram(self,
	# keywords: List[str],
	# field: str = 'content',
	# index: str = 'publications',
	# date_start: Optional[str] = None,
	# date_end: Optional[str] = None,
	# **kwargs
	# ) -> Dict[str, Union[str, Dict[str, int]]]:
	
	# 	"""
	# 	Get histogram year articles from index using keywords query
		
	# 	keywords: (list) of keywords
	# 	field: (str) field name to quieried
	# 	index: (str) ES index name
	# 	date_start: (str) Filter article from YYYY-MM-DD. Default None
	# 	date_end: (str) Filter article until YYYY-MM-DD. Defaut None
		
	# 	:return: Dict[stats, {year, count}]
	# 	"""
	# 	extras = {
	# 		'size': 0, 'track_total_hits': True,
	# 		'aggs': {'search_interest': {
	# 			'date_histogram': {
	# 				'field': 'publication_date',
	# 				'calendar_interval': '1y',
	# 				'format': 'yyyy'
	# 			}
	# 		}}}
	# 	filters = [
	# 		Q('range', publication_date={
	# 			'gte': date_start,
	# 			'lte': date_end
	# 		})
	# 	]

	# 	query = Q('bool',
	# 	  should = [ Q(
	# 		  'match', **{ field: {
	# 			  'query': k,
	# 			  'operator': "and",
	# 			  'fuzziness': "AUTO:5,8",
	# 			  'auto_generate_synonyms_phrase_query': False
	# 		  }}) for k in keywords
	# 	  ],
	# 	  minimum_should_match = 1,
	# 	  filter = filters)
	# 	query = Search(index=index).extra(**extras).query(query).to_dict()
	# 	print(f"QUERY: {str(query)}")
	# #     resp = Search(index=index).extra(**extras).query(query)
	# #     return resp
	# 	resp = Search(index=index).extra(**extras).query(query).execute()

	# 	histogram = list(map(lambda x: {'year': x.key_as_string, 'count': x.doc_count},
	# 					 resp.aggregations.search_interest.buckets))

	# 	results = {
	# 		'histogram': histogram,
	# 		'stats': {**resp.hits.total.to_dict(), 'took': resp.took}
	# 	}
		
	# 	return results


	def get_histogram(self,
		keywords: List[str],
		field: str = 'content',
		index: str = 'publications',
		date_start: Optional[str] = None,
		date_end: Optional[str] = None,
		fuzziness: bool=False,
		**kwargs
	) -> Dict[str, Union[str, Dict[str, int]]]:
		"""
		Get histogram year articles from index using keywords query
		
		keywords: (list) of keywords
		field: (str) field name to quieried
		index: (str) ES index name
		date_start: (str) Filter article from YYYY-MM-DD. Default None
		date_end: (str) Filter article until YYYY-MM-DD. Defaut None
		
		:return: Dict[stats, {year, count}]
		"""
		extras = {
			'size': 0, 'track_total_hits': True,
			'aggs': {'search_interest': {
				'date_histogram': {
					'field': 'publication_date',
					'calendar_interval': '1y',
					'format': 'yyyy'
				}
			}}}
		filters = [
			Q('range', publication_date={
				'gte': date_start,
				'lte': date_end
			})
		]
		if len(keywords) > 0:
			if fuzziness:
				_should = [ Q(
				  'match', **{ field: {
					  'query': k,
					  'operator': "and",
					  'fuzziness': "AUTO:5,8",
					  'auto_generate_synonyms_phrase_query': False
				  }}) for k in keywords
			  	]
			else:
				_should = [ Q(
				  'match', **{ field: {
					  'query': k,
					  'operator': "and",
					  'auto_generate_synonyms_phrase_query': False
				  }}) for k in keywords
			  	]

			query = Q('bool',
			  should = _should,
			  minimum_should_match = 1,
			  filter = filters)
			resp = Search(index=index).extra(**extras).query(query).execute()
			# histogram = list(map(lambda x: {'year': x.key_as_string, 'count': x.doc_count},
			# 			 resp.aggregations.search_interest.buckets))

			# results = {
			# 	'histogram': histogram,
			# 	'stats': {**resp.hits.total.to_dict(), 'took': resp.took}
			# }
		else:
			query = filters[0]
			print('*****************')
			print(Search(index=index).extra(**extras).query(query).to_dict())
			resp = Search(index=index).extra(**extras).query(query).execute()

			# results = {
			# 	'stats': {**resp.hits.total.to_dict(), 'took': resp.took}
			# }

		# resp = Search(index=index).extra(**extras).query(query).execute()

		histogram = list(map(lambda x: {'year': x.key_as_string, 'count': x.doc_count},
						 resp.aggregations.search_interest.buckets))

		results = {
			'histogram': histogram,
			'stats': {**resp.hits.total.to_dict(), 'took': resp.took}
		}
		
		return results