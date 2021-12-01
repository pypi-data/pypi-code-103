# keep reading from here https://neo4j.com/docs/python-manual/current/cypher-workflow/
# docs https://neo4j.com/docs/api/python-driver/4.3/api.html#api-documentation
# this works with a local neo4j, but we can make a server later
from neo4j import ( GraphDatabase, TRUST_ALL_CERTIFICATES)
import logging
from neo4j.exceptions import ServiceUnavailable

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logging.getLogger("neo4j").addHandler(handler)

class GraphQuerier:

	def __init__(self):
		self.driver = GraphDatabase.driver(
			"bolt://localhost:7687", auth=("neo4j","password"))

	def _close(self):
		# Don't forget to close the driver connection when you are finished with it
		self.driver.close()

	def query(self, query = None):
		# Cypher syntax https://neo4j.com/docs/cypher-manual/current/
		# The Reference https://neo4j.com/docs/cypher-refcard/current/

		result = self.driver.session().run(query)
		try:
			return result
		# Capture any errors along with the query and data for traceability
		except ServiceUnavailable as exception:
			logging.error("{query} raised an error: \n {exception}".format(
				query=query, exception=exception))
			raise